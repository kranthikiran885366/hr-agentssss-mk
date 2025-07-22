"""
Leave Agent - Automated leave and attendance management
Handles all leave requests, approvals, and attendance tracking without human intervention
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import uuid
import calendar
from dataclasses import dataclass

from ..base_agent import BaseAgent
from backend.database.mongo_database import get_mongo_client
from backend.database.sql_database import SessionLocal
from models.sql_models import Employee, LeaveRequest, AttendanceRecord
from backend.utils.config import settings

logger = logging.getLogger(__name__)

@dataclass
class LeavePolicy:
    leave_type: str
    annual_quota: int
    max_consecutive_days: int
    min_notice_days: int
    requires_approval: bool
    auto_approve_threshold: int

class LeaveAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "leave_agent"
        
        # Leave policies
        self.leave_policies = {
            "annual": LeavePolicy("annual", 25, 15, 7, True, 3),
            "sick": LeavePolicy("sick", 12, 5, 0, False, 2),
            "personal": LeavePolicy("personal", 5, 3, 3, True, 1),
            "maternity": LeavePolicy("maternity", 180, 180, 30, False, 0),
            "paternity": LeavePolicy("paternity", 15, 15, 15, False, 0),
            "emergency": LeavePolicy("emergency", 3, 2, 0, False, 1),
            "bereavement": LeavePolicy("bereavement", 5, 5, 0, False, 0),
            "study": LeavePolicy("study", 10, 5, 14, True, 0)
        }
        
        # Attendance tracking
        self.attendance_rules = {
            "core_hours": {"start": "09:00", "end": "17:00"},
            "flexible_window": 2,  # hours
            "minimum_hours_per_day": 8,
            "overtime_threshold": 9,
            "late_threshold_minutes": 15,
            "early_leave_threshold_minutes": 30
        }

    async def initialize(self):
        """Initialize leave agent"""
        try:
            logger.info("Initializing Leave Agent...")
            await super().initialize()
            
            # Start automated processes
            asyncio.create_task(self._automated_leave_processing())
            asyncio.create_task(self._automated_attendance_monitoring())
            asyncio.create_task(self._automated_policy_enforcement())
            
            self.is_initialized = True
            logger.info("Leave Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Leave Agent: {str(e)}")
            raise

    async def submit_leave_request(self, employee_id: str, leave_type: str, 
                                 start_date: str, end_date: str, reason: str = "") -> Dict[str, Any]:
        """Submit and automatically process leave request"""
        try:
            request_id = str(uuid.uuid4())
            
            # Validate leave request
            validation_result = await self._validate_leave_request(
                employee_id, leave_type, start_date, end_date
            )
            
            if not validation_result["valid"]:
                return {
                    "request_id": request_id,
                    "status": "rejected",
                    "reason": validation_result["reason"],
                    "processed_at": datetime.utcnow().isoformat()
                }
            
            # Calculate leave days
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            leave_days = await self._calculate_leave_days(start_dt, end_dt)
            
            # Create leave request
            leave_request = {
                "id": request_id,
                "employee_id": employee_id,
                "leave_type": leave_type,
                "start_date": start_date,
                "end_date": end_date,
                "leave_days": leave_days,
                "reason": reason,
                "status": "pending",
                "submitted_at": datetime.utcnow().isoformat(),
                "auto_processed": True
            }
            
            # Auto-approve or reject based on AI logic
            approval_result = await self._auto_approve_leave(leave_request)
            leave_request.update(approval_result)
            
            # Store leave request
            await self._store_leave_request(leave_request)
            
            # Send notifications
            await self._send_leave_notifications(leave_request)
            
            # Update calendar and systems
            if leave_request["status"] == "approved":
                await self._update_systems_for_approved_leave(leave_request)
            
            return leave_request
            
        except Exception as e:
            logger.error(f"Leave request submission error: {str(e)}")
            raise

    async def _validate_leave_request(self, employee_id: str, leave_type: str, 
                                    start_date: str, end_date: str) -> Dict[str, Any]:
        """Validate leave request against policies"""
        try:
            if leave_type not in self.leave_policies:
                return {"valid": False, "reason": "Invalid leave type"}
            
            policy = self.leave_policies[leave_type]
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            # Check date validity
            if start_dt > end_dt:
                return {"valid": False, "reason": "Start date cannot be after end date"}
            
            if start_dt < datetime.utcnow():
                return {"valid": False, "reason": "Cannot request leave for past dates"}
            
            # Check notice period
            notice_days = (start_dt - datetime.utcnow()).days
            if notice_days < policy.min_notice_days:
                return {"valid": False, "reason": f"Minimum {policy.min_notice_days} days notice required"}
            
            # Check consecutive days limit
            leave_days = await self._calculate_leave_days(start_dt, end_dt)
            if leave_days > policy.max_consecutive_days:
                return {"valid": False, "reason": f"Maximum {policy.max_consecutive_days} consecutive days allowed"}
            
            # Check annual quota
            used_leaves = await self._get_used_leaves(employee_id, leave_type)
            if used_leaves + leave_days > policy.annual_quota:
                return {"valid": False, "reason": f"Exceeds annual quota of {policy.annual_quota} days"}
            
            # Check for overlapping requests
            overlapping = await self._check_overlapping_requests(employee_id, start_date, end_date)
            if overlapping:
                return {"valid": False, "reason": "Overlapping leave request exists"}
            
            return {"valid": True, "reason": "Valid request"}
            
        except Exception as e:
            logger.error(f"Leave validation error: {str(e)}")
            return {"valid": False, "reason": "Validation failed"}

    async def _auto_approve_leave(self, leave_request: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically approve or reject leave using AI logic"""
        try:
            employee_id = leave_request["employee_id"]
            
            # Get employee data
            employee_data = await self._get_employee_data(employee_id)
            
            # Factors for AI decision
            factors = {
                "performance_score": employee_data.get("performance_score", 75),
                "attendance_score": employee_data.get("attendance_score", 85),
                "leave_history": employee_data.get("leave_frequency", 0.5),
                "project_criticality": employee_data.get("project_criticality", "medium"),
                "team_size": employee_data.get("team_size", 5),
                "backup_available": employee_data.get("backup_available", True)
            }
            
            # AI scoring algorithm
            approval_score = 0
            
            # Performance factor (30%)
            if factors["performance_score"] >= 80:
                approval_score += 30
            elif factors["performance_score"] >= 70:
                approval_score += 20
            else:
                approval_score += 10
            
            # Attendance factor (25%)
            if factors["attendance_score"] >= 90:
                approval_score += 25
            elif factors["attendance_score"] >= 80:
                approval_score += 20
            else:
                approval_score += 10
            
            # Leave history factor (20%)
            if factors["leave_history"] <= 0.3:  # Low leave frequency
                approval_score += 20
            elif factors["leave_history"] <= 0.6:
                approval_score += 15
            else:
                approval_score += 5
            
            # Project criticality factor (15%)
            if factors["project_criticality"] == "low":
                approval_score += 15
            elif factors["project_criticality"] == "medium":
                approval_score += 10
            else:
                approval_score += 5
            
            # Backup availability factor (10%)
            if factors["backup_available"]:
                approval_score += 10
            
            # Decision threshold
            approve = approval_score >= 70
            
            reason = f"AI Decision Score: {approval_score}/100. "
            if approve:
                reason += "Employee meets approval criteria."
            else:
                reason += "Employee does not meet minimum approval criteria."
            
            return {
                "status": "approved" if approve else "rejected",
                "approval_reason": reason,
                "processed_at": datetime.utcnow().isoformat(),
                "auto_approved": approve,
                "team_impact_assessment": await self._assess_team_impact(leave_request)
            }
            
        except Exception as e:
            logger.error(f"AI leave decision error: {str(e)}")
            return {"status": "pending", "approval_reason": "AI decision failed", "processed_at": datetime.utcnow().isoformat()}

    async def track_attendance(self, employee_id: str, check_in_time: str = None, 
                             check_out_time: str = None, location: Dict[str, Any] = None) -> Dict[str, Any]:
        """Track employee attendance automatically"""
        try:
            today = datetime.utcnow().date()
            
            # Get or create attendance record
            attendance_record = await self._get_or_create_attendance_record(employee_id, today)
            
            if check_in_time:
                attendance_record["check_in_time"] = check_in_time
                attendance_record["check_in_location"] = location
                
                # Analyze check-in
                check_in_analysis = await self._analyze_check_in(check_in_time)
                attendance_record["check_in_analysis"] = check_in_analysis
            
            if check_out_time:
                attendance_record["check_out_time"] = check_out_time
                
                # Calculate work hours
                work_hours = await self._calculate_work_hours(
                    attendance_record.get("check_in_time"),
                    check_out_time
                )
                attendance_record["work_hours"] = work_hours
                
                # Analyze full day
                day_analysis = await self._analyze_work_day(attendance_record)
                attendance_record["day_analysis"] = day_analysis
            
            # Update attendance record
            await self._update_attendance_record(attendance_record)
            
            # Check for attendance violations
            violations = await self._check_attendance_violations(attendance_record)
            if violations:
                await self._handle_attendance_violations(employee_id, violations)
            
            return attendance_record
            
        except Exception as e:
            logger.error(f"Attendance tracking error: {str(e)}")
            raise

    async def _automated_leave_processing(self):
        """Automated background leave processing"""
        while True:
            try:
                # Process pending leave requests
                await self._process_pending_leaves()
                
                # Update leave balances
                await self._update_leave_balances()
                
                # Send leave reminders
                await self._send_leave_reminders()
                
                # Process leave expiry
                await self._process_leave_expiry()
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Automated leave processing error: {str(e)}")
                await asyncio.sleep(300)

    async def _automated_attendance_monitoring(self):
        """Automated attendance monitoring and alerts"""
        while True:
            try:
                # Monitor late arrivals
                await self._monitor_late_arrivals()
                
                # Monitor early departures
                await self._monitor_early_departures()
                
                # Monitor overtime
                await self._monitor_overtime()
                
                # Generate attendance reports
                await self._generate_attendance_reports()
                
                # Sleep for 30 minutes
                await asyncio.sleep(1800)
                
            except Exception as e:
                logger.error(f"Automated attendance monitoring error: {str(e)}")
                await asyncio.sleep(300)

    async def _process_pending_leaves(self):
        """Process pending leave requests"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            pending_leaves = await mongo_db.leave_requests.find({"status": "pending"}).to_list(None)
            
            for leave_request in pending_leaves:
                # Auto-approve or reject
                approval_result = await self._auto_approve_leave(leave_request)
                leave_request.update(approval_result)
                
                # Update leave request
                await self._update_leave_request(leave_request)
                
                # Send notifications
                await self._send_leave_notifications(leave_request)
                
                # Update calendar and systems
                if leave_request["status"] == "approved":
                    await self._update_systems_for_approved_leave(leave_request)
                    
        except Exception as e:
            logger.error(f"Pending leaves processing error: {str(e)}")

    async def _update_leave_balances(self):
        """Update leave balances for all employees"""
        try:
            db = SessionLocal()
            employees = db.query(Employee).all()
            db.close()
            
            for employee in employees:
                for leave_type in self.leave_policies:
                    # Calculate and update leave balance
                    await self._calculate_and_update_leave_balance(employee.id, leave_type)
                    
        except Exception as e:
            logger.error(f"Leave balances update error: {str(e)}")

    async def _send_leave_reminders(self):
        """Send reminders for upcoming leaves"""
        try:
            # Get upcoming leaves
            upcoming_leaves = await self._get_upcoming_leaves()
            
            # Send reminders
            for leave in upcoming_leaves:
                await self._send_leave_reminder(leave)
                
        except Exception as e:
            logger.error(f"Leave reminders sending error: {str(e)}")

    async def _process_leave_expiry(self):
        """Process expired leave balances"""
        try:
            # Get expired leave balances
            expired_balances = await self._get_expired_leave_balances()
            
            # Adjust balances
            for balance in expired_balances:
                await self._adjust_expired_leave_balance(balance)
                
        except Exception as e:
            logger.error(f"Leave expiry processing error: {str(e)}")

    async def _monitor_late_arrivals(self):
        """Monitor late arrivals and send alerts"""
        try:
            # Get today's attendance records
            today = datetime.utcnow().date()
            attendance_records = await self._get_attendance_records_for_date(today)
            
            for record in attendance_records:
                # Check for late arrival
                if record.get("check_in_time"):
                    check_in_time = datetime.fromisoformat(record["check_in_time"]).time()
                    core_start = datetime.strptime(self.attendance_rules["core_hours"]["start"], "%H:%M").time()
                    
                    if check_in_time > core_start:
                        # Send late arrival alert
                        await self._send_late_arrival_alert(record, check_in_time, core_start)
                        
        except Exception as e:
            logger.error(f"Late arrivals monitoring error: {str(e)}")

    async def _monitor_early_departures(self):
        """Monitor early departures and send alerts"""
        try:
            # Get today's attendance records
            today = datetime.utcnow().date()
            attendance_records = await self._get_attendance_records_for_date(today)
            
            for record in attendance_records:
                # Check for early departure
                if record.get("check_out_time"):
                    check_out_time = datetime.fromisoformat(record["check_out_time"]).time()
                    core_end = datetime.strptime(self.attendance_rules["core_hours"]["end"], "%H:%M").time()
                    
                    if check_out_time < core_end:
                        # Send early departure alert
                        await self._send_early_departure_alert(record, check_out_time, core_end)
                        
        except Exception as e:
            logger.error(f"Early departures monitoring error: {str(e)}")

    async def _monitor_overtime(self):
        """Monitor overtime and send alerts"""
        try:
            # Get today's attendance records
            today = datetime.utcnow().date()
            attendance_records = await self._get_attendance_records_for_date(today)
            
            for record in attendance_records:
                # Check for overtime
                if record.get("work_hours", 0) > self.attendance_rules["overtime_threshold"]:
                    # Send overtime alert
                    await self._send_overtime_alert(record)
                    
        except Exception as e:
            logger.error(f"Overtime monitoring error: {str(e)}")

    async def _generate_attendance_reports(self):
        """Generate attendance reports"""
        try:
            # Placeholder for generating attendance reports logic
            logger.info("Generating automated attendance reports")
            
        except Exception as e:
            logger.error(f"Attendance reports generation error: {str(e)}")

    async def _get_employee_data(self, employee_id: str) -> Dict[str, Any]:
        """Get employee data"""
        try:
            db = SessionLocal()
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            db.close()
            
            if employee:
                return {
                    "id": employee.id,
                    "name": employee.name,
                    "email": employee.email,
                    "phone": employee.phone,
                    "position": employee.position,
                    "department": employee.department,
                    "manager_id": employee.manager_id
                }
            return {}
        except Exception as e:
            logger.error(f"Employee data retrieval error: {str(e)}")
            return {}

    async def _calculate_leave_days(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate working days between dates"""
        try:
            total_days = 0
            current_date = start_date
            
            while current_date <= end_date:
                # Skip weekends (assuming Monday=0, Sunday=6)
                if current_date.weekday() < 5:  # Monday to Friday
                    total_days += 1
                current_date += timedelta(days=1)
            
            return total_days
            
        except Exception as e:
            logger.error(f"Leave days calculation error: {str(e)}")
            return 0

    async def _get_used_leaves(self, employee_id: str, leave_type: str) -> int:
        """Get used leaves for current year"""
        try:
            current_year = datetime.utcnow().year
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            
            pipeline = [
                {
                    "$match": {
                        "employee_id": employee_id,
                        "leave_type": leave_type,
                        "status": "approved",
                        "start_date": {
                            "$gte": f"{current_year}-01-01",
                            "$lt": f"{current_year + 1}-01-01"
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_days": {"$sum": "$leave_days"}
                    }
                }
            ]
            
            result = await mongo_db.leave_requests.aggregate(pipeline).to_list(None)
            return result[0]["total_days"] if result else 0
            
        except Exception as e:
            logger.error(f"Get used leaves error: {str(e)}")
            return 0

    async def _update_leave_request(self, leave_request: Dict[str, Any]):
        """Update leave request in databases"""
        try:
            # Update SQL
            db = SessionLocal()
            leave_record = db.query(LeaveRequest).filter(LeaveRequest.id == leave_request["id"]).first()
            if leave_record:
                leave_record.status = leave_request["status"]
                db.commit()
            db.close()
            
            # Update MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.leave_requests.replace_one(
                {"id": leave_request["id"]},
                leave_request
            )
            
        except Exception as e:
            logger.error(f"Leave request update error: {str(e)}")

    async def _send_leave_notifications(self, leave_request: Dict[str, Any]):
        """Send automated leave notifications"""
        try:
            from ..communication_agent.core import CommunicationAgent
            comm_agent = CommunicationAgent()
            
            # Notify employee
            await comm_agent.send_communication(
                recipient_id=leave_request["employee_id"],
                communication_type="leave_status_update",
                channel="email",
                template_data=leave_request
            )
            
            # Notify manager if approved
            if leave_request["status"] == "approved":
                employee_data = await self._get_employee_data(leave_request["employee_id"])
                if employee_data.get("manager_id"):
                    await comm_agent.send_communication(
                        recipient_id=employee_data["manager_id"],
                        communication_type="team_leave_notification",
                        channel="email",
                        template_data=leave_request
                    )
            
        except Exception as e:
            logger.error(f"Leave notification error: {str(e)}")

    async def _update_systems_for_approved_leave(self, leave_request: Dict[str, Any]):
        """Update calendar and other systems for approved leave"""
        try:
            # Placeholder for updating systems logic
            logger.info(f"Updating systems for approved leave: {leave_request['id']}")
            
        except Exception as e:
            logger.error(f"Systems update error: {str(e)}")

    async def _get_or_create_attendance_record(self, employee_id: str, date: datetime) -> Dict[str, Any]:
        """Get or create attendance record for employee and date"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            
            attendance_record = await mongo_db.attendance_records.find_one({"employee_id": employee_id, "date": date.isoformat()})
            
            if not attendance_record:
                attendance_record = {
                    "id": str(uuid.uuid4()),
                    "employee_id": employee_id,
                    "date": date.isoformat(),
                    "check_in_time": None,
                    "check_out_time": None,
                    "work_hours": 0,
                    "status": "absent",
                    "created_at": datetime.utcnow().isoformat()
                }
                await mongo_db.attendance_records.insert_one(attendance_record)
            
            return attendance_record
            
        except Exception as e:
            logger.error(f"Attendance record retrieval/creation error: {str(e)}")
            return {}

    async def _analyze_check_in(self, check_in_time: str) -> Dict[str, Any]:
        """Analyze check-in time"""
        try:
            check_in_dt = datetime.fromisoformat(check_in_time)
            core_start = datetime.strptime(self.attendance_rules["core_hours"]["start"], "%H:%M").time()
            
            # Calculate lateness
            lateness_minutes = (check_in_dt.time().hour - core_start.hour) * 60 + (check_in_dt.time().minute - core_start.minute)
            
            return {
                "check_in_time": check_in_time,
                "lateness_minutes": lateness_minutes,
                "is_late": lateness_minutes > self.attendance_rules["late_threshold_minutes"]
            }
            
        except Exception as e:
            logger.error(f"Check-in analysis error: {str(e)}")
            return {}

    async def _calculate_work_hours(self, check_in_time: str, check_out_time: str) -> float:
        """Calculate work hours"""
        try:
            check_in_dt = datetime.fromisoformat(check_in_time)
            check_out_dt = datetime.fromisoformat(check_out_time)
            
            work_duration = check_out_dt - check_in_dt
            work_hours = work_duration.total_seconds() / 3600
            
            return work_hours
            
        except Exception as e:
            logger.error(f"Work hours calculation error: {str(e)}")
            return 0.0

    async def _analyze_work_day(self, attendance_record: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze work day"""
        try:
            work_hours = attendance_record.get("work_hours", 0)
            
            # Check if minimum hours met
            minimum_hours_met = work_hours >= self.attendance_rules["minimum_hours_per_day"]
            
            # Check for overtime
            overtime_hours = max(0, work_hours - self.attendance_rules["overtime_threshold"])
            
            return {
                "work_hours": work_hours,
                "minimum_hours_met": minimum_hours_met,
                "overtime_hours": overtime_hours
            }
            
        except Exception as e:
            logger.error(f"Work day analysis error: {str(e)}")
            return {}

    async def _update_attendance_record(self, attendance_record: Dict[str, Any]):
        """Update attendance record in database"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.attendance_records.replace_one(
                {"id": attendance_record["id"]},
                attendance_record
            )
            
        except Exception as e:
            logger.error(f"Attendance record update error: {str(e)}")

    async def _check_attendance_violations(self, attendance_record: Dict[str, Any]) -> List[str]:
        """Check for attendance violations"""
        try:
            violations = []
            
            # Check for late arrival
            if attendance_record.get("check_in_analysis", {}).get("is_late"):
                violations.append("late_arrival")
            
            # Check for early departure
            if attendance_record.get("day_analysis", {}).get("work_hours", 0) < self.attendance_rules["minimum_hours_per_day"]:
                violations.append("early_departure")
            
            return violations
            
        except Exception as e:
            logger.error(f"Attendance violations check error: {str(e)}")
            return []

    async def _handle_attendance_violations(self, employee_id: str, violations: List[str]):
        """Handle attendance violations"""
        try:
            # Placeholder for handling attendance violations logic
            logger.info(f"Handling attendance violations for employee: {employee_id}, Violations: {violations}")
            
        except Exception as e:
            logger.error(f"Attendance violations handling error: {str(e)}")

    async def _get_attendance_records_for_date(self, date: datetime) -> List[Dict[str, Any]]:
        """Get attendance records for a specific date"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            attendance_records = await mongo_db.attendance_records.find({"date": date.isoformat()}).to_list(None)
            return attendance_records
            
        except Exception as e:
            logger.error(f"Attendance records retrieval error: {str(e)}")
            return []

    async def _send_late_arrival_alert(self, record: Dict[str, Any], check_in_time: datetime.time, core_start: datetime.time):
        """Send late arrival alert"""
        try:
            from ..communication_agent.core import CommunicationAgent
            comm_agent = CommunicationAgent()
            
            # Send alert to employee
            await comm_agent.send_communication(
                recipient_id=record["employee_id"],
                communication_type="late_arrival_alert",
                channel="email",
                template_data={
                    "check_in_time": check_in_time.strftime("%H:%M"),
                    "core_start": core_start.strftime("%H:%M")
                }
            )
            
            # Send alert to manager
            employee_data = await self._get_employee_data(record["employee_id"])
            if employee_data.get("manager_id"):
                await comm_agent.send_communication(
                    recipient_id=employee_data["manager_id"],
                    communication_type="team_late_arrival_alert",
                    channel="email",
                    template_data={
                        "employee_name": employee_data["name"],
                        "check_in_time": check_in_time.strftime("%H:%M"),
                        "core_start": core_start.strftime("%H:%M")
                    }
                )
            
        except Exception as e:
            logger.error(f"Late arrival alert sending error: {str(e)}")

    async def _send_early_departure_alert(self, record: Dict[str, Any], check_out_time: datetime.time, core_end: datetime.time):
        """Send early departure alert"""
        try:
            from ..communication_agent.core import CommunicationAgent
            comm_agent = CommunicationAgent()
            
            # Send alert to employee
            await comm_agent.send_communication(
                recipient_id=record["employee_id"],
                communication_type="early_departure_alert",
                channel="email",
                template_data={
                    "check_out_time": check_out_time.strftime("%H:%M"),
                    "core_end": core_end.strftime("%H:%M")
                }
            )
            
            # Send alert to manager
            employee_data = await self._get_employee_data(record["employee_id"])
            if employee_data.get("manager_id"):
                await comm_agent.send_communication(
                    recipient_id=employee_data["manager_id"],
                    communication_type="team_early_departure_alert",
                    channel="email",
                    template_data={
                        "employee_name": employee_data["name"],
                        "check_out_time": check_out_time.strftime("%H:%M"),
                        "core_end": core_end.strftime("%H:%M")
                    }
                )
            
        except Exception as e:
            logger.error(f"Early departure alert sending error: {str(e)}")

    async def _send_overtime_alert(self, record: Dict[str, Any]):
        """Send overtime alert"""
        try:
            from ..communication_agent.core import CommunicationAgent
            comm_agent = CommunicationAgent()
            
            # Send alert to employee
            await comm_agent.send_communication(
                recipient_id=record["employee_id"],
                communication_type="overtime_alert",
                channel="email",
                template_data={
                    "work_hours": record["work_hours"]
                }
            )
            
            # Send alert to manager
            employee_data = await self._get_employee_data(record["employee_id"])
            if employee_data.get("manager_id"):
                await comm_agent.send_communication(
                    recipient_id=employee_data["manager_id"],
                    communication_type="team_overtime_alert",
                    channel="email",
                    template_data={
                        "employee_name": employee_data["name"],
                        "work_hours": record["work_hours"]
                    }
                )
            
        except Exception as e:
            logger.error(f"Overtime alert sending error: {str(e)}")

    async def _generate_attendance_reports(self):
        """Generate attendance reports"""
        try:
            # Placeholder for generating attendance reports logic
            logger.info("Generating automated attendance reports")
            
        except Exception as e:
            logger.error(f"Attendance reports generation error: {str(e)}")

    async def _get_employee_data(self, employee_id: str) -> Dict[str, Any]:
        """Get employee data"""
        try:
            db = SessionLocal()
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            db.close()
            
            if employee:
                return {
                    "id": employee.id,
                    "name": employee.name,
                    "email": employee.email,
                    "phone": employee.phone,
                    "position": employee.position,
                    "department": employee.department,
                    "manager_id": employee.manager_id
                }
            return {}
        except Exception as e:
            logger.error(f"Employee data retrieval error: {str(e)}")
            return {}

    async def _calculate_leave_days(self, start_date: datetime, end_date: datetime) -> int:
        """Calculate working days between dates"""
        try:
            total_days = 0
            current_date = start_date
            
            while current_date <= end_date:
                # Skip weekends (assuming Monday=0, Sunday=6)
                if current_date.weekday() < 5:  # Monday to Friday
                    total_days += 1
                current_date += timedelta(days=1)
            
            return total_days
            
        except Exception as e:
            logger.error(f"Leave days calculation error: {str(e)}")
            return 0

    async def _get_used_leaves(self, employee_id: str, leave_type: str) -> int:
        """Get used leaves for current year"""
        try:
            current_year = datetime.utcnow().year
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            
            pipeline = [
                {
                    "$match": {
                        "employee_id": employee_id,
                        "leave_type": leave_type,
                        "status": "approved",
                        "start_date": {
                            "$gte": f"{current_year}-01-01",
                            "$lt": f"{current_year + 1}-01-01"
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_days": {"$sum": "$leave_days"}
                    }
                }
            ]
            
            result = await mongo_db.leave_requests.aggregate(pipeline).to_list(None)
            return result[0]["total_days"] if result else 0
            
        except Exception as e:
            logger.error(f"Get used leaves error: {str(e)}")
            return 0

    async def _update_leave_request(self, leave_request: Dict[str, Any]):
        """Update leave request in databases"""
        try:
            # Update SQL
            db = SessionLocal()
            leave_record = db.query(LeaveRequest).filter(LeaveRequest.id == leave_request["id"]).first()
            if leave_record:
                leave_record.status = leave_request["status"]
                db.commit()
            db.close()
            
            # Update MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.leave_requests.replace_one(
                {"id": leave_request["id"]},
                leave_request
            )
            
        except Exception as e:
            logger.error(f"Leave request update error: {str(e)}")

    async def _send_leave_notifications(self, leave_request: Dict[str, Any]):
        """Send automated leave notifications"""
        try:
            from ..communication_agent.core import CommunicationAgent
            comm_agent = CommunicationAgent()
            
            # Notify employee
            await comm_agent.send_communication(
                recipient_id=leave_request["employee_id"],
                communication_type="leave_status_update",
                channel="email",
                template_data=leave_request
            )
            
            # Notify manager if approved
            if leave_request["status"] == "approved":
                employee_data = await self._get_employee_data(leave_request["employee_id"])
                if employee_data.get("manager_id"):
                    await comm_agent.send_communication(
                        recipient_id=employee_data["manager_id"],
                        communication_type="team_leave_notification",
                        channel="email",
                        template_data=leave_request
                    )
            
        except Exception as e:
            logger.error(f"Leave notification error: {str(e)}")
