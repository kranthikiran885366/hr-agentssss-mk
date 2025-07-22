"""
Payroll Agent - Complete payroll and compensation management
Handles salary calculations, benefits, taxes, and compliance
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import uuid
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
import calendar

from .base_agent import BaseAgent
from backend.database.mongo_database import get_mongo_client
from backend.database.sql_database import SessionLocal
from models.sql_models import Employee, PayrollRecord, BenefitsEnrollment
from backend.utils.config import settings

logger = logging.getLogger(__name__)

class PayrollAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "payroll_agent"
        
        # Tax brackets and rates (simplified US federal)
        self.tax_brackets = {
            "federal": [
                {"min": 0, "max": 10275, "rate": 0.10},
                {"min": 10275, "max": 41775, "rate": 0.12},
                {"min": 41775, "max": 89450, "rate": 0.22},
                {"min": 89450, "max": 190750, "rate": 0.24},
                {"min": 190750, "max": 364200, "rate": 0.32},
                {"min": 364200, "max": 462500, "rate": 0.35},
                {"min": 462500, "max": float('inf'), "rate": 0.37}
            ],
            "social_security": {"rate": 0.062, "wage_base": 147000},
            "medicare": {"rate": 0.0145, "additional_rate": 0.009, "threshold": 200000},
            "unemployment": {"rate": 0.006, "wage_base": 7000}
        }
        
        # State tax rates (simplified)
        self.state_tax_rates = {
            "CA": 0.08, "NY": 0.07, "TX": 0.00, "FL": 0.00,
            "WA": 0.00, "OR": 0.09, "IL": 0.05, "MA": 0.05
        }
        
        # Benefits configurations
        self.benefits_config = {
            "health_insurance": {
                "employee_contribution": 0.25,
                "employer_contribution": 0.75,
                "monthly_premium": 450
            },
            "dental_insurance": {
                "employee_contribution": 0.30,
                "employer_contribution": 0.70,
                "monthly_premium": 85
            },
            "vision_insurance": {
                "employee_contribution": 0.40,
                "employer_contribution": 0.60,
                "monthly_premium": 25
            },
            "retirement_401k": {
                "employee_max_contribution": 0.15,
                "employer_match": 0.06,
                "vesting_schedule": "immediate"
            },
            "life_insurance": {
                "coverage_multiple": 2.0,
                "employee_cost_per_1000": 0.50
            }
        }
        
        # Payroll frequencies
        self.payroll_frequencies = {
            "weekly": {"periods_per_year": 52, "days": 7},
            "bi_weekly": {"periods_per_year": 26, "days": 14},
            "semi_monthly": {"periods_per_year": 24, "days": 15},
            "monthly": {"periods_per_year": 12, "days": 30}
        }

    async def initialize(self):
        """Initialize payroll agent"""
        try:
            logger.info("Initializing Payroll Agent...")
            await super().initialize()
            
            # Start automated processes
            asyncio.create_task(self._automated_payroll_processing())
            asyncio.create_task(self._automated_tax_calculations())
            asyncio.create_task(self._automated_benefits_processing())
            asyncio.create_task(self._automated_compliance_monitoring())
            
            self.is_initialized = True
            logger.info("Payroll Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Payroll Agent: {str(e)}")
            raise

    async def process_payroll(self, pay_period_start: str, pay_period_end: str, 
                            employee_ids: List[str] = None) -> Dict[str, Any]:
        """Process complete payroll for pay period"""
        try:
            payroll_run_id = str(uuid.uuid4())
            
            payroll_run = {
                "id": payroll_run_id,
                "pay_period_start": pay_period_start,
                "pay_period_end": pay_period_end,
                "processed_at": datetime.utcnow().isoformat(),
                "status": "processing",
                "employee_payrolls": [],
                "totals": {
                    "gross_pay": 0.0,
                    "net_pay": 0.0,
                    "total_taxes": 0.0,
                    "total_deductions": 0.0,
                    "employer_costs": 0.0
                },
                "compliance_checks": [],
                "errors": []
            }
            
            # Get employees to process
            if not employee_ids:
                employee_ids = await self._get_active_employee_ids()
            
            # Process each employee
            for employee_id in employee_ids:
                try:
                    employee_payroll = await self._process_employee_payroll(
                        employee_id, pay_period_start, pay_period_end
                    )
                    payroll_run["employee_payrolls"].append(employee_payroll)
                    
                    # Update totals
                    payroll_run["totals"]["gross_pay"] += employee_payroll["gross_pay"]
                    payroll_run["totals"]["net_pay"] += employee_payroll["net_pay"]
                    payroll_run["totals"]["total_taxes"] += employee_payroll["total_taxes"]
                    payroll_run["totals"]["total_deductions"] += employee_payroll["total_deductions"]
                    payroll_run["totals"]["employer_costs"] += employee_payroll["employer_costs"]
                    
                except Exception as e:
                    payroll_run["errors"].append({
                        "employee_id": employee_id,
                        "error": str(e)
                    })
            
            # Run compliance checks
            payroll_run["compliance_checks"] = await self._run_payroll_compliance_checks(payroll_run)
            
            # Finalize payroll run
            payroll_run["status"] = "completed" if not payroll_run["errors"] else "completed_with_errors"
            
            # Store payroll run
            await self._store_payroll_run(payroll_run)
            
            # Generate payroll reports
            await self._generate_payroll_reports(payroll_run)
            
            # Send notifications
            await self._send_payroll_notifications(payroll_run)
            
            return payroll_run
            
        except Exception as e:
            logger.error(f"Payroll processing error: {str(e)}")
            raise

    async def _process_employee_payroll(self, employee_id: str, pay_period_start: str, 
                                      pay_period_end: str) -> Dict[str, Any]:
        """Process individual employee payroll"""
        try:
            # Get employee data
            employee = await self._get_employee_data(employee_id)
            
            # Calculate time worked
            time_data = await self._calculate_time_worked(employee_id, pay_period_start, pay_period_end)
            
            # Calculate gross pay
            gross_pay_data = await self._calculate_gross_pay(employee, time_data)
            
            # Calculate taxes
            tax_data = await self._calculate_taxes(employee, gross_pay_data)
            
            # Calculate deductions
            deduction_data = await self._calculate_deductions(employee, gross_pay_data)
            
            # Calculate net pay
            net_pay = gross_pay_data["total_gross"] - tax_data["total_taxes"] - deduction_data["total_deductions"]
            
            # Calculate employer costs
            employer_costs = await self._calculate_employer_costs(employee, gross_pay_data)
            
            employee_payroll = {
                "employee_id": employee_id,
                "employee_name": employee["name"],
                "pay_period_start": pay_period_start,
                "pay_period_end": pay_period_end,
                "time_data": time_data,
                "gross_pay_breakdown": gross_pay_data,
                "gross_pay": gross_pay_data["total_gross"],
                "tax_breakdown": tax_data,
                "total_taxes": tax_data["total_taxes"],
                "deduction_breakdown": deduction_data,
                "total_deductions": deduction_data["total_deductions"],
                "net_pay": net_pay,
                "employer_costs": employer_costs["total_cost"],
                "employer_cost_breakdown": employer_costs,
                "pay_stub_data": await self._generate_pay_stub_data(employee, gross_pay_data, tax_data, deduction_data, net_pay)
            }
            
            return employee_payroll
            
        except Exception as e:
            logger.error(f"Employee payroll processing error for {employee_id}: {str(e)}")
            raise

    async def _calculate_time_worked(self, employee_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Calculate time worked during pay period"""
        try:
            # Get attendance records
            attendance_records = await self._get_attendance_records(employee_id, start_date, end_date)
            
            time_data = {
                "regular_hours": 0.0,
                "overtime_hours": 0.0,
                "double_time_hours": 0.0,
                "holiday_hours": 0.0,
                "sick_hours": 0.0,
                "vacation_hours": 0.0,
                "total_hours": 0.0,
                "days_worked": 0,
                "attendance_details": []
            }
            
            for record in attendance_records:
                daily_hours = record.get("work_hours", 0)
                record_type = record.get("type", "regular")
                
                if record_type == "holiday":
                    time_data["holiday_hours"] += daily_hours
                elif record_type == "sick":
                    time_data["sick_hours"] += daily_hours
                elif record_type == "vacation":
                    time_data["vacation_hours"] += daily_hours
                else:
                    # Regular work day
                    if daily_hours <= 8:
                        time_data["regular_hours"] += daily_hours
                    elif daily_hours <= 12:
                        time_data["regular_hours"] += 8
                        time_data["overtime_hours"] += (daily_hours - 8)
                    else:
                        time_data["regular_hours"] += 8
                        time_data["overtime_hours"] += 4
                        time_data["double_time_hours"] += (daily_hours - 12)
                
                time_data["days_worked"] += 1
                time_data["attendance_details"].append(record)
            
            time_data["total_hours"] = (
                time_data["regular_hours"] + time_data["overtime_hours"] + 
                time_data["double_time_hours"] + time_data["holiday_hours"] + 
                time_data["sick_hours"] + time_data["vacation_hours"]
            )
            
            return time_data
            
        except Exception as e:
            logger.error(f"Time calculation error: {str(e)}")
            return {"regular_hours": 80, "total_hours": 80}  # Default full-time

    async def _calculate_gross_pay(self, employee: Dict[str, Any], time_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate gross pay components"""
        try:
            base_salary = employee.get("salary", 0)
            hourly_rate = employee.get("hourly_rate", base_salary / 2080)  # Annual to hourly
            
            gross_pay_data = {
                "base_pay": 0.0,
                "overtime_pay": 0.0,
                "double_time_pay": 0.0,
                "holiday_pay": 0.0,
                "sick_pay": 0.0,
                "vacation_pay": 0.0,
                "bonus": 0.0,
                "commission": 0.0,
                "allowances": 0.0,
                "total_gross": 0.0
            }
            
            # Calculate pay components
            gross_pay_data["base_pay"] = time_data["regular_hours"] * hourly_rate
            gross_pay_data["overtime_pay"] = time_data["overtime_hours"] * hourly_rate * 1.5
            gross_pay_data["double_time_pay"] = time_data["double_time_hours"] * hourly_rate * 2.0
            gross_pay_data["holiday_pay"] = time_data["holiday_hours"] * hourly_rate
            gross_pay_data["sick_pay"] = time_data["sick_hours"] * hourly_rate
            gross_pay_data["vacation_pay"] = time_data["vacation_hours"] * hourly_rate
            
            # Add bonuses and commissions
            gross_pay_data["bonus"] = employee.get("current_bonus", 0)
            gross_pay_data["commission"] = employee.get("current_commission", 0)
            gross_pay_data["allowances"] = employee.get("allowances", 0)
            
            # Calculate total
            gross_pay_data["total_gross"] = sum(gross_pay_data.values()) - gross_pay_data["total_gross"]
            
            return gross_pay_data
            
        except Exception as e:
            logger.error(f"Gross pay calculation error: {str(e)}")
            return {"total_gross": 0.0}

    async def _calculate_taxes(self, employee: Dict[str, Any], gross_pay_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all tax withholdings"""
        try:
            gross_pay = gross_pay_data["total_gross"]
            annual_gross = gross_pay * 26  # Bi-weekly assumption
            
            tax_data = {
                "federal_income_tax": 0.0,
                "state_income_tax": 0.0,
                "social_security_tax": 0.0,
                "medicare_tax": 0.0,
                "additional_medicare_tax": 0.0,
                "state_disability_tax": 0.0,
                "local_taxes": 0.0,
                "total_taxes": 0.0
            }
            
            # Federal income tax (progressive)
            tax_data["federal_income_tax"] = await self._calculate_federal_tax(annual_gross) / 26
            
            # State income tax
            state = employee.get("state", "CA")
            state_rate = self.state_tax_rates.get(state, 0.05)
            tax_data["state_income_tax"] = gross_pay * state_rate
            
            # Social Security tax
            ss_config = self.tax_brackets["social_security"]
            if annual_gross <= ss_config["wage_base"]:
                tax_data["social_security_tax"] = gross_pay * ss_config["rate"]
            else:
                remaining_base = max(0, ss_config["wage_base"] - (annual_gross - gross_pay))
                tax_data["social_security_tax"] = min(gross_pay, remaining_base) * ss_config["rate"]
            
            # Medicare tax
            medicare_config = self.tax_brackets["medicare"]
            tax_data["medicare_tax"] = gross_pay * medicare_config["rate"]
            
            # Additional Medicare tax (high earners)
            if annual_gross > medicare_config["threshold"]:
                additional_wages = max(0, annual_gross - medicare_config["threshold"])
                tax_data["additional_medicare_tax"] = min(gross_pay, additional_wages) * medicare_config["additional_rate"]
            
            # State disability insurance (CA example)
            if state == "CA":
                tax_data["state_disability_tax"] = gross_pay * 0.009  # CA SDI rate
            
            # Calculate total
            tax_data["total_taxes"] = sum(tax_data.values()) - tax_data["total_taxes"]
            
            return tax_data
            
        except Exception as e:
            logger.error(f"Tax calculation error: {str(e)}")
            return {"total_taxes": 0.0}

    async def _calculate_federal_tax(self, annual_income: float) -> float:
        """Calculate federal income tax using progressive brackets"""
        try:
            total_tax = 0.0
            remaining_income = annual_income
            
            for bracket in self.tax_brackets["federal"]:
                if remaining_income <= 0:
                    break
                
                bracket_min = bracket["min"]
                bracket_max = bracket["max"]
                bracket_rate = bracket["rate"]
                
                if annual_income > bracket_min:
                    taxable_in_bracket = min(remaining_income, bracket_max - bracket_min)
                    total_tax += taxable_in_bracket * bracket_rate
                    remaining_income -= taxable_in_bracket
            
            return total_tax
            
        except Exception as e:
            logger.error(f"Federal tax calculation error: {str(e)}")
            return annual_income * 0.22  # Default rate

    async def _calculate_deductions(self, employee: Dict[str, Any], gross_pay_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all payroll deductions"""
        try:
            gross_pay = gross_pay_data["total_gross"]
            
            deduction_data = {
                "health_insurance": 0.0,
                "dental_insurance": 0.0,
                "vision_insurance": 0.0,
                "retirement_401k": 0.0,
                "life_insurance": 0.0,
                "disability_insurance": 0.0,
                "hsa_contribution": 0.0,
                "parking": 0.0,
                "union_dues": 0.0,
                "garnishments": 0.0,
                "other_deductions": 0.0,
                "total_deductions": 0.0
            }
            
            # Get employee benefit elections
            benefit_elections = await self._get_benefit_elections(employee["id"])
            
            # Health insurance
            if benefit_elections.get("health_insurance"):
                monthly_premium = self.benefits_config["health_insurance"]["monthly_premium"]
                employee_portion = self.benefits_config["health_insurance"]["employee_contribution"]
                deduction_data["health_insurance"] = (monthly_premium * employee_portion) / 2  # Bi-weekly
            
            # Dental insurance
            if benefit_elections.get("dental_insurance"):
                monthly_premium = self.benefits_config["dental_insurance"]["monthly_premium"]
                employee_portion = self.benefits_config["dental_insurance"]["employee_contribution"]
                deduction_data["dental_insurance"] = (monthly_premium * employee_portion) / 2
            
            # Vision insurance
            if benefit_elections.get("vision_insurance"):
                monthly_premium = self.benefits_config["vision_insurance"]["monthly_premium"]
                employee_portion = self.benefits_config["vision_insurance"]["employee_contribution"]
                deduction_data["vision_insurance"] = (monthly_premium * employee_portion) / 2
            
            # 401k contribution
            contribution_rate = benefit_elections.get("retirement_401k_rate", 0.06)
            max_contribution = self.benefits_config["retirement_401k"]["employee_max_contribution"]
            actual_rate = min(contribution_rate, max_contribution)
            deduction_data["retirement_401k"] = gross_pay * actual_rate
            
            # Life insurance
            if benefit_elections.get("life_insurance"):
                salary = employee.get("salary", 50000)
                coverage = salary * self.benefits_config["life_insurance"]["coverage_multiple"]
                cost_per_1000 = self.benefits_config["life_insurance"]["employee_cost_per_1000"]
                deduction_data["life_insurance"] = (coverage / 1000) * cost_per_1000 / 26  # Bi-weekly
            
            # HSA contribution
            hsa_contribution = benefit_elections.get("hsa_contribution_per_pay", 0)
            deduction_data["hsa_contribution"] = hsa_contribution
            
            # Other deductions
            deduction_data["parking"] = employee.get("parking_deduction", 0)
            deduction_data["union_dues"] = employee.get("union_dues", 0)
            deduction_data["garnishments"] = employee.get("garnishments", 0)
            
            # Calculate total
            deduction_data["total_deductions"] = sum(deduction_data.values()) - deduction_data["total_deductions"]
            
            return deduction_data
            
        except Exception as e:
            logger.error(f"Deductions calculation error: {str(e)}")
            return {"total_deductions": 0.0}

    async def _calculate_employer_costs(self, employee: Dict[str, Any], gross_pay_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate employer payroll costs"""
        try:
            gross_pay = gross_pay_data["total_gross"]
            
            employer_costs = {
                "social_security_match": 0.0,
                "medicare_match": 0.0,
                "federal_unemployment": 0.0,
                "state_unemployment": 0.0,
                "workers_compensation": 0.0,
                "health_insurance_contribution": 0.0,
                "dental_insurance_contribution": 0.0,
                "vision_insurance_contribution": 0.0,
                "retirement_match": 0.0,
                "life_insurance_premium": 0.0,
                "total_cost": 0.0
            }
            
            # Payroll tax matches
            employer_costs["social_security_match"] = gross_pay * 0.062
            employer_costs["medicare_match"] = gross_pay * 0.0145
            employer_costs["federal_unemployment"] = min(gross_pay, 7000 / 26) * 0.006
            employer_costs["state_unemployment"] = gross_pay * 0.034  # Average state rate
            employer_costs["workers_compensation"] = gross_pay * 0.015  # Average rate
            
            # Benefit contributions
            benefit_elections = await self._get_benefit_elections(employee["id"])
            
            if benefit_elections.get("health_insurance"):
                monthly_premium = self.benefits_config["health_insurance"]["monthly_premium"]
                employer_portion = self.benefits_config["health_insurance"]["employer_contribution"]
                employer_costs["health_insurance_contribution"] = (monthly_premium * employer_portion) / 2
            
            if benefit_elections.get("dental_insurance"):
                monthly_premium = self.benefits_config["dental_insurance"]["monthly_premium"]
                employer_portion = self.benefits_config["dental_insurance"]["employer_contribution"]
                employer_costs["dental_insurance_contribution"] = (monthly_premium * employer_portion) / 2
            
            if benefit_elections.get("vision_insurance"):
                monthly_premium = self.benefits_config["vision_insurance"]["monthly_premium"]
                employer_portion = self.benefits_config["vision_insurance"]["employer_contribution"]
                employer_costs["vision_insurance_contribution"] = (monthly_premium * employer_portion) / 2
            
            # 401k match
            employee_contribution_rate = benefit_elections.get("retirement_401k_rate", 0)
            employer_match_rate = min(employee_contribution_rate, 0.06)  # Match up to 6%
            employer_costs["retirement_match"] = gross_pay * employer_match_rate
            
            # Calculate total
            employer_costs["total_cost"] = sum(employer_costs.values()) - employer_costs["total_cost"]
            
            return employer_costs
            
        except Exception as e:
            logger.error(f"Employer costs calculation error: {str(e)}")
            return {"total_cost": 0.0}

    async def manage_benefits_enrollment(self, employee_id: str, enrollment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage employee benefits enrollment"""
        try:
            enrollment_id = str(uuid.uuid4())
            
            # Validate enrollment eligibility
            eligibility = await self._check_benefits_eligibility(employee_id)
            if not eligibility["eligible"]:
                return {
                    "enrollment_id": enrollment_id,
                    "status": "rejected",
                    "reason": eligibility["reason"]
                }
            
            # Process benefit elections
            enrollment_result = {
                "enrollment_id": enrollment_id,
                "employee_id": employee_id,
                "enrollment_date": datetime.utcnow().isoformat(),
                "benefit_elections": {},
                "cost_breakdown": {},
                "total_employee_cost": 0.0,
                "total_employer_cost": 0.0,
                "effective_date": enrollment_data.get("effective_date", datetime.utcnow().isoformat()),
                "status": "active"
            }
            
            # Process each benefit election
            for benefit_type, election in enrollment_data.get("elections", {}).items():
                if election.get("elected", False):
                    benefit_cost = await self._calculate_benefit_cost(benefit_type, election, employee_id)
                    
                    enrollment_result["benefit_elections"][benefit_type] = {
                        "elected": True,
                        "plan": election.get("plan", "standard"),
                        "coverage_level": election.get("coverage_level", "employee_only"),
                        "employee_cost": benefit_cost["employee_cost"],
                        "employer_cost": benefit_cost["employer_cost"]
                    }
                    
                    enrollment_result["cost_breakdown"][benefit_type] = benefit_cost
                    enrollment_result["total_employee_cost"] += benefit_cost["employee_cost"]
                    enrollment_result["total_employer_cost"] += benefit_cost["employer_cost"]
            
            # Store enrollment
            await self._store_benefits_enrollment(enrollment_result)
            
            # Generate enrollment confirmation
            await self._generate_enrollment_confirmation(enrollment_result)
            
            # Send notifications
            await self._send_enrollment_notifications(enrollment_result)
            
            return enrollment_result
            
        except Exception as e:
            logger.error(f"Benefits enrollment error: {str(e)}")
            raise

    async def calculate_compensation_analysis(self, employee_id: str) -> Dict[str, Any]:
        """Comprehensive compensation analysis"""
        try:
            employee = await self._get_employee_data(employee_id)
            
            analysis = {
                "employee_id": employee_id,
                "analysis_date": datetime.utcnow().isoformat(),
                "current_compensation": {},
                "market_analysis": {},
                "total_compensation": {},
                "recommendations": [],
                "pay_equity_analysis": {},
                "career_progression": {}
            }
            
            # Current compensation breakdown
            analysis["current_compensation"] = {
                "base_salary": employee.get("salary", 0),
                "bonus_target": employee.get("bonus_target", 0),
                "equity_value": employee.get("equity_value", 0),
                "benefits_value": await self._calculate_benefits_value(employee_id),
                "perks_value": await self._calculate_perks_value(employee_id)
            }
            
            # Market analysis
            analysis["market_analysis"] = await self._analyze_market_compensation(employee)
            
            # Total compensation calculation
            total_comp = sum(analysis["current_compensation"].values())
            analysis["total_compensation"] = {
                "total_value": total_comp,
                "percentile": await self._calculate_market_percentile(employee, total_comp),
                "competitiveness": await self._assess_competitiveness(employee, total_comp)
            }
            
            # Pay equity analysis
            analysis["pay_equity_analysis"] = await self._analyze_pay_equity(employee)
            
            # Generate recommendations
            analysis["recommendations"] = await self._generate_compensation_recommendations(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Compensation analysis error: {str(e)}")
            raise

    async def _automated_payroll_processing(self):
        """Automated payroll processing"""
        while True:
            try:
                # Check if payroll run is due
                if await self._is_payroll_due():
                    # Get pay period dates
                    pay_period = await self._get_current_pay_period()
                    
                    # Process payroll
                    await self.process_payroll(
                        pay_period["start"],
                        pay_period["end"]
                    )
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Automated payroll processing error: {str(e)}")
                await asyncio.sleep(3600)

    async def _automated_tax_calculations(self):
        """Automated tax calculations and updates"""
        while True:
            try:
                # Update tax tables if needed
                await self._update_tax_tables()
                
                # Process tax adjustments
                await self._process_tax_adjustments()
                
                # Generate tax reports
                await self._generate_tax_reports()
                
                # Sleep for 7 days
                await asyncio.sleep(604800)
                
            except Exception as e:
                logger.error(f"Automated tax calculations error: {str(e)}")
                await asyncio.sleep(86400)

    # Helper methods
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
                    "salary": employee.salary or 0,
                    "hourly_rate": employee.hourly_rate or 0,
                    "department": employee.department,
                    "position": employee.position,
                    "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
                    "state": employee.state or "CA",
                    "tax_status": employee.tax_status or "single"
                }
            return {}
        except Exception as e:
            logger.error(f"Employee data retrieval error: {str(e)}")
            return {}

    async def _get_attendance_records(self, employee_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get attendance records for pay period"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            
            records = await mongo_db.attendance_records.find({
                "employee_id": employee_id,
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }).to_list(None)
            
            return records
            
        except Exception as e:
            logger.error(f"Attendance records retrieval error: {str(e)}")
            return []

    async def _get_benefit_elections(self, employee_id: str) -> Dict[str, Any]:
        """Get employee benefit elections"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            
            elections = await mongo_db.benefit_elections.find_one({"employee_id": employee_id})
            return elections or {}
            
        except Exception as e:
            logger.error(f"Benefit elections retrieval error: {str(e)}")
            return {}

    async def _store_payroll_run(self, payroll_run: Dict[str, Any]):
        """Store payroll run data"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.payroll_runs.insert_one(payroll_run)
            
            # Store individual payroll records in SQL
            db = SessionLocal()
            for emp_payroll in payroll_run["employee_payrolls"]:
                payroll_record = PayrollRecord(
                    id=str(uuid.uuid4()),
                    employee_id=emp_payroll["employee_id"],
                    pay_period_start=datetime.fromisoformat(emp_payroll["pay_period_start"]),
                    pay_period_end=datetime.fromisoformat(emp_payroll["pay_period_end"]),
                    gross_pay=emp_payroll["gross_pay"],
                    net_pay=emp_payroll["net_pay"],
                    total_taxes=emp_payroll["total_taxes"],
                    total_deductions=emp_payroll["total_deductions"]
                )
                db.add(payroll_record)
            
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Payroll run storage error: {str(e)}")
