"""
Training Agent - Automated training and development management
Handles skill gap analysis, training recommendations, and progress tracking
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import openai
from datetime import datetime, timedelta
import json
import uuid
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from ..base_agent import BaseAgent
from .skill_assessor import SkillAssessor
from .course_recommender import CourseRecommender
from .progress_tracker import ProgressTracker
from backend.database.mongo_database import get_mongo_client
from backend.database.sql_database import SessionLocal
from models.sql_models import TrainingAssignment, Employee, TrainingCourse
from backend.utils.config import settings

logger = logging.getLogger(__name__)

class TrainingAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "training_agent"
        self.skill_assessor = SkillAssessor()
        self.course_recommender = CourseRecommender()
        self.progress_tracker = ProgressTracker()
        
        # Training categories and skills
        self.training_categories = {
            "technical": {
                "programming": ["Python", "JavaScript", "Java", "C++", "Go", "Rust"],
                "web_development": ["React", "Angular", "Vue", "Node.js", "Django", "Flask"],
                "data_science": ["Machine Learning", "Data Analysis", "Statistics", "SQL", "Pandas"],
                "cloud": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform"],
                "mobile": ["iOS", "Android", "React Native", "Flutter", "Swift", "Kotlin"]
            },
            "soft_skills": {
                "leadership": ["Team Management", "Decision Making", "Strategic Thinking", "Delegation"],
                "communication": ["Presentation Skills", "Writing", "Active Listening", "Negotiation"],
                "collaboration": ["Teamwork", "Conflict Resolution", "Cross-functional Work"],
                "personal": ["Time Management", "Problem Solving", "Critical Thinking", "Adaptability"]
            },
            "business": {
                "management": ["Project Management", "Process Improvement", "Quality Management"],
                "finance": ["Financial Analysis", "Budgeting", "Cost Management", "ROI Analysis"],
                "marketing": ["Digital Marketing", "Content Strategy", "SEO", "Analytics"],
                "sales": ["Sales Techniques", "Customer Relations", "CRM", "Lead Generation"]
            },
            "compliance": {
                "security": ["Information Security", "Data Privacy", "Cybersecurity", "GDPR"],
                "hr": ["Employment Law", "Diversity & Inclusion", "Performance Management"],
                "industry": ["Industry Regulations", "Quality Standards", "Safety Protocols"]
            }
        }
        
        # Learning paths
        self.learning_paths = {}
        
        # Training providers
        self.training_providers = {
            "internal": {"cost_multiplier": 0.3, "quality_score": 0.7},
            "coursera": {"cost_multiplier": 1.0, "quality_score": 0.85},
            "udemy": {"cost_multiplier": 0.6, "quality_score": 0.75},
            "linkedin_learning": {"cost_multiplier": 0.8, "quality_score": 0.80},
            "pluralsight": {"cost_multiplier": 1.2, "quality_score": 0.90},
            "custom_workshop": {"cost_multiplier": 2.0, "quality_score": 0.95}
        }

    async def initialize(self):
        """Initialize training agent components"""
        try:
            logger.info("Initializing Training Agent...")
            
            await super().initialize()
            
            # Initialize sub-components
            await self.skill_assessor.initialize()
            await self.course_recommender.initialize()
            await self.progress_tracker.initialize()
            
            # Initialize OpenAI
            openai.api_key = settings.OPENAI_API_KEY
            
            # Load training data
            await self._load_training_catalog()
            await self._build_learning_paths()
            
            # Start automated processes
            asyncio.create_task(self._automated_skill_gap_analysis())
            asyncio.create_task(self._automated_training_recommendations())
            asyncio.create_task(self._automated_progress_tracking())
            
            self.is_initialized = True
            logger.info("Training Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Training Agent: {str(e)}")
            raise

    async def assess_employee_skills(self, employee_id: str, assessment_type: str = "comprehensive") -> Dict[str, Any]:
        """Conduct comprehensive skill assessment"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # Get employee information
            employee_info = await self._get_employee_info(employee_id)
            
            # Conduct skill assessment
            skill_assessment = await self.skill_assessor.conduct_assessment(
                employee_id=employee_id,
                employee_info=employee_info,
                assessment_type=assessment_type
            )
            
            # Analyze current skills
            current_skills = await self._analyze_current_skills(skill_assessment)
            
            # Identify skill gaps
            skill_gaps = await self._identify_skill_gaps(employee_info, current_skills)
            
            # Generate skill recommendations
            recommendations = await self._generate_skill_recommendations(current_skills, skill_gaps)
            
            # Create assessment record
            assessment_record = {
                "id": assessment_id,
                "employee_id": employee_id,
                "employee_info": employee_info,
                "assessment_type": assessment_type,
                "conducted_at": datetime.utcnow().isoformat(),
                "current_skills": current_skills,
                "skill_gaps": skill_gaps,
                "recommendations": recommendations,
                "overall_score": await self._calculate_overall_score(current_skills),
                "strengths": await self._identify_strengths(current_skills),
                "development_areas": await self._identify_development_areas(skill_gaps),
                "next_assessment_date": (datetime.utcnow() + timedelta(days=180)).isoformat()
            }
            
            # Store assessment
            await self._store_skill_assessment(assessment_record)
            
            return {
                "assessment_id": assessment_id,
                "overall_score": assessment_record["overall_score"],
                "strengths": assessment_record["strengths"],
                "development_areas": assessment_record["development_areas"],
                "recommended_training": recommendations[:5],  # Top 5 recommendations
                "next_assessment": assessment_record["next_assessment_date"]
            }
            
        except Exception as e:
            logger.error(f"Skill assessment error: {str(e)}")
            raise

    async def recommend_training_plan(self, employee_id: str, career_goal: str = None, 
                                    time_commitment: str = "moderate") -> Dict[str, Any]:
        """Generate personalized training plan"""
        try:
            plan_id = str(uuid.uuid4())
            
            # Get latest skill assessment
            latest_assessment = await self._get_latest_assessment(employee_id)
            if not latest_assessment:
                # Conduct quick assessment
                latest_assessment = await self.assess_employee_skills(employee_id, "quick")
            
            # Get employee information and preferences
            employee_info = await self._get_employee_info(employee_id)
            learning_preferences = await self._get_learning_preferences(employee_id)
            
            # Determine learning path
            learning_path = await self._determine_learning_path(employee_info, career_goal)
            
            # Generate course recommendations
            course_recommendations = await self.course_recommender.recommend_courses(
                skill_gaps=latest_assessment.get("skill_gaps", []),
                learning_preferences=learning_preferences,
                career_goal=career_goal,
                time_commitment=time_commitment
            )
            
            # Create training schedule
            training_schedule = await self._create_training_schedule(
                course_recommendations, time_commitment
            )
            
            # Calculate training metrics
            training_metrics = await self._calculate_training_metrics(course_recommendations)
            
            # Create training plan
            training_plan = {
                "id": plan_id,
                "employee_id": employee_id,
                "employee_info": employee_info,
                "career_goal": career_goal,
                "learning_path": learning_path,
                "time_commitment": time_commitment,
                "created_at": datetime.utcnow().isoformat(),
                "course_recommendations": course_recommendations,
                "training_schedule": training_schedule,
                "estimated_duration": training_metrics["total_duration"],
                "estimated_cost": training_metrics["total_cost"],
                "key_skills": training_metrics["key_skills"],
                "milestones": await self._define_expected_outcomes(course_recommendations),
                "progress_tracking": await self._setup_progress_tracking(course_recommendations),
                "status": "draft"
            }
            
            # Store training plan
            await self._store_training_plan(training_plan)
            
            return {
                "plan_id": plan_id,
                "learning_path": learning_path,
                "total_courses": len(course_recommendations),
                "estimated_duration": training_metrics["total_duration"],
                "estimated_cost": training_metrics["total_cost"],
                "key_skills": training_metrics["key_skills"],
                "milestones": training_plan["milestones"][:3]  # First 3 milestones
            }
            
        except Exception as e:
            logger.error(f"Training plan recommendation error: {str(e)}")
            raise

    async def assign_training(self, employee_id: str, course_ids: List[str], 
                            assigned_by: str, deadline: str = None) -> Dict[str, Any]:
        """Assign training courses to employee"""
        try:
            assignment_id = str(uuid.uuid4())
            
            # Get employee and course information
            employee_info = await self._get_employee_info(employee_id)
            courses_info = await self._get_courses_info(course_ids)
            
            # Validate course assignments
            validation_result = await self._validate_course_assignments(employee_id, course_ids)
            if not validation_result["valid"]:
                return {
                    "assignment_id": assignment_id,
                    "status": "failed",
                    "errors": validation_result["errors"]
                }
            
            # Calculate assignment details
            total_duration = sum(course.get("duration_hours", 0) for course in courses_info)
            estimated_completion = datetime.utcnow() + timedelta(days=total_duration // 2)  # Assuming 2 hours per day
            
            # Create training assignment
            training_assignment = {
                "id": assignment_id,
                "employee_id": employee_id,
                "employee_info": employee_info,
                "course_ids": course_ids,
                "courses_info": courses_info,
                "assigned_by": assigned_by,
                "assigned_at": datetime.utcnow().isoformat(),
                "deadline": deadline or estimated_completion.isoformat(),
                "status": "assigned",
                "progress": {
                    "courses_started": 0,
                    "courses_completed": 0,
                    "total_courses": len(course_ids),
                    "completion_percentage": 0.0,
                    "time_spent_hours": 0.0
                },
                "course_progress": {course_id: {"status": "not_started", "progress": 0.0} for course_id in course_ids}
            }
            
            # Store assignment
            await self._store_training_assignment(training_assignment)
            
            # Send assignment notification
            await self._send_training_assignment_notification(training_assignment)
            
            # Schedule progress check-ins
            await self._schedule_progress_checkins(training_assignment)
            
            return {
                "assignment_id": assignment_id,
                "status": "assigned",
                "total_courses": len(course_ids),
                "estimated_duration": f"{total_duration} hours",
                "deadline": training_assignment["deadline"],
                "courses": [{"id": c["id"], "title": c["title"]} for c in courses_info]
            }
            
        except Exception as e:
            logger.error(f"Training assignment error: {str(e)}")
            raise

    async def analyze_skill_gaps(self, employee_id: str) -> Dict[str, Any]:
        """Analyze skill gaps for an employee"""
        try:
            logger.info(f"Analyzing skill gaps for employee: {employee_id}")
            
            # Get employee data
            employee_data = await self._get_employee_data(employee_id)
            
            # Get current skills
            current_skills = await self._extract_current_skills(employee_data)
            
            # Get required skills for role
            required_skills = await self._get_required_skills(employee_data["position"])
            
            # Get career aspirations
            career_goals = await self._get_career_aspirations(employee_id)
            
            # Calculate skill gaps
            skill_gaps = await self._calculate_skill_gaps(current_skills, required_skills, career_goals)
            
            # Prioritize gaps
            prioritized_gaps = await self._prioritize_skill_gaps(skill_gaps, employee_data)
            
            # Generate recommendations
            recommendations = await self._generate_training_recommendations(prioritized_gaps)
            
            analysis_result = {
                "employee_id": employee_id,
                "analysis_date": datetime.utcnow().isoformat(),
                "current_skills": current_skills,
                "required_skills": required_skills,
                "skill_gaps": skill_gaps,
                "prioritized_gaps": prioritized_gaps,
                "recommendations": recommendations,
                "overall_skill_score": await self._calculate_overall_skill_score(current_skills, required_skills),
                "development_priority": await self._determine_development_priority(skill_gaps)
            }
            
            # Store analysis
            await self._store_skill_gap_analysis(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Skill gap analysis error: {str(e)}")
            raise

    async def create_personalized_learning_path(self, employee_id: str, skill_gaps: List[str], 
                                              timeline: int = 90) -> Dict[str, Any]:
        """Create personalized learning path"""
        try:
            logger.info(f"Creating learning path for employee: {employee_id}")
            
            # Get employee preferences
            preferences = await self._get_learning_preferences(employee_id)
            
            # Generate learning path
            learning_path = await self._generate_learning_path(skill_gaps, preferences, timeline)
            
            # Optimize path
            optimized_path = await self._optimize_learning_path(learning_path, preferences)
            
            # Create assignments
            assignments = await self._create_training_assignments(employee_id, optimized_path)
            
            learning_path_result = {
                "id": str(uuid.uuid4()),
                "employee_id": employee_id,
                "skill_gaps": skill_gaps,
                "timeline_days": timeline,
                "learning_path": optimized_path,
                "assignments": assignments,
                "estimated_cost": await self._calculate_learning_cost(optimized_path),
                "estimated_completion_time": await self._estimate_completion_time(optimized_path),
                "success_probability": await self._predict_success_probability(employee_id, optimized_path),
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Store learning path
            await self._store_learning_path(learning_path_result)
            
            # Send notifications
            await self._send_learning_path_notifications(learning_path_result)
            
            return learning_path_result
            
        except Exception as e:
            logger.error(f"Learning path creation error: {str(e)}")
            raise

    async def track_training_progress(self, assignment_id: str) -> Dict[str, Any]:
        """Track and analyze training progress"""
        try:
            # Get training assignment
            assignment = await self._get_training_assignment(assignment_id)
            if not assignment:
                raise ValueError("Training assignment not found")
            
            # Get latest progress data
            progress_data = await self.progress_tracker.get_progress_data(assignment_id)
            
            # Analyze progress patterns
            progress_analysis = await self._analyze_progress_patterns(progress_data)
            
            # Calculate completion predictions
            completion_prediction = await self._predict_completion_date(progress_analysis)
            
            # Identify learning challenges
            challenges = await self._identify_learning_challenges(progress_analysis)
            
            # Generate progress recommendations
            recommendations = await self._generate_progress_recommendations(progress_analysis, challenges)
            
            progress_report = {
                "assignment_id": assignment_id,
                "employee_id": assignment["employee_id"],
                "current_progress": progress_data.get("overall_progress", 0),
                "courses_completed": progress_data.get("courses_completed", 0),
                "total_courses": assignment["progress"]["total_courses"],
                "time_spent": progress_data.get("time_spent_hours", 0),
                "predicted_completion": completion_prediction,
                "on_track": progress_analysis.get("on_track", True),
                "challenges": challenges,
                "recommendations": recommendations,
                "learning_velocity": progress_analysis.get("learning_velocity", 0),
                "engagement_score": progress_analysis.get("engagement_score", 0),
                "last_activity": progress_data.get("last_activity_date")
            }
            
            # Update assignment progress
            await self._update_assignment_progress(assignment_id, progress_report)
            
            # Trigger interventions if needed
            if not progress_report["on_track"] or len(challenges) > 2:
                await self._trigger_learning_intervention(assignment_id, progress_report)
            
            return progress_report
            
        except Exception as e:
            logger.error(f"Training progress tracking error: {str(e)}")
            return {"error": str(e)}

    async def recommend_training_for_team(self, team_id: str) -> Dict[str, Any]:
        """Recommend training for entire team"""
        try:
            logger.info(f"Generating team training recommendations for: {team_id}")
            
            # Get team members
            team_members = await self._get_team_members(team_id)
            
            # Analyze team skill gaps
            team_analysis = await self._analyze_team_skills(team_members)
            
            # Identify common gaps
            common_gaps = await self._identify_common_skill_gaps(team_analysis)
            
            # Generate team training recommendations
            team_recommendations = await self._generate_team_training_recommendations(common_gaps, team_members)
            
            # Create team learning initiatives
            team_initiatives = await self._create_team_learning_initiatives(team_recommendations)
            
            team_training_plan = {
                "team_id": team_id,
                "team_size": len(team_members),
                "analysis_date": datetime.utcnow().isoformat(),
                "team_skill_analysis": team_analysis,
                "common_skill_gaps": common_gaps,
                "recommendations": team_recommendations,
                "learning_initiatives": team_initiatives,
                "estimated_budget": await self._calculate_team_training_budget(team_recommendations),
                "expected_roi": await self._calculate_training_roi(team_recommendations),
                "implementation_timeline": await self._create_implementation_timeline(team_initiatives)
            }
            
            # Store team training plan
            await self._store_team_training_plan(team_training_plan)
            
            return team_training_plan
            
        except Exception as e:
            logger.error(f"Team training recommendation error: {str(e)}")
            raise

    async def generate_training_analytics(self, time_period: str = "30d") -> Dict[str, Any]:
        """Generate comprehensive training analytics"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            if time_period == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_period == "30d":
                start_date = end_date - timedelta(days=30)
            elif time_period == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            analytics = {
                "period": time_period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "training_statistics": await self._calculate_training_statistics(start_date, end_date),
                "skill_development_trends": await self._analyze_skill_development_trends(start_date, end_date),
                "training_effectiveness": await self._measure_training_effectiveness(start_date, end_date),
                "cost_analysis": await self._analyze_training_costs(start_date, end_date),
                "completion_rates": await self._calculate_completion_rates(start_date, end_date),
                "skill_gap_trends": await self._analyze_skill_gap_trends(start_date, end_date),
                "roi_analysis": await self._calculate_training_roi_analysis(start_date, end_date),
                "recommendations": await self._generate_training_program_recommendations(),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Training analytics error: {str(e)}")
            return {"error": str(e)}

    # Helper methods
    async def _analyze_current_skills(self, skill_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current skill levels"""
        try:
            skills_by_category = {}
            
            for category, skills in self.training_categories.items():
                skills_by_category[category] = {}
                
                for skill_area, skill_list in skills.items():
                    skills_by_category[category][skill_area] = {}
                    
                    for skill in skill_list:
                        # Get skill level from assessment
                        skill_level = skill_assessment.get("skills", {}).get(skill, 0)
                        skills_by_category[category][skill_area][skill] = {
                            "level": skill_level,
                            "proficiency": await self._categorize_proficiency(skill_level),
                            "last_assessed": datetime.utcnow().isoformat()
                        }
            
            return skills_by_category
            
        except Exception as e:
            logger.error(f"Current skills analysis error: {str(e)}")
            return {}

    async def _identify_skill_gaps(self, employee_info: Dict[str, Any], 
                                 current_skills: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify skill gaps based on role requirements"""
        try:
            position = employee_info.get("position", "")
            department = employee_info.get("department", "")
            
            # Get required skills for position
            required_skills = await self._get_required_skills_for_position(position, department)
            
            skill_gaps = []
            
            for skill_name, required_level in required_skills.items():
                current_level = await self._get_current_skill_level(skill_name, current_skills)
                
                if current_level < required_level:
                    gap_severity = required_level - current_level
                    skill_gaps.append({
                        "skill": skill_name,
                        "current_level": current_level,
                        "required_level": required_level,
                        "gap_severity": gap_severity,
                        "priority": await self._calculate_skill_priority(skill_name, gap_severity),
                        "category": await self._get_skill_category(skill_name)
                    })
            
            # Sort by priority
            skill_gaps.sort(key=lambda x: x["priority"], reverse=True)
            
            return skill_gaps
            
        except Exception as e:
            logger.error(f"Skill gaps identification error: {str(e)}")
            return []

    async def _store_training_assignment(self, assignment: Dict[str, Any]):
        """Store training assignment in databases"""
        try:
            # Store in SQL
            db = SessionLocal()
            assignment_record = TrainingAssignment(
                id=assignment["id"],
                employee_id=assignment["employee_id"],
                assigned_by=assignment["assigned_by"],
                assigned_at=datetime.fromisoformat(assignment["assigned_at"]),
                deadline=datetime.fromisoformat(assignment["deadline"]) if assignment.get("deadline") else None,
                status=assignment["status"],
                completion_percentage=assignment["progress"]["completion_percentage"]
            )
            db.add(assignment_record)
            db.commit()
            db.close()
            
            # Store detailed data in MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.training_assignments.insert_one(assignment)
            
        except Exception as e:
            logger.error(f"Training assignment storage error: {str(e)}")
            if 'db' in locals():
                db.rollback()
                db.close()

    async def _automated_skill_gap_analysis(self):
        """Automated background skill gap analysis"""
        while True:
            try:
                # Get all active employees
                employees = await self._get_all_active_employees()
                
                for employee in employees:
                    # Check if analysis is due
                    last_analysis = await self._get_last_skill_analysis(employee["id"])
                    
                    if await self._is_analysis_due(last_analysis):
                        await self.analyze_skill_gaps(employee["id"])
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Automated skill gap analysis error: {str(e)}")
                await asyncio.sleep(3600)

    async def _automated_training_recommendations(self):
        """Automated training recommendations"""
        while True:
            try:
                # Get employees with skill gaps
                employees_with_gaps = await self._get_employees_with_skill_gaps()
                
                for employee_data in employees_with_gaps:
                    # Generate recommendations
                    recommendations = await self._generate_training_recommendations(
                        employee_data["skill_gaps"]
                    )
                    
                    # Create learning paths
                    if recommendations:
                        await self.create_personalized_learning_path(
                            employee_data["employee_id"],
                            [gap["skill"] for gap in employee_data["skill_gaps"][:5]]  # Top 5 gaps
                        )
                
                # Sleep for 12 hours
                await asyncio.sleep(43200)
                
            except Exception as e:
                logger.error(f"Automated training recommendations error: {str(e)}")
                await asyncio.sleep(3600)

    async def _automated_progress_tracking(self):
        """Automated progress tracking"""
        while True:
            try:
                # Get all active training assignments
                assignments = await self._get_all_active_assignments()
                
                for assignment in assignments:
                    # Track progress
                    await self.track_training_progress(assignment["id"])
                
                # Sleep for 6 hours
                await asyncio.sleep(21600)
                
            except Exception as e:
                logger.error(f"Automated progress tracking error: {str(e)}")
                await asyncio.sleep(3600)

    async def _load_training_catalog(self):
        """Load training catalog from database"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            self.training_catalog = await mongo_db.training_catalog.find().to_list(None)
            
        except Exception as e:
            logger.error(f"Training catalog loading error: {str(e)}")

    async def _build_learning_paths(self):
        """Build learning paths based on training catalog"""
        try:
            for category, skills in self.training_categories.items():
                for skill_area, skill_list in skills.items():
                    for skill in skill_list:
                        courses = [course for course in self.training_catalog if skill in course["skills"]]
                        self.learning_paths[skill] = courses
            
        except Exception as e:
            logger.error(f"Learning paths building error: {str(e)}")

    async def _get_employee_data(self, employee_id: str) -> Dict[str, Any]:
        """Retrieve employee data"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            employee_data = await mongo_db.employees.find_one({"id": employee_id})
            return employee_data
            
        except Exception as e:
            logger.error(f"Employee data retrieval error: {str(e)}")
            return {}

    async def _extract_current_skills(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract current skills from employee data"""
        try:
            skills = {
                "technical": [],
                "soft_skills": [],
                "business": [],
                "compliance": []
            }
            
            # Extract from resume/profile
            if "skills" in employee_data:
                for skill in employee_data["skills"]:
                    category = await self._categorize_skill(skill)
                    if category in skills:
                        skills[category].append({
                            "skill": skill,
                            "proficiency": employee_data.get("skill_levels", {}).get(skill, "intermediate"),
                            "last_used": employee_data.get("skill_usage", {}).get(skill, "recent")
                        })
            
            # Extract from performance reviews
            performance_skills = await self._extract_skills_from_performance(employee_data["id"])
            for category, skill_list in performance_skills.items():
                if category in skills:
                    skills[category].extend(skill_list)
            
            return skills
            
        except Exception as e:
            logger.error(f"Skill extraction error: {str(e)}")
            return {"technical": [], "soft_skills": [], "business": [], "compliance": []}

    async def _get_required_skills(self, position: str) -> Dict[str, Any]:
        """Get required skills for a position"""
        try:
            # This would typically come from job descriptions or role definitions
            position_skills = {
                "Software Engineer": {
                    "technical": ["Python", "JavaScript", "SQL", "Git", "Testing"],
                    "soft_skills": ["Problem Solving", "Communication", "Teamwork"],
                    "business": ["Agile Methodology"],
                    "compliance": ["Code Security", "Data Privacy"]
                },
                "Data Scientist": {
                    "technical": ["Python", "R", "SQL", "Machine Learning", "Statistics"],
                    "soft_skills": ["Analytical Thinking", "Communication", "Presentation"],
                    "business": ["Business Analysis", "ROI Analysis"],
                    "compliance": ["Data Privacy", "Statistical Ethics"]
                },
                "Product Manager": {
                    "technical": ["Analytics Tools", "SQL", "A/B Testing"],
                    "soft_skills": ["Leadership", "Communication", "Strategic Thinking"],
                    "business": ["Product Strategy", "Market Analysis", "Project Management"],
                    "compliance": ["Product Compliance", "User Privacy"]
                }
            }
            
            return position_skills.get(position, {
                "technical": [],
                "soft_skills": ["Communication", "Problem Solving"],
                "business": ["Time Management"],
                "compliance": ["Company Policies"]
            })
            
        except Exception as e:
            logger.error(f"Required skills retrieval error: {str(e)}")
            return {}

    async def _calculate_skill_gaps(self, current_skills: Dict[str, Any], 
                                  required_skills: Dict[str, Any], 
                                  career_goals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate skill gaps"""
        try:
            gaps = []
            
            for category, required_list in required_skills.items():
                current_list = [skill["skill"] for skill in current_skills.get(category, [])]
                
                for required_skill in required_list:
                    if required_skill not in current_list:
                        gaps.append({
                            "skill": required_skill,
                            "category": category,
                            "gap_type": "missing",
                            "priority": "high",
                            "reason": "Required for current role"
                        })
            
            # Add career goal gaps
            for category, goal_skills in career_goals.get("desired_skills", {}).items():
                current_list = [skill["skill"] for skill in current_skills.get(category, [])]
                
                for goal_skill in goal_skills:
                    if goal_skill not in current_list:
                        gaps.append({
                            "skill": goal_skill,
                            "category": category,
                            "gap_type": "career_development",
                            "priority": "medium",
                            "reason": "Career advancement"
                        })
            
            return gaps
            
        except Exception as e:
            logger.error(f"Skill gap calculation error: {str(e)}")
            return []

    async def _generate_training_recommendations(self, skill_gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate training recommendations for skill gaps"""
        try:
            recommendations = []
            
            for gap in skill_gaps:
                skill = gap["skill"]
                category = gap["category"]
                
                # Find relevant training courses
                courses = await self._find_training_courses(skill, category)
                
                # Select best course
                best_course = await self._select_best_course(courses, gap)
                
                if best_course:
                    recommendations.append({
                        "skill_gap": gap,
                        "recommended_course": best_course,
                        "estimated_duration": best_course.get("duration", "4 weeks"),
                        "estimated_cost": best_course.get("cost", 500),
                        "provider": best_course.get("provider", "internal"),
                        "delivery_method": best_course.get("delivery_method", "online"),
                        "priority_score": await self._calculate_recommendation_priority(gap, best_course)
                    })
            
            # Sort by priority
            recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Training recommendations error: {str(e)}")
            return []

    async def _store_skill_gap_analysis(self, analysis: Dict[str, Any]):
        """Store skill gap analysis"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.skill_gap_analyses.insert_one(analysis)
            
        except Exception as e:
            logger.error(f"Skill gap analysis storage error: {str(e)}")

    async def _store_learning_path(self, learning_path: Dict[str, Any]):
        """Store learning path"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.learning_paths.insert_one(learning_path)
            
        except Exception as e:
            logger.error(f"Learning path storage error: {str(e)}")

    async def _store_team_training_plan(self, team_training_plan: Dict[str, Any]):
        """Store team training plan"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.team_training_plans.insert_one(team_training_plan)
            
        except Exception as e:
            logger.error(f"Team training plan storage error: {str(e)}")

    async def _get_employee_info(self, employee_id: str) -> Dict[str, Any]:
        """Retrieve employee information from database"""
        try:
            db = SessionLocal()
            employee = db.query(Employee).filter(Employee.id == employee_id).first()
            db.close()
            return employee.__dict__ if employee else {}
            
        except Exception as e:
            logger.error(f"Employee info retrieval error: {str(e)}")
            return {}

    async def _get_courses_info(self, course_ids: List[str]) -> List[Dict[str, Any]]:
        """Retrieve course information from database"""
        try:
            db = SessionLocal()
            courses = db.query(TrainingCourse).filter(TrainingCourse.id.in_(course_ids)).all()
            db.close()
            return [course.__dict__ for course in courses]
            
        except Exception as e:
            logger.error(f"Courses info retrieval error: {str(e)}")
            return []

    async def _get_latest_assessment(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the latest skill assessment for an employee"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            latest_assessment = await mongo_db.skill_assessments.find_one({"employee_id": employee_id}, sort=[("conducted_at", -1)])
            return latest_assessment
            
        except Exception as e:
            logger.error(f"Latest assessment retrieval error: {str(e)}")
            return None

    async def _get_learning_preferences(self, employee_id: str) -> Dict[str, Any]:
        """Retrieve learning preferences for an employee"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            preferences = await mongo_db.learning_preferences.find_one({"employee_id": employee_id})
            return preferences if preferences else {}
            
        except Exception as e:
            logger.error(f"Learning preferences retrieval error: {str(e)}")
            return {}

    async def _determine_learning_path(self, employee_info: Dict[str, Any], career_goal: str) -> Dict[str, Any]:
        """Determine learning path based on employee info and career goal"""
        try:
            position = employee_info.get("position", "")
            department = employee_info.get("department", "")
            
            # Placeholder for determining learning path logic
            learning_path = {
                "position": position,
                "department": department,
                "career_goal": career_goal,
                "steps": []
            }
            
            return learning_path
            
        except Exception as e:
            logger.error(f"Learning path determination error: {str(e)}")
            return {}

    async def _create_training_schedule(self, course_recommendations: List[Dict[str, Any]], 
                                       time_commitment: str) -> Dict[str, Any]:
        """Create a training schedule based on recommendations and time commitment"""
        try:
            schedule = {
                "time_commitment": time_commitment,
                "courses": course_recommendations
            }
            
            return schedule
            
        except Exception as e:
            logger.error(f"Training schedule creation error: {str(e)}")
            return {}

    async def _calculate_training_metrics(self, course_recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metrics for training recommendations"""
        try:
            total_duration = sum(course.get("duration_hours", 0) for course in course_recommendations)
            total_cost = sum(course.get("cost", 0) for course in course_recommendations)
            key_skills = list(set(course["skills"] for course in course_recommendations))
            
            metrics = {
                "total_duration": total_duration,
                "total_cost": total_cost,
                "key_skills": key_skills
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Training metrics calculation error: {str(e)}")
            return {}

    async def _define_expected_outcomes(self, course_recommendations: List[Dict[str, Any]]) -> List[str]:
        """Define expected outcomes based on course recommendations"""
        try:
            outcomes = []
            for course in course_recommendations:
                outcomes.extend(course.get("outcomes", []))
            
            return outcomes
            
        except Exception as e:
            logger.error(f"Expected outcomes definition error: {str(e)}")
            return []

    async def _define_training_milestones(self, learning_path: Dict[str, Any], 
                                         course_recommendations: List[Dict[str, Any]]) -> List[str]:
        """Define training milestones based on learning path and course recommendations"""
        try:
            milestones = []
            for course in course_recommendations:
                milestones.extend(course.get("milestones", []))
            
            return milestones
            
        except Exception as e:
            logger.error(f"Training milestones definition error: {str(e)}")
            return []

    async def _setup_progress_tracking(self, course_recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Setup progress tracking for course recommendations"""
        try:
            tracking = {
                "courses": course_recommendations,
                "last_checked": datetime.utcnow().isoformat()
            }
            
            return tracking
            
        except Exception as e:
            logger.error(f"Progress tracking setup error: {str(e)}")
            return {}

    async def _store_skill_assessment(self, assessment_record: Dict[str, Any]):
        """Store skill assessment in database"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.skill_assessments.insert_one(assessment_record)
            
        except Exception as e:
            logger.error(f"Skill assessment storage error: {str(e)}")

    async def _store_training_plan(self, training_plan: Dict[str, Any]):
        """Store training plan in database"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.training_plans.insert_one(training_plan)
            
        except Exception as e:
            logger.error(f"Training plan storage error: {str(e)}")

    async def _send_training_assignment_notification(self, training_assignment: Dict[str, Any]):
        """Send notification for training assignment"""
        try:
            # Placeholder for sending notification logic
            logger.info(f"Notification sent for training assignment: {training_assignment['id']}")
            
        except Exception as e:
            logger.error(f"Notification sending error: {str(e)}")

    async def _schedule_progress_checkins(self, training_assignment: Dict[str, Any]):
        """Schedule progress check-ins for training assignment"""
        try:
            # Placeholder for scheduling check-ins logic
            logger.info(f"Progress check-ins scheduled for assignment: {training_assignment['id']}")
            
        except Exception as e:
            logger.error(f"Progress check-ins scheduling error: {str(e)}")

    async def _update_assignment_progress(self, assignment_id: str, progress_report: Dict[str, Any]):
        """Update training assignment progress in database"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.training_assignments.update_one({"id": assignment_id}, {"$set": progress_report})
            
        except Exception as e:
            logger.error(f"Assignment progress update error: {str(e)}")

    async def _trigger_learning_intervention(self, assignment_id: str, progress_report: Dict[str, Any]):
        """Trigger learning intervention if needed"""
        try:
            # Placeholder for triggering intervention logic
            logger.info(f"Learning intervention triggered for assignment: {assignment_id}")
            
        except Exception as e:
            logger.error(f"Learning intervention triggering error: {str(e)}")

    async def _get_all_active_employees(self) -> List[Dict[str, Any]]:
        """Retrieve all active employees"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            active_employees = await mongo_db.employees.find({"status": "active"}).to_list(None)
            return active_employees
            
        except Exception as e:
            logger.error(f"Active employees retrieval error: {str(e)}")
            return []

    async def _get_last_skill_analysis(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the last skill analysis for an employee"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            last_analysis = await mongo_db.skill_gap_analyses.find_one({"employee_id": employee_id}, sort=[("analysis_date", -1)])
            return last_analysis
            
        except Exception as e:
            logger.error(f"Last skill analysis retrieval error: {str(e)}")
            return None

    async def _is_analysis_due(self, last_analysis: Optional[Dict[str, Any]]) -> bool:
        """Check if skill gap analysis is due"""
        try:
            if last_analysis:
                last_date = datetime.fromisoformat(last_analysis["analysis_date"])
                due_date = last_date + timedelta(days=180)
                return datetime.utcnow() > due_date
            return True
            
        except Exception as e:
            logger.error(f"Analysis due check error: {str(e)}")
            return False

    async def _get_employees_with_skill_gaps(self) -> List[Dict[str, Any]]:
        """Retrieve employees with identified skill gaps"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            employees_with_gaps = await mongo_db.skill_gap_analyses.find({"skill_gaps": {"$exists": True, "$ne": []}}).to_list(None)
            return employees_with_gaps
            
        except Exception as e:
            logger.error(f"Employees with skill gaps retrieval error: {str(e)}")
            return []

    async def _get_team_members(self, team_id: str) -> List[Dict[str, Any]]:
        """Retrieve team members"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            team_members = await mongo_db.teams.find_one({"id": team_id}, {"members": 1})
            return team_members.get("members", []) if team_members else []
            
        except Exception as e:
            logger.error(f"Team members retrieval error: {str(e)}")
            return []

    async def _analyze_team_skills(self, team_members: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze skills for a team of employees"""
        try:
            team_skills = {}
            for member in team_members:
                member_skills = await self._extract_current_skills(member)
                for category, skills in member_skills.items():
                    if category not in team_skills:
                        team_skills[category] = {}
                    for skill_area, skill_list in skills.items():
                        if skill_area not in team_skills[category]:
                            team_skills[category][skill_area] = []
                        team_skills[category][skill_area].extend(skill_list)
            
            return team_skills
            
        except Exception as e:
            logger.error(f"Team skills analysis error: {str(e)}")
            return {}

    async def _identify_common_skill_gaps(self, team_analysis: Dict[str, Any]) -> List[str]:
        """Identify common skill gaps in a team"""
        try:
            common_gaps = []
            for category, skills in team_analysis.items():
                for skill_area, skill_list in skills.items():
                    for skill in skill_list:
                        if skill["gap_severity"] > 0:
                            common_gaps.append(skill["skill"])
            
            return list(set(common_gaps))
            
        except Exception as e:
            logger.error(f"Common skill gaps identification error: {str(e)}")
            return []

    async def _generate_team_training_recommendations(self, common_gaps: List[str], 
                                                    team_members: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate training recommendations for a team"""
        try:
            recommendations = []
            for gap in common_gaps:
                courses = await self._find_training_courses(gap, await self._categorize_skill(gap))
                best_course = await self._select_best_course(courses, {"skill": gap})
                if best_course:
                    recommendations.append({
                        "skill_gap": gap,
                        "recommended_course": best_course,
                        "estimated_duration": best_course.get("duration", "4 weeks"),
                        "estimated_cost": best_course.get("cost", 500),
                        "provider": best_course.get("provider", "internal"),
                        "delivery_method": best_course.get("delivery_method", "online"),
                        "priority_score": await self._calculate_recommendation_priority({"skill": gap}, best_course)
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Team training recommendations error: {str(e)}")
            return []

    async def _create_team_learning_initiatives(self, team_recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create learning initiatives for a team"""
        try:
            initiatives = []
            for recommendation in team_recommendations:
                initiatives.append({
                    "course": recommendation["recommended_course"],
                    "employees": await self._get_team_members_for_course(recommendation["recommended_course"]["id"])
                })
            
            return initiatives
            
        except Exception as e:
            logger.error(f"Team learning initiatives creation error: {str(e)}")
            return []

    async def _get_team_members_for_course(self, course_id: str) -> List[str]:
        """Retrieve team members who need a specific course"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            members = await mongo_db.team_training_plans.find_one({"assignments.course_ids": course_id}, {"employees": 1})
            return members.get("employees", []) if members else []
            
        except Exception as e:
            logger.error(f"Team members for course retrieval error: {str(e)}")
            return []

    async def _calculate_team_training_budget(self, team_recommendations: List[Dict[str, Any]]) -> float:
        """Calculate the estimated budget for team training"""
        try:
            total_cost = sum(recommendation["estimated_cost"] for recommendation in team_recommendations)
            return total_cost
            
        except Exception as e:
            logger.error(f"Team training budget calculation error: {str(e)}")
            return 0.0

    async def _calculate_training_roi(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate the return on investment for training recommendations"""
        try:
            total_cost = sum(recommendation["estimated_cost"] for recommendation in recommendations)
            # Placeholder for ROI calculation logic
            roi = total_cost * 0.1  # Example calculation
            return roi
            
        except Exception as e:
            logger.error(f"Training ROI calculation error: {str(e)}")
            return 0.0

    async def _create_implementation_timeline(self, team_initiatives: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create an implementation timeline for team learning initiatives"""
        try:
            timeline = {
                "initiatives": team_initiatives,
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=90)).isoformat()
            }
            
            return timeline
            
        except Exception as e:
            logger.error(f"Implementation timeline creation error: {str(e)}")
            return {}

    async def _calculate_training_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate training statistics for a given time period"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            assignments = await mongo_db.training_assignments.find({
                "assigned_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }).to_list(None)
            
            total_assignments = len(assignments)
            completed_assignments = sum(1 for assignment in assignments if assignment["status"] == "completed")
            completion_rate = (completed_assignments / total_assignments) * 100 if total_assignments > 0 else 0
            
            return {
                "total_assignments": total_assignments,
                "completed_assignments": completed_assignments,
                "completion_rate": completion_rate
            }
            
        except Exception as e:
            logger.error(f"Training statistics calculation error: {str(e)}")
            return {}

    async def _analyze_skill_development_trends(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze skill development trends for a given time period"""
        try:
            # Placeholder for skill development trends analysis logic
            trends = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "trends": {}
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Skill development trends analysis error: {str(e)}")
            return {}

    async def _measure_training_effectiveness(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Measure the effectiveness of training programs for a given time period"""
        try:
            # Placeholder for training effectiveness measurement logic
            effectiveness = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "effectiveness": {}
            }
            
            return effectiveness
            
        except Exception as e:
            logger.error(f"Training effectiveness measurement error: {str(e)}")
            return {}

    async def _analyze_training_costs(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze training costs for a given time period"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            assignments = await mongo_db.training_assignments.find({
                "assigned_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }).to_list(None)
            
            total_cost = sum(assignment["estimated_cost"] for assignment in assignments)
            
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_cost": total_cost
            }
            
        except Exception as e:
            logger.error(f"Training costs analysis error: {str(e)}")
            return {}

    async def _calculate_completion_rates(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate completion rates for training assignments in a given time period"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            assignments = await mongo_db.training_assignments.find({
                "assigned_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }).to_list(None)
            
            total_assignments = len(assignments)
            completed_assignments = sum(1 for assignment in assignments if assignment["status"] == "completed")
            completion_rate = (completed_assignments / total_assignments) * 100 if total_assignments > 0 else 0
            
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "completion_rate": completion_rate
            }
            
        except Exception as e:
            logger.error(f"Completion rates calculation error: {str(e)}")
            return {}

    async def _analyze_skill_gap_trends(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze skill gap trends for a given time period"""
        try:
            # Placeholder for skill gap trends analysis logic
            trends = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "trends": {}
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Skill gap trends analysis error: {str(e)}")
            return {}

    async def _calculate_training_roi_analysis(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate ROI analysis for training programs in a given time period"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            assignments = await mongo_db.training_assignments.find({
                "assigned_at": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }).to_list(None)
            
            total_cost = sum(assignment["estimated_cost"] for assignment in assignments)
            total_roi = sum(assignment["expected_outcomes"]["roi"] for assignment in assignments)
            
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_cost": total_cost,
                "total_roi": total_roi
            }
            
        except Exception as e:
            logger.error(f"Training ROI analysis error: {str(e)}")
            return {}

    async def _generate_training_program_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations for training programs"""
        try:
            # Placeholder for training program recommendations logic
            recommendations = []
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Training program recommendations error: {str(e)}")
            return []

    async def _get_all_active_assignments(self) -> List[Dict[str, Any]]:
        """Retrieve all active training assignments"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            active_assignments = await mongo_db.training_assignments.find({"status": "assigned"}).to_list(None)
            return active_assignments
            
        except Exception as e:
            logger.error(f"Active assignments retrieval error: {str(e)}")
            return []

    async def _collect_progress_data(self, assignment: Dict[str, Any]) -> Dict[str, Any]:
        """Collect progress data for a training assignment"""
        try:
            # Placeholder for collecting progress data logic
            progress_data = {
                "overall_progress": 0,
                "courses_completed": 0,
                "time_spent_hours": 0,
                "last_activity_date": datetime.utcnow().isoformat()
            }
            
            return progress_data
            
        except Exception as e:
            logger.error(f"Progress data collection error: {str(e)}")
            return {}

    async def _analyze_training_progress(self, progress_data: Dict[str, Any], 
                                         assignment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze training progress"""
        try:
            # Placeholder for analyzing training progress logic
            analysis = {
                "completion_percentage": progress_data["overall_progress"],
                "status": "on_track" if progress_data["overall_progress"] >= 50 else "at_risk",
                "issues": []
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Training progress analysis error: {str(e)}")
            return {}

    async def _handle_training_completion(self, assignment: Dict[str, Any]):
        """Handle training completion"""
        try:
            # Placeholder for handling training completion logic
            logger.info(f"Training completed for assignment: {assignment['id']}")
            
        except Exception as e:
            logger.error(f"Training completion handling error: {str(e)}")

    async def _handle_training_issues(self, assignment: Dict[str, Any], issues: List[str]):
        """Handle training issues"""
        try:
            # Placeholder for handling training issues logic
            logger.info(f"Issues identified for assignment: {assignment['id']}, Issues: {issues}")
            
        except Exception as e:
            logger.error(f"Training issues handling error: {str(e)}")

    async def _update_training_assignment(self, assignment: Dict[str, Any]):
        """Update training assignment in database"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.training_assignments.update_one({"id": assignment["id"]}, {"$set": assignment})
            
        except Exception as e:
            logger.error(f"Training assignment update error: {str(e)}")

    async def _categorize_skill(self, skill: str) -> str:
        """Categorize a skill"""
        try:
            for category, skills in self.training_categories.items():
                for skill_area, skill_list in skills.items():
                    if skill in skill_list:
                        return category
            return "unknown"
            
        except Exception as e:
            logger.error(f"Skill categorization error: {str(e)}")
            return "unknown"

    async def _extract_skills_from_performance(self, employee_id: str) -> Dict[str, Any]:
        """Extract skills from performance reviews"""
        try:
            # Placeholder for extracting skills from performance reviews logic
            skills = {
                "technical": [],
                "soft_skills": [],
                "business": [],
                "compliance": []
            }
            
            return skills
            
        except Exception as e:
            logger.error(f"Skills extraction from performance error: {str(e)}")
            return {}

    async def _get_current_skill_level(self, skill_name: str, current_skills: Dict[str, Any]) -> int:
        """Get the current skill level for a skill"""
        try:
            for category, skills in current_skills.items():
                for skill_area, skill_list in skills.items():
                    for skill in skill_list:
                        if skill["skill"] == skill_name:
                            return skill["level"]
            return 0
            
        except Exception as e:
            logger.error(f"Current skill level retrieval error: {str(e)}")
            return 0

    async def _calculate_skill_priority(self, skill_name: str, gap_severity: int) -> int:
        """Calculate the priority of a skill gap"""
        try:
            # Placeholder for calculating skill priority logic
            priority = gap_severity * 2  # Example calculation
            return priority
            
        except Exception as e:
            logger.error(f"Skill priority calculation error: {str(e)}")
            return 0

    async def _get_skill_category(self, skill_name: str) -> str:
        """Get the category of a skill"""
        try:
            for category, skills in self.training_categories.items():
                for skill_area, skill_list in skills.items():
                    if skill_name in skill_list:
                        return category
            return "unknown"
            
        except Exception as e:
            logger.error(f"Skill category retrieval error: {str(e)}")
            return "unknown"

    async def _find_training_courses(self, skill: str, category: str) -> List[Dict[str, Any]]:
        """Find training courses for a skill and category"""
        try:
            courses = [course for course in self.training_catalog if skill in course["skills"] and category in course["categories"]]
            return courses
            
        except Exception as e:
            logger.error(f"Training courses finding error: {str(e)}")
            return []

    async def _select_best_course(self, courses: List[Dict[str, Any]], gap: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Select the best course for a skill gap"""
        try:
            if courses:
                # Placeholder for selecting best course logic
                return courses[0]
            return None
            
        except Exception as e:
            logger.error(f"Best course selection error: {str(e)}")
            return None

    async def _calculate_recommendation_priority(self, gap: Dict[str, Any], course: Dict[str, Any]) -> int:
        """Calculate the priority of a training recommendation"""
        try:
            # Placeholder for calculating recommendation priority logic
            priority = gap["gap_severity"] * 2 + course["quality_score"] * 10  # Example calculation
            return priority
            
        except Exception as e:
            logger.error(f"Recommendation priority calculation error: {str(e)}")
            return 0

    async def _categorize_proficiency(self, skill_level: int) -> str:
        """Categorize skill proficiency level"""
        try:
            if skill_level >= 80:
                return "expert"
            elif skill_level >= 50:
                return "intermediate"
            else:
                return "beginner"
            
        except Exception as e:
            logger.error(f"Proficiency categorization error: {str(e)}")
            return "unknown"

    async def _identify_strengths(self, current_skills: Dict[str, Any]) -> List[str]:
        """Identify strengths based on current skills"""
        try:
            strengths = []
            for category, skills in current_skills.items():
                for skill_area, skill_list in skills.items():
                    for skill in skill_list:
                        if skill["proficiency"] == "expert":
                            strengths.append(skill["skill"])
            
            return strengths
            
        except Exception as e:
            logger.error(f"Strengths identification error: {str(e)}")
            return []

    async def _identify_development_areas(self, skill_gaps: List[Dict[str, Any]]) -> List[str]:
        """Identify development areas based on skill gaps"""
        try:
            development_areas = []
            for gap in skill_gaps:
                development_areas.append(gap["skill"])
            
            return development_areas
            
        except Exception as e:
            logger.error(f"Development areas identification error: {str(e)}")
            return []

    async def _calculate_overall_score(self, current_skills: Dict[str, Any]) -> float:
        """Calculate overall skill score"""
        try:
            total_score = 0
            total_skills = 0
            
            for category, skills in current_skills.items():
                for skill_area, skill_list in skills.items():
                    for skill in skill_list:
                        total_score += skill["level"]
                        total_skills += 1
            
            overall_score = total_score / total_skills if total_skills > 0 else 0
            return overall_score
            
        except Exception as e:
            logger.error(f"Overall score calculation error: {str(e)}")
            return 0.0

    async def _calculate_overall_skill_score(self, current_skills: Dict[str, Any], required_skills: Dict[str, Any]) -> float:
        """Calculate overall skill score for an employee"""
        try:
            total_score = 0
            total_required_skills = 0
            
            for category, skills in required_skills.items():
                for required_skill in skills:
                    current_level = await self._get_current_skill_level(required_skill, current_skills)
                    total_score += current_level
                    total_required_skills += 1
            
            overall_skill_score = total_score / total_required_skills if total_required_skills > 0 else 0
            return overall_skill_score
            
        except Exception as e:
            logger.error(f"Overall skill score calculation error: {str(e)}")
            return 0.0

    async def _determine_development_priority(self, skill_gaps: List[Dict[str, Any]]) -> str:
        """Determine development priority based on skill gaps"""
        try:
            # Placeholder for determining development priority logic
            priority = "high" if any(gap["priority"] == "high" for gap in skill_gaps) else "medium"
            return priority
            
        except Exception as e:
            logger.error(f"Development priority determination error: {str(e)}")
            return "unknown"

    async def _get_career_aspirations(self, employee_id: str) -> Dict[str, Any]:
        """Retrieve career aspirations for an employee"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            aspirations = await mongo_db.career_aspirations.find_one({"employee_id": employee_id})
            return aspirations if aspirations else {}
            
        except Exception as e:
            logger.error(f"Career aspirations retrieval error: {str(e)}")
            return {}

    async def _get_required_skills_for_position(self, position: str, department: str) -> Dict[str, Any]:
        """Retrieve required skills for a position and department"""
        try:
            # Placeholder for retrieving required skills logic
            required_skills = {
                "technical": [],
                "soft_skills": [],
                "business": [],
                "compliance": []
            }
            
            return required_skills
            
        except Exception as e:
            logger.error(f"Required skills for position retrieval error: {str(e)}")
            return {}

    async def _get_popular_courses(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Retrieve popular courses based on training assignments"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            pipeline = [
                {
                    "$match": {
                        "assigned_at": {
                            "$gte": start_date.isoformat(),
                            "$lte": end_date.isoformat()
                        }
                    }
                },
                {
                    "$unwind": "$course_ids"
                },
                {
                    "$group": {
                        "_id": "$course_ids",
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"count": -1}
                },
                {
                    "$limit": 5
                }
            ]
            
            popular_courses = await mongo_db.training_assignments.aggregate(pipeline).to_list(None)
            return popular_courses
            
        except Exception as e:
            logger.error(f"Popular courses retrieval error: {str(e)}")
            return []

    async def _predict_success_probability(self, employee_id: str, learning_path: Dict[str, Any]) -> float:
        """Predict success probability for a learning path"""
        try:
            # Placeholder for predicting success probability logic
            probability = 0.8  # Example calculation
            return probability
            
        except Exception as e:
            logger.error(f"Success probability prediction error: {str(e)}")
            return 0.0

    async def _validate_course_assignments(self, employee_id: str, course_ids: List[str]) -> Dict[str, Any]:
        """Validate course assignments for an employee"""
        try:
            # Placeholder for validating course assignments logic
            validation_result = {
                "valid": True,
                "errors": []
            }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Course assignments validation error: {str(e)}")
            return {"valid": False, "errors": [str(e)]}
