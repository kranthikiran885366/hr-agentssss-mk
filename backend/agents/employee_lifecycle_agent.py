"""
Employee Lifecycle Agent - Complete employee journey management
Handles hiring, onboarding, development, performance, and offboarding
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import uuid
import numpy as np

from .base_agent import BaseAgent
from backend.database.mongo_database import get_mongo_client
from backend.database.sql_database import SessionLocal
from models.sql_models import Employee, LifecycleEvent, CareerPath
from backend.utils.config import settings

logger = logging.getLogger(__name__)

class EmployeeLifecycleAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "employee_lifecycle_agent"
        
        # Lifecycle stages
        self.lifecycle_stages = {
            "pre_hire": {
                "duration_days": 14,
                "key_activities": ["background_check", "reference_verification", "offer_negotiation"],
                "stakeholders": ["hiring_manager", "hr", "candidate"]
            },
            "onboarding": {
                "duration_days": 90,
                "key_activities": ["orientation", "documentation", "training", "system_access"],
                "stakeholders": ["hr", "manager", "buddy", "it"]
            },
            "probation": {
                "duration_days": 90,
                "key_activities": ["performance_monitoring", "feedback_sessions", "skill_assessment"],
                "stakeholders": ["manager", "hr", "employee"]
            },
            "active_employment": {
                "duration_days": None,
                "key_activities": ["performance_reviews", "career_development", "training"],
                "stakeholders": ["manager", "employee", "hr"]
            },
            "career_transition": {
                "duration_days": 30,
                "key_activities": ["role_change", "promotion", "lateral_move"],
                "stakeholders": ["current_manager", "new_manager", "hr", "employee"]
            },
            "pre_departure": {
                "duration_days": 14,
                "key_activities": ["resignation_processing", "transition_planning", "exit_interview"],
                "stakeholders": ["manager", "hr", "employee"]
            },
            "offboarding": {
                "duration_days": 7,
                "key_activities": ["knowledge_transfer", "asset_return", "access_revocation"],
                "stakeholders": ["manager", "hr", "it", "employee"]
            }
        }
        
        # Career progression paths
        self.career_paths = {
            "individual_contributor": {
                "levels": ["junior", "mid", "senior", "staff", "principal"],
                "progression_criteria": {
                    "technical_skills": [60, 70, 80, 90, 95],
                    "experience_years": [0, 2, 5, 8, 12],
                    "project_complexity": [3, 5, 7, 9, 10]
                }
            },
            "management": {
                "levels": ["team_lead", "manager", "senior_manager", "director", "vp"],
                "progression_criteria": {
                    "leadership_skills": [70, 80, 85, 90, 95],
                    "team_size": [3, 8, 15, 30, 50],
                    "business_impact": [5, 7, 8, 9, 10]
                }
            },
            "specialist": {
                "levels": ["specialist", "senior_specialist", "expert", "principal_expert", "distinguished"],
                "progression_criteria": {
                    "domain_expertise": [75, 85, 90, 95, 98],
                    "innovation_score": [6, 7, 8, 9, 10],
                    "industry_recognition": [3, 5, 7, 8, 10]
                }
            }
        }

    async def initialize(self):
        """Initialize employee lifecycle agent"""
        try:
            logger.info("Initializing Employee Lifecycle Agent...")
            await super().initialize()
            
            # Start automated processes
            asyncio.create_task(self._automated_lifecycle_monitoring())
            asyncio.create_task(self._automated_career_progression())
            asyncio.create_task(self._automated_milestone_tracking())
            asyncio.create_task(self._automated_retention_analysis())
            
            self.is_initialized = True
            logger.info("Employee Lifecycle Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Employee Lifecycle Agent: {str(e)}")
            raise

    async def track_employee_journey(self, employee_id: str) -> Dict[str, Any]:
        """Track complete employee journey and lifecycle"""
        try:
            journey_data = {
                "employee_id": employee_id,
                "tracked_at": datetime.utcnow().isoformat(),
                "current_stage": "",
                "stage_history": [],
                "milestones": [],
                "career_progression": {},
                "performance_trends": {},
                "engagement_metrics": {},
                "risk_factors": [],
                "recommendations": [],
                "predicted_outcomes": {}
            }
            
            # Get employee data
            employee = await self._get_employee_data(employee_id)
            
            # Determine current lifecycle stage
            journey_data["current_stage"] = await self._determine_current_stage(employee)
            
            # Get stage history
            journey_data["stage_history"] = await self._get_stage_history(employee_id)
            
            # Track milestones
            journey_data["milestones"] = await self._track_milestones(employee_id)
            
            # Analyze career progression
            journey_data["career_progression"] = await self._analyze_career_progression(employee)
            
            # Get performance trends
            journey_data["performance_trends"] = await self._get_performance_trends(employee_id)
            
            # Calculate engagement metrics
            journey_data["engagement_metrics"] = await self._calculate_engagement_metrics(employee_id)
            
            # Identify risk factors
            journey_data["risk_factors"] = await self._identify_risk_factors(employee, journey_data)
            
            # Generate recommendations
            journey_data["recommendations"] = await self._generate_lifecycle_recommendations(journey_data)
            
            # Predict outcomes
            journey_data["predicted_outcomes"] = await self._predict_employee_outcomes(journey_data)
            
            # Store journey data
            await self._store_journey_data(journey_data)
            
            return journey_data
            
        except Exception as e:
            logger.error(f"Employee journey tracking error: {str(e)}")
            raise

    async def manage_career_development(self, employee_id: str, development_goals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Manage employee career development and progression"""
        try:
            development_plan_id = str(uuid.uuid4())
            
            # Get employee data
            employee = await self._get_employee_data(employee_id)
            
            # Analyze current position
            current_analysis = await self._analyze_current_position(employee)
            
            # Create development plan
            development_plan = {
                "id": development_plan_id,
                "employee_id": employee_id,
                "created_at": datetime.utcnow().isoformat(),
                "current_analysis": current_analysis,
                "development_goals": [],
                "career_path": await self._recommend_career_path(employee),
                "skill_gaps": await self._identify_skill_gaps(employee),
                "learning_opportunities": [],
                "mentorship_recommendations": [],
                "timeline": {},
                "success_metrics": [],
                "progress_tracking": {}
            }
            
            # Process each development goal
            for goal in development_goals:
                processed_goal = await self._process_development_goal(goal, employee)
                development_plan["development_goals"].append(processed_goal)
                
                # Add learning opportunities
                opportunities = await self._find_learning_opportunities(processed_goal)
                development_plan["learning_opportunities"].extend(opportunities)
            
            # Create timeline
            development_plan["timeline"] = await self._create_development_timeline(development_plan)
            
            # Define success metrics
            development_plan["success_metrics"] = await self._define_success_metrics(development_plan)
            
            # Set up progress tracking
            development_plan["progress_tracking"] = await self._setup_progress_tracking(development_plan)
            
            # Find mentorship opportunities
            development_plan["mentorship_recommendations"] = await self._recommend_mentors(employee, development_plan)
            
            # Store development plan
            await self._store_development_plan(development_plan)
            
            # Create action items
            await self._create_development_action_items(development_plan)
            
            # Send notifications
            await self._send_development_notifications(development_plan)
            
            return development_plan
            
        except Exception as e:
            logger.error(f"Career development management error: {str(e)}")
            raise

    async def process_role_transition(self, employee_id: str, transition_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process employee role transitions (promotion, lateral move, etc.)"""
        try:
            transition_id = str(uuid.uuid4())
            
            transition_process = {
                "id": transition_id,
                "employee_id": employee_id,
                "transition_type": transition_data["type"],  # promotion, lateral_move, demotion, department_change
                "from_role": transition_data["from_role"],
                "to_role": transition_data["to_role"],
                "effective_date": transition_data["effective_date"],
                "initiated_at": datetime.utcnow().isoformat(),
                "status": "initiated",
                "approval_workflow": [],
                "transition_plan": {},
                "knowledge_transfer": {},
                "stakeholder_communications": [],
                "system_updates": [],
                "compensation_changes": {},
                "training_requirements": []
            }
            
            # Create approval workflow
            transition_process["approval_workflow"] = await self._create_approval_workflow(transition_data)
            
            # Create transition plan
            transition_process["transition_plan"] = await self._create_transition_plan(transition_data)
            
            # Plan knowledge transfer
            transition_process["knowledge_transfer"] = await self._plan_knowledge_transfer(transition_data)
            
            # Identify stakeholder communications
            transition_process["stakeholder_communications"] = await self._plan_stakeholder_communications(transition_data)
            
            # Plan system updates
            transition_process["system_updates"] = await self._plan_system_updates(transition_data)
            
            # Calculate compensation changes
            transition_process["compensation_changes"] = await self._calculate_compensation_changes(transition_data)
            
            # Identify training requirements
            transition_process["training_requirements"] = await self._identify_training_requirements(transition_data)
            
            # Start approval process
            await self._start_approval_process(transition_process)
            
            # Store transition process
            await self._store_transition_process(transition_process)
            
            return transition_process
            
        except Exception as e:
            logger.error(f"Role transition processing error: {str(e)}")
            raise

    async def manage_employee_offboarding(self, employee_id: str, departure_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage complete employee offboarding process"""
        try:
            offboarding_id = str(uuid.uuid4())
            
            offboarding_process = {
                "id": offboarding_id,
                "employee_id": employee_id,
                "departure_type": departure_data["type"],  # resignation, termination, retirement, layoff
                "departure_date": departure_data["departure_date"],
                "last_working_day": departure_data["last_working_day"],
                "initiated_at": datetime.utcnow().isoformat(),
                "status": "initiated",
                "exit_interview": {},
                "knowledge_transfer": {},
                "asset_return": {},
                "access_revocation": {},
                "final_payroll": {},
                "benefits_continuation": {},
                "reference_policy": {},
                "rehire_eligibility": {},
                "completion_checklist": []
            }
            
            # Schedule exit interview
            offboarding_process["exit_interview"] = await self._schedule_exit_interview(employee_id, departure_data)
            
            # Plan knowledge transfer
            offboarding_process["knowledge_transfer"] = await self._plan_offboarding_knowledge_transfer(employee_id)
            
            # Create asset return checklist
            offboarding_process["asset_return"] = await self._create_asset_return_checklist(employee_id)
            
            # Plan access revocation
            offboarding_process["access_revocation"] = await self._plan_access_revocation(employee_id)
            
            # Calculate final payroll
            offboarding_process["final_payroll"] = await self._calculate_final_payroll(employee_id, departure_data)
            
            # Handle benefits continuation
            offboarding_process["benefits_continuation"] = await self._handle_benefits_continuation(employee_id, departure_data)
            
            # Set reference policy
            offboarding_process["reference_policy"] = await self._set_reference_policy(employee_id, departure_data)
            
            # Determine rehire eligibility
            offboarding_process["rehire_eligibility"] = await self._determine_rehire_eligibility(employee_id, departure_data)
            
            # Create completion checklist
            offboarding_process["completion_checklist"] = await self._create_offboarding_checklist(offboarding_process)
            
            # Start offboarding workflow
            await self._start_offboarding_workflow(offboarding_process)
            
            # Store offboarding process
            await self._store_offboarding_process(offboarding_process)
            
            return offboarding_process
            
        except Exception as e:
            logger.error(f"Employee offboarding error: {str(e)}")
            raise

    async def analyze_employee_retention(self, department: str = None, time_period: str = "12m") -> Dict[str, Any]:
        """Analyze employee retention and turnover patterns"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            if time_period == "6m":
                start_date = end_date - timedelta(days=180)
            elif time_period == "12m":
                start_date = end_date - timedelta(days=365)
            elif time_period == "24m":
                start_date = end_date - timedelta(days=730)
            else:
                start_date = end_date - timedelta(days=365)
            
            retention_analysis = {
                "analysis_period": time_period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "department": department,
                "overall_metrics": {},
                "turnover_analysis": {},
                "retention_drivers": {},
                "risk_segments": {},
                "predictive_insights": {},
                "recommendations": [],
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Get employee data
            employees = await self._get_employees_for_retention_analysis(department, start_date, end_date)
            
            # Calculate overall metrics
            retention_analysis["overall_metrics"] = await self._calculate_retention_metrics(employees, start_date, end_date)
            
            # Analyze turnover patterns
            retention_analysis["turnover_analysis"] = await self._analyze_turnover_patterns(employees)
            
            # Identify retention drivers
            retention_analysis["retention_drivers"] = await self._identify_retention_drivers(employees)
            
            # Segment at-risk employees
            retention_analysis["risk_segments"] = await self._segment_at_risk_employees(employees)
            
            # Generate predictive insights
            retention_analysis["predictive_insights"] = await self._generate_predictive_insights(employees)
            
            # Create recommendations
            retention_analysis["recommendations"] = await self._generate_retention_recommendations(retention_analysis)
            
            return retention_analysis
            
        except Exception as e:
            logger.error(f"Employee retention analysis error: {str(e)}")
            raise

    async def _automated_lifecycle_monitoring(self):
        """Automated lifecycle monitoring"""
        while True:
            try:
                # Get all active employees
                active_employees = await self._get_active_employees()
                
                for employee in active_employees:
                    # Track journey
                    await self.track_employee_journey(employee["id"])
                    
                    # Check for stage transitions
                    await self._check_stage_transitions(employee)
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Automated lifecycle monitoring error: {str(e)}")
                await asyncio.sleep(3600)

    async def _automated_career_progression(self):
        """Automated career progression monitoring"""
        while True:
            try:
                # Get employees eligible for progression
                eligible_employees = await self._get_progression_eligible_employees()
                
                for employee in eligible_employees:
                    # Analyze progression readiness
                    readiness = await self._analyze_progression_readiness(employee)
                    
                    if readiness["ready"]:
                        # Create progression recommendation
                        await self._create_progression_recommendation(employee, readiness)
                
                # Sleep for 7 days
                await asyncio.sleep(604800)
                
            except Exception as e:
                logger.error(f"Automated career progression error: {str(e)}")
                await asyncio.sleep(86400)

    # Helper methods
    async def _get_employee_data(self, employee_id: str) -> Dict[str, Any]:
        """Get comprehensive employee data"""
        try:
            db = SessionLocal()
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            db.close()
            
            if employee:
                return {
                    "id": employee.id,
                    "name": employee.name,
                    "email": employee.email,
                    "department": employee.department,
                    "position": employee.position,
                    "level": employee.level,
                    "hire_date": employee.hire_date.isoformat() if employee.hire_date else None,
                    "manager_id": employee.manager_id,
                    "salary": employee.salary or 0,
                    "performance_rating": employee.performance_rating or 0,
                    "career_track": employee.career_track or "individual_contributor"
                }
            return {}
        except Exception as e:
            logger.error(f"Employee data retrieval error: {str(e)}")
            return {}

    async def _determine_current_stage(self, employee: Dict[str, Any]) -> str:
        """Determine employee's current lifecycle stage"""
        try:
            hire_date = employee.get("hire_date")
            if not hire_date:
                return "pre_hire"
            
            hire_dt = datetime.fromisoformat(hire_date)
            days_since_hire = (datetime.utcnow() - hire_dt).days
            
            if days_since_hire <= 90:
                return "onboarding"
            elif days_since_hire <= 180:
                return "probation"
            else:
                return "active_employment"
                
        except Exception as e:
            logger.error(f"Stage determination error: {str(e)}")
            return "active_employment"

    async def _analyze_career_progression(self, employee: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze employee's career progression"""
        try:
            career_track = employee.get("career_track", "individual_contributor")
            current_level = employee.get("level", "junior")
            
            progression_data = {
                "current_track": career_track,
                "current_level": current_level,
                "next_level": "",
                "progression_readiness": 0.0,
                "time_in_current_level": 0,
                "skills_for_next_level": [],
                "estimated_time_to_promotion": 0
            }
            
            # Get career path configuration
            path_config = self.career_paths.get(career_track, {})
            levels = path_config.get("levels", [])
            
            if current_level in levels:
                current_index = levels.index(current_level)
                if current_index < len(levels) - 1:
                    progression_data["next_level"] = levels[current_index + 1]
                    
                    # Calculate progression readiness
                    progression_data["progression_readiness"] = await self._calculate_progression_readiness(employee, career_track, current_level)
                    
                    # Estimate time to promotion
                    progression_data["estimated_time_to_promotion"] = await self._estimate_time_to_promotion(employee, progression_data["progression_readiness"])
            
            return progression_data
            
        except Exception as e:
            logger.error(f"Career progression analysis error: {str(e)}")
            return {}

    async def _identify_risk_factors(self, employee: Dict[str, Any], journey_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify employee retention risk factors"""
        try:
            risk_factors = []
            
            # Performance risk
            performance_rating = employee.get("performance_rating", 0)
            if performance_rating < 3.0:
                risk_factors.append({
                    "type": "performance",
                    "severity": "high",
                    "description": "Below average performance rating",
                    "impact": "termination_risk"
                })
            
            # Engagement risk
            engagement_score = journey_data.get("engagement_metrics", {}).get("overall_score", 0)
            if engagement_score < 60:
                risk_factors.append({
                    "type": "engagement",
                    "severity": "medium",
                    "description": "Low engagement score",
                    "impact": "turnover_risk"
                })
            
            # Career stagnation risk
            time_in_role = await self._calculate_time_in_current_role(employee)
            if time_in_role > 730:  # 2 years
                risk_factors.append({
                    "type": "career_stagnation",
                    "severity": "medium",
                    "description": "Extended time in current role without progression",
                    "impact": "turnover_risk"
                })
            
            # Compensation risk
            market_position = await self._get_market_position(employee)
            if market_position < 25:  # Below 25th percentile
                risk_factors.append({
                    "type": "compensation",
                    "severity": "high",
                    "description": "Below market compensation",
                    "impact": "turnover_risk"
                })
            
            return risk_factors
            
        except Exception as e:
            logger.error(f"Risk factors identification error: {str(e)}")
            return []

    async def _store_journey_data(self, journey_data: Dict[str, Any]):
        """Store employee journey data"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.employee_journeys.insert_one(journey_data)
            
        except Exception as e:
            logger.error(f"Journey data storage error: {str(e)}")

    async def _store_development_plan(self, development_plan: Dict[str, Any]):
        """Store career development plan"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.development_plans.insert_one(development_plan)
            
        except Exception as e:
            logger.error(f"Development plan storage error: {str(e)}")
