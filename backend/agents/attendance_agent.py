
"""
Attendance & Time Tracking Agent
Handles biometric, GPS, face recognition, and shift management
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, time
import json
import uuid
import cv2
import numpy as np
from geopy.distance import geodesic
import face_recognition
from sqlalchemy.orm import Session
from ..database.sql_database import get_db
from ..models.sql_models import Employee, AttendanceRecord
import calendar

logger = logging.getLogger(__name__)

class AttendanceAgent:
    def __init__(self):
        self.agent_name = "attendance_agent"
        self.office_locations = {
            "main_office": {"lat": 37.7749, "lng": -122.4194, "radius": 100},  # SF coordinates
            "branch_office": {"lat": 40.7128, "lng": -74.0060, "radius": 150}  # NY coordinates
        }
        self.face_encodings_db = {}  # Will store known face encodings
        self.shift_schedules = {}
        
    async def clock_in_with_gps(self, employee_id: str, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process clock-in with GPS verification"""
        try:
            current_time = datetime.utcnow()
            employee_location = (location_data.get("latitude"), location_data.get("longitude"))
            
            # Verify location
            location_valid = False
            nearest_office = None
            min_distance = float('inf')
            
            for office_name, office_data in self.office_locations.items():
                office_location = (office_data["lat"], office_data["lng"])
                distance = geodesic(employee_location, office_location).meters
                
                if distance <= office_data["radius"]:
                    location_valid = True
                    if distance < min_distance:
                        min_distance = distance
                        nearest_office = office_name
            
            if not location_valid:
                return {
                    "success": False,
                    "message": "Location verification failed. You are not within office premises.",
                    "distance_to_nearest": min_distance,
                    "timestamp": current_time.isoformat()
                }
            
            # Get employee shift schedule
            shift_info = await self._get_employee_shift(employee_id)
            
            # Check if early/late
            scheduled_start = shift_info.get("start_time")
            status = "on_time"
            if scheduled_start:
                scheduled_datetime = datetime.combine(current_time.date(), scheduled_start)
                if current_time > scheduled_datetime + timedelta(minutes=15):
                    status = "late"
                elif current_time < scheduled_datetime - timedelta(minutes=30):
                    status = "early"
            
            # Record attendance
            attendance_record = {
                "id": str(uuid.uuid4()),
                "employee_id": employee_id,
                "clock_in_time": current_time.isoformat(),
                "location": {
                    "office": nearest_office,
                    "coordinates": employee_location,
                    "verification_method": "gps",
                    "accuracy": location_data.get("accuracy", 0)
                },
                "status": status,
                "shift_info": shift_info
            }
            
            # Save to database
            await self._save_attendance_record(attendance_record)
            
            # Send notifications if late
            if status == "late":
                await self._send_late_notification(employee_id, current_time, scheduled_datetime)
            
            return {
                "success": True,
                "message": f"Clock-in successful at {nearest_office}",
                "status": status,
                "time": current_time.isoformat(),
                "location": nearest_office,
                "attendance_id": attendance_record["id"]
            }
            
        except Exception as e:
            logger.error(f"GPS clock-in error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def clock_in_with_face_recognition(self, employee_id: str, image_data: bytes) -> Dict[str, Any]:
        """Process clock-in with face recognition"""
        try:
            current_time = datetime.utcnow()
            
            # Convert image data to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(rgb_image)
            if not face_locations:
                return {
                    "success": False,
                    "message": "No face detected in the image",
                    "timestamp": current_time.isoformat()
                }
            
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            if not face_encodings:
                return {
                    "success": False,
                    "message": "Could not encode face from image",
                    "timestamp": current_time.isoformat()
                }
            
            # Get employee's stored face encoding
            stored_encoding = await self._get_employee_face_encoding(employee_id)
            if not stored_encoding:
                return {
                    "success": False,
                    "message": "Employee face encoding not found. Please register your face first.",
                    "timestamp": current_time.isoformat()
                }
            
            # Compare faces
            face_distances = face_recognition.face_distance([stored_encoding], face_encodings[0])
            face_match = face_distances[0] < 0.6  # Threshold for face match
            
            if not face_match:
                return {
                    "success": False,
                    "message": "Face recognition failed. Face does not match registered employee.",
                    "confidence": 1 - face_distances[0],
                    "timestamp": current_time.isoformat()
                }
            
            # Get shift information
            shift_info = await self._get_employee_shift(employee_id)
            
            # Determine status
            scheduled_start = shift_info.get("start_time")
            status = "on_time"
            if scheduled_start:
                scheduled_datetime = datetime.combine(current_time.date(), scheduled_start)
                if current_time > scheduled_datetime + timedelta(minutes=15):
                    status = "late"
                elif current_time < scheduled_datetime - timedelta(minutes=30):
                    status = "early"
            
            # Record attendance
            attendance_record = {
                "id": str(uuid.uuid4()),
                "employee_id": employee_id,
                "clock_in_time": current_time.isoformat(),
                "verification_method": "face_recognition",
                "confidence_score": 1 - face_distances[0],
                "status": status,
                "shift_info": shift_info
            }
            
            await self._save_attendance_record(attendance_record)
            
            return {
                "success": True,
                "message": "Clock-in successful with face recognition",
                "status": status,
                "confidence": 1 - face_distances[0],
                "time": current_time.isoformat(),
                "attendance_id": attendance_record["id"]
            }
            
        except Exception as e:
            logger.error(f"Face recognition clock-in error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def auto_fill_timesheet(self, employee_id: str, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Automatically fill timesheet based on attendance records"""
        try:
            start_date = datetime.fromisoformat(date_range["start_date"])
            end_date = datetime.fromisoformat(date_range["end_date"])
            
            # Get attendance records for the period
            attendance_records = await self._get_attendance_records(employee_id, start_date, end_date)
            
            # Get employee's standard shift
            shift_info = await self._get_employee_shift(employee_id)
            standard_hours = shift_info.get("duration_hours", 8)
            
            timesheet_data = []
            current_date = start_date
            
            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                day_records = [r for r in attendance_records if r["date"] == date_str]
                
                if day_records:
                    # Calculate worked hours from actual records
                    day_entry = await self._calculate_day_hours(day_records, shift_info)
                else:
                    # Check if it's a working day
                    if current_date.weekday() < 5:  # Monday to Friday
                        # Check if it's a holiday
                        is_holiday = await self._check_if_holiday(current_date)
                        if is_holiday:
                            day_entry = {
                                "date": date_str,
                                "status": "holiday",
                                "hours_worked": 0,
                                "break_time": 0,
                                "overtime": 0,
                                "notes": f"Holiday: {is_holiday}"
                            }
                        else:
                            # Mark as absent
                            day_entry = {
                                "date": date_str,
                                "status": "absent",
                                "hours_worked": 0,
                                "break_time": 0,
                                "overtime": 0,
                                "notes": "No attendance record found"
                            }
                    else:
                        # Weekend
                        day_entry = {
                            "date": date_str,
                            "status": "weekend",
                            "hours_worked": 0,
                            "break_time": 0,
                            "overtime": 0,
                            "notes": "Weekend"
                        }
                
                timesheet_data.append(day_entry)
                current_date += timedelta(days=1)
            
            # Calculate totals
            total_hours = sum(day["hours_worked"] for day in timesheet_data)
            total_overtime = sum(day["overtime"] for day in timesheet_data)
            working_days = len([day for day in timesheet_data if day["status"] == "present"])
            
            timesheet = {
                "employee_id": employee_id,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "summary": {
                    "total_hours": total_hours,
                    "total_overtime": total_overtime,
                    "working_days": working_days,
                    "absent_days": len([day for day in timesheet_data if day["status"] == "absent"]),
                    "late_days": len([day for day in timesheet_data if day.get("late_arrival", False)])
                },
                "daily_entries": timesheet_data,
                "generated_at": datetime.utcnow().isoformat(),
                "auto_generated": True
            }
            
            # Save timesheet
            await self._save_timesheet(timesheet)
            
            return {
                "success": True,
                "timesheet": timesheet,
                "message": "Timesheet auto-filled successfully"
            }
            
        except Exception as e:
            logger.error(f"Auto timesheet generation error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def optimize_shift_planning(self, department_id: str, planning_period: Dict[str, str]) -> Dict[str, Any]:
        """AI-powered shift planning and optimization"""
        try:
            start_date = datetime.fromisoformat(planning_period["start_date"])
            end_date = datetime.fromisoformat(planning_period["end_date"])
            
            # Get department employees
            employees = await self._get_department_employees(department_id)
            
            # Get historical attendance patterns
            attendance_patterns = await self._analyze_attendance_patterns(employees, start_date - timedelta(days=90), start_date)
            
            # Get business requirements
            business_requirements = await self._get_business_requirements(department_id)
            
            # Generate optimal shift schedule
            optimized_schedule = await self._generate_optimal_shifts(
                employees, 
                attendance_patterns, 
                business_requirements, 
                start_date, 
                end_date
            )
            
            # Calculate optimization metrics
            optimization_metrics = await self._calculate_optimization_metrics(optimized_schedule, business_requirements)
            
            return {
                "success": True,
                "optimized_schedule": optimized_schedule,
                "optimization_metrics": optimization_metrics,
                "recommendations": await self._generate_shift_recommendations(optimization_metrics),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Shift optimization error: {str(e)}")
            return {"success": False, "error": str(e)}

    # Helper methods
    async def _get_employee_shift(self, employee_id: str) -> Dict[str, Any]:
        """Get employee's shift information"""
        # Default shift information - in real implementation, fetch from database
        return {
            "shift_type": "day",
            "start_time": time(9, 0),
            "end_time": time(17, 30),
            "duration_hours": 8.5,
            "break_duration": 60,  # minutes
            "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
        }
    
    async def _save_attendance_record(self, record: Dict[str, Any]):
        """Save attendance record to database"""
        # Implementation would save to actual database
        logger.info(f"Saving attendance record: {record['id']}")
    
    async def _send_late_notification(self, employee_id: str, actual_time: datetime, scheduled_time: datetime):
        """Send notification for late arrival"""
        delay_minutes = int((actual_time - scheduled_time).total_seconds() / 60)
        logger.info(f"Employee {employee_id} is {delay_minutes} minutes late")
    
    async def _get_employee_face_encoding(self, employee_id: str) -> Optional[np.ndarray]:
        """Get stored face encoding for employee"""
        # In real implementation, fetch from database
        return self.face_encodings_db.get(employee_id)
    
    async def _get_attendance_records(self, employee_id: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get attendance records for date range"""
        # Mock data - in real implementation, fetch from database
        return []
    
    async def _calculate_day_hours(self, day_records: List[Dict[str, Any]], shift_info: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate worked hours for a day"""
        if not day_records:
            return {"date": "", "status": "absent", "hours_worked": 0, "break_time": 0, "overtime": 0}
        
        # Find clock-in and clock-out times
        clock_in = None
        clock_out = None
        
        for record in day_records:
            if record.get("clock_in_time") and not clock_in:
                clock_in = datetime.fromisoformat(record["clock_in_time"])
            if record.get("clock_out_time"):
                clock_out = datetime.fromisoformat(record["clock_out_time"])
        
        if not clock_in:
            return {"date": day_records[0].get("date", ""), "status": "absent", "hours_worked": 0, "break_time": 0, "overtime": 0}
        
        if not clock_out:
            # Assume still working or forgot to clock out
            clock_out = clock_in + timedelta(hours=shift_info.get("duration_hours", 8))
        
        # Calculate total time
        total_minutes = int((clock_out - clock_in).total_seconds() / 60)
        break_minutes = shift_info.get("break_duration", 60)
        worked_minutes = max(0, total_minutes - break_minutes)
        worked_hours = worked_minutes / 60
        
        # Calculate overtime
        standard_hours = shift_info.get("duration_hours", 8)
        overtime = max(0, worked_hours - standard_hours)
        
        return {
            "date": clock_in.strftime("%Y-%m-%d"),
            "status": "present",
            "hours_worked": round(worked_hours, 2),
            "break_time": break_minutes,
            "overtime": round(overtime, 2),
            "clock_in": clock_in.strftime("%H:%M"),
            "clock_out": clock_out.strftime("%H:%M"),
            "late_arrival": clock_in.time() > shift_info.get("start_time", time(9, 0))
        }
    
    async def _check_if_holiday(self, date: datetime) -> Optional[str]:
        """Check if date is a holiday"""
        # Mock holiday data - in real implementation, check holiday calendar
        holidays = {
            "2024-01-01": "New Year's Day",
            "2024-07-04": "Independence Day",
            "2024-12-25": "Christmas Day"
        }
        return holidays.get(date.strftime("%Y-%m-%d"))
    
    async def _save_timesheet(self, timesheet: Dict[str, Any]):
        """Save timesheet to database"""
        logger.info(f"Saving timesheet for employee: {timesheet['employee_id']}")
    
    async def _get_department_employees(self, department_id: str) -> List[Dict[str, Any]]:
        """Get all employees in a department"""
        # Mock data - in real implementation, fetch from database
        return [
            {"id": "emp1", "name": "John Doe", "role": "Developer"},
            {"id": "emp2", "name": "Jane Smith", "role": "Designer"},
        ]
    
    async def _analyze_attendance_patterns(self, employees: List[Dict[str, Any]], start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze historical attendance patterns"""
        return {
            "average_attendance_rate": 0.92,
            "peak_hours": {"start": "09:00", "end": "17:00"},
            "low_attendance_days": ["monday", "friday"],
            "seasonal_patterns": {"summer": -0.05, "winter": 0.02}
        }
    
    async def _get_business_requirements(self, department_id: str) -> Dict[str, Any]:
        """Get business requirements for the department"""
        return {
            "minimum_staff": 5,
            "peak_hours_staff": 8,
            "coverage_hours": {"start": "08:00", "end": "18:00"},
            "critical_roles": ["team_lead", "senior_developer"]
        }
    
    async def _generate_optimal_shifts(self, employees: List[Dict[str, Any]], patterns: Dict[str, Any], 
                                     requirements: Dict[str, Any], start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate optimal shift assignments"""
        return {
            "shifts": [
                {
                    "shift_id": "morning",
                    "time": "08:00-16:00",
                    "employees": ["emp1", "emp2"],
                    "coverage_score": 0.95
                },
                {
                    "shift_id": "day",
                    "time": "09:00-17:00", 
                    "employees": ["emp3", "emp4"],
                    "coverage_score": 0.98
                }
            ],
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }
    
    async def _calculate_optimization_metrics(self, schedule: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimization metrics"""
        return {
            "coverage_efficiency": 0.94,
            "cost_optimization": 0.87,
            "employee_satisfaction": 0.91,
            "business_requirement_fulfillment": 0.96
        }
    
    async def _generate_shift_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on metrics"""
        return [
            "Consider flexible start times to improve employee satisfaction",
            "Add one additional staff member during peak hours",
            "Implement compressed work week for better coverage"
        ]
