"""
Performance Agent - Automated performance review and management
Handles 360-degree feedback, goal tracking, and performance analytics
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import openai
from datetime import datetime, timedelta
import json
import uuid
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

from ..base_agent import BaseAgent
from .feedback_collector import FeedbackCollector
from .goal_tracker import GoalTracker
from .performance_analyzer import PerformanceAnalyzer
from backend.database.mongo_database import get_mongo_client
from backend.database.sql_database import SessionLocal
from models.sql_models import Employee, PerformanceReview, Goal
from backend.utils.config import settings

logger = logging.getLogger(__name__)

class PerformanceAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "performance_agent"
        self.feedback_collector = FeedbackCollector()
        self.goal_tracker = GoalTracker()
        self.performance_analyzer = PerformanceAnalyzer()
        
        # Performance review cycles
        self.review_cycles = {
            "quarterly": {"frequency": 90, "type": "comprehensive"},
            "monthly": {"frequency": 30, "type": "check_in"},
            "annual": {"frequency": 365, "type": "annual_review"},
            "probation": {"frequency": 90, "type": "probation_review"}
        }
        
        # Performance metrics
        self.performance_metrics = {
            "technical_skills": {"weight": 0.3, "categories": ["coding", "architecture", "problem_solving"]},
            "soft_skills": {"weight": 0.25, "categories": ["communication", "teamwork", "leadership"]},
            "goal_achievement": {"weight": 0.25, "categories": ["project_delivery", "kpi_achievement"]},
            "cultural_fit": {"weight": 0.2, "categories": ["values_alignment", "collaboration", "innovation"]}
        }

    async def initialize(self):
        """Initialize performance agent components"""
        try:
            logger.info("Initializing Performance Agent...")
            
            await super().initialize()
            
            # Initialize sub-components
            await self.feedback_collector.initialize()
            await self.goal_tracker.initialize()
            await self.performance_analyzer.initialize()
            
            self.is_initialized = True
            logger.info("Performance Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Performance Agent: {str(e)}")
            raise

    async def start_performance_review(self, employee_id: str, review_type: str = "quarterly", 
                                     reviewer_id: str = None) -> Dict[str, Any]:
        """Start automated performance review process"""
        try:
            review_id = str(uuid.uuid4())
            
            # Get employee information
            employee_info = await self._get_employee_info(employee_id)
            
            # Initialize review data
            review_data = {
                "id": review_id,
                "employee_id": employee_id,
                "reviewer_id": reviewer_id or "ai_system",
                "review_type": review_type,
                "status": "in_progress",
                "started_at": datetime.utcnow().isoformat(),
                "review_period": await self._calculate_review_period(review_type),
                "employee_info": employee_info,
                "feedback_collection": {
                    "self_assessment": None,
                    "manager_feedback": None,
                    "peer_feedback": [],
                    "subordinate_feedback": [],
                    "360_feedback_complete": False
                },
                "goal_evaluation": {},
                "performance_analysis": {},
                "final_rating": 0.0,
                "recommendations": [],
                "development_plan": {}
            }
            
            # Start feedback collection process
            feedback_process = await self.feedback_collector.start_collection_process(
                employee_id=employee_id,
                review_id=review_id,
                review_type=review_type
            )
            
            review_data["feedback_collection"]["process_id"] = feedback_process["process_id"]
            
            # Store review data
            await self._store_review_data(review_data)
            
            # Schedule automated follow-ups
            await self._schedule_review_reminders(review_data)
            
            return {
                "review_id": review_id,
                "status": "started",
                "feedback_process": feedback_process,
                "estimated_completion": await self._estimate_completion_date(review_type),
                "next_steps": await self._get_next_steps(review_data)
            }
            
        except Exception as e:
            logger.error(f"Performance review start error: {str(e)}")
            raise

    async def process_feedback_submission(self, review_id: str, feedback_type: str, 
                                        feedback_data: Dict[str, Any], submitter_id: str) -> Dict[str, Any]:
        """Process submitted feedback"""
        try:
            # Get review data
            review_data = await self._get_review_data(review_id)
            if not review_data:
                raise ValueError("Review not found")
            
            # Validate and process feedback
            processed_feedback = await self.feedback_collector.process_feedback(
                feedback_type=feedback_type,
                feedback_data=feedback_data,
                submitter_id=submitter_id,
                review_context=review_data
            )
            
            # Update review data
            if feedback_type == "self_assessment":
                review_data["feedback_collection"]["self_assessment"] = processed_feedback
            elif feedback_type == "manager_feedback":
                review_data["feedback_collection"]["manager_feedback"] = processed_feedback
            elif feedback_type == "peer_feedback":
                review_data["feedback_collection"]["peer_feedback"].append(processed_feedback)
            elif feedback_type == "subordinate_feedback":
                review_data["feedback_collection"]["subordinate_feedback"].append(processed_feedback)
            
            # Check if 360 feedback is complete
            review_data["feedback_collection"]["360_feedback_complete"] = await self._check_feedback_completeness(review_data)
            
            # If feedback collection is complete, start analysis
            if review_data["feedback_collection"]["360_feedback_complete"]:
                await self._trigger_performance_analysis(review_data)
            
            # Update review data
            await self._update_review_data(review_data)
            
            return {
                "status": "feedback_processed",
                "feedback_type": feedback_type,
                "feedback_complete": review_data["feedback_collection"]["360_feedback_complete"],
                "next_steps": await self._get_next_steps(review_data)
            }
            
        except Exception as e:
            logger.error(f"Feedback processing error: {str(e)}")
            raise

    async def _trigger_performance_analysis(self, review_data: Dict[str, Any]):
        """Trigger comprehensive performance analysis"""
        try:
            employee_id = review_data["employee_id"]
            review_period = review_data["review_period"]
            
            # Analyze goal achievement
            goal_analysis = await self.goal_tracker.analyze_goal_achievement(
                employee_id=employee_id,
                period_start=review_period["start"],
                period_end=review_period["end"]
            )
            review_data["goal_evaluation"] = goal_analysis
            
            # Perform comprehensive performance analysis
            performance_analysis = await self.performance_analyzer.analyze_performance(
                employee_id=employee_id,
                feedback_data=review_data["feedback_collection"],
                goal_data=goal_analysis,
                review_period=review_period
            )
            review_data["performance_analysis"] = performance_analysis
            
            # Calculate final rating
            final_rating = await self._calculate_final_rating(review_data)
            review_data["final_rating"] = final_rating
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(review_data)
            review_data["recommendations"] = recommendations
            
            # Create development plan
            development_plan = await self._create_development_plan(review_data)
            review_data["development_plan"] = development_plan
            
            # Update status
            review_data["status"] = "analysis_complete"
            review_data["completed_at"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"Performance analysis trigger error: {str(e)}")
            raise

    async def _calculate_final_rating(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final performance rating"""
        try:
            performance_analysis = review_data.get("performance_analysis", {})
            goal_evaluation = review_data.get("goal_evaluation", {})
            
            # Get individual scores
            scores = {
                "technical_skills": performance_analysis.get("technical_score", 0),
                "soft_skills": performance_analysis.get("soft_skills_score", 0),
                "goal_achievement": goal_evaluation.get("overall_achievement_score", 0),
                "cultural_fit": performance_analysis.get("cultural_fit_score", 0)
            }
            
            # Calculate weighted score
            weights = {metric: data["weight"] for metric, data in self.performance_metrics.items()}
            
            weighted_score = sum(scores[metric] * weights[metric] for metric in scores.keys())
            
            # Determine rating category
            rating_category = self._categorize_rating(weighted_score)
            
            # Generate rating explanation
            rating_explanation = await self._generate_rating_explanation(scores, weighted_score, rating_category)
            
            return {
                "overall_score": weighted_score,
                "rating_category": rating_category,
                "individual_scores": scores,
                "weights_applied": weights,
                "explanation": rating_explanation,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Final rating calculation error: {str(e)}")
            return {"overall_score": 0.0, "rating_category": "needs_review"}

    def _categorize_rating(self, score: float) -> str:
        """Categorize performance rating"""
        if score >= 90:
            return "exceptional"
        elif score >= 80:
            return "exceeds_expectations"
        elif score >= 70:
            return "meets_expectations"
        elif score >= 60:
            return "below_expectations"
        else:
            return "needs_improvement"

    async def _generate_rating_explanation(self, scores: Dict[str, float], overall_score: float, 
                                         rating_category: str) -> str:
        """Generate AI-powered rating explanation"""
        try:
            prompt = f"""
            Generate a professional performance rating explanation:
            
            Overall Score: {overall_score:.1f}/100
            Rating Category: {rating_category.replace('_', ' ').title()}
            
            Individual Scores:
            - Technical Skills: {scores.get('technical_skills', 0):.1f}/100
            - Soft Skills: {scores.get('soft_skills', 0):.1f}/100
            - Goal Achievement: {scores.get('goal_achievement', 0):.1f}/100
            - Cultural Fit: {scores.get('cultural_fit', 0):.1f}/100
            
            Provide a constructive explanation that:
            1. Summarizes overall performance
            2. Highlights key strengths
            3. Identifies areas for development
            4. Maintains a professional, encouraging tone
            
            Keep it concise (150-200 words).
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert HR professional providing performance evaluations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Rating explanation generation error: {str(e)}")
            return f"Performance rating of {overall_score:.1f}/100 ({rating_category.replace('_', ' ')}) based on comprehensive evaluation."

    async def _generate_recommendations(self, review_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance improvement recommendations"""
        try:
            performance_analysis = review_data.get("performance_analysis", {})
            goal_evaluation = review_data.get("goal_evaluation", {})
            final_rating = review_data.get("final_rating", {})
            
            recommendations = []
            
            # Analyze each performance area
            individual_scores = final_rating.get("individual_scores", {})
            
            for area, score in individual_scores.items():
                if score < 70:  # Below expectations
                    recommendation = await self._generate_area_recommendation(area, score, performance_analysis)
                    recommendations.append(recommendation)
                elif score >= 85:  # High performance
                    recognition = await self._generate_recognition(area, score, performance_analysis)
                    recommendations.append(recognition)
            
            # Add goal-specific recommendations
            if goal_evaluation.get("missed_goals"):
                goal_recommendations = await self._generate_goal_recommendations(goal_evaluation)
                recommendations.extend(goal_recommendations)
            
            # Add career development recommendations
            career_recommendations = await self._generate_career_recommendations(review_data)
            recommendations.extend(career_recommendations)
            
            return recommendations[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            logger.error(f"Recommendations generation error: {str(e)}")
            return []

    async def _generate_area_recommendation(self, area: str, score: float, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendation for specific performance area"""
        try:
            area_recommendations = {
                "technical_skills": {
                    "type": "skill_development",
                    "priority": "high",
                    "actions": [
                        "Enroll in advanced technical training courses",
                        "Participate in code review sessions",
                        "Work on challenging technical projects",
                        "Seek mentorship from senior developers"
                    ]
                },
                "soft_skills": {
                    "type": "communication_improvement",
                    "priority": "medium",
                    "actions": [
                        "Attend communication workshops",
                        "Practice presentation skills",
                        "Join cross-functional projects",
                        "Seek feedback on communication style"
                    ]
                },
                "goal_achievement": {
                    "type": "goal_management",
                    "priority": "high",
                    "actions": [
                        "Improve project planning and time management",
                        "Set more realistic and measurable goals",
                        "Regular check-ins with manager",
                        "Use project management tools effectively"
                    ]
                },
                "cultural_fit": {
                    "type": "cultural_alignment",
                    "priority": "medium",
                    "actions": [
                        "Participate in company culture initiatives",
                        "Engage more in team activities",
                        "Understand and embody company values",
                        "Seek feedback on cultural alignment"
                    ]
                }
            }
            
            base_recommendation = area_recommendations.get(area, {
                "type": "general_improvement",
                "priority": "medium",
                "actions": [f"Focus on improving {area.replace('_', ' ')}"]
            })
            
            return {
                "id": str(uuid.uuid4()),
                "area": area,
                "current_score": score,
                "type": base_recommendation["type"],
                "priority": base_recommendation["priority"],
                "title": f"Improve {area.replace('_', ' ').title()}",
                "description": f"Current score of {score:.1f} indicates need for development in {area.replace('_', ' ')}",
                "recommended_actions": base_recommendation["actions"],
                "timeline": "3-6 months",
                "success_metrics": [f"Achieve score of 75+ in {area.replace('_', ' ')}"],
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Area recommendation generation error: {str(e)}")
            return {}

    async def _generate_recognition(self, area: str, score: float, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recognition for high performance areas"""
        try:
            return {
                "id": str(uuid.uuid4()),
                "area": area,
                "current_score": score,
                "type": "recognition",
                "priority": "low",
                "title": f"Excellent {area.replace('_', ' ').title()} Performance",
                "description": f"Outstanding score of {score:.1f} demonstrates excellence in {area.replace('_', ' ')}",
                "recommended_actions": [
                    f"Continue maintaining high standards in {area.replace('_', ' ')}",
                    "Consider mentoring others in this area",
                    "Share best practices with the team",
                    "Take on leadership roles leveraging this strength"
                ],
                "timeline": "ongoing",
                "success_metrics": ["Maintain current performance level", "Help others improve in this area"],
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Recognition generation error: {str(e)}")
            return {}

    async def _create_development_plan(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized development plan"""
        try:
            recommendations = review_data.get("recommendations", [])
            employee_info = review_data.get("employee_info", {})
            
            # Categorize recommendations by timeline
            short_term = []  # 0-3 months
            medium_term = []  # 3-6 months
            long_term = []  # 6+ months
            
            for rec in recommendations:
                timeline = rec.get("timeline", "3-6 months")
                if "0-3" in timeline or "immediate" in timeline:
                    short_term.append(rec)
                elif "6+" in timeline or "long" in timeline:
                    long_term.append(rec)
                else:
                    medium_term.append(rec)
            
            # Generate learning resources
            learning_resources = await self._generate_learning_resources(recommendations)
            
            # Create development goals
            development_goals = await self._create_development_goals(recommendations)
            
            development_plan = {
                "id": str(uuid.uuid4()),
                "employee_id": review_data["employee_id"],
                "created_at": datetime.utcnow().isoformat(),
                "review_period": review_data.get("review_period", {}),
                "development_timeline": {
                    "short_term": short_term,
                    "medium_term": medium_term,
                    "long_term": long_term
                },
                "learning_resources": learning_resources,
                "development_goals": development_goals,
                "success_metrics": await self._define_success_metrics(recommendations),
                "check_in_schedule": await self._create_checkin_schedule(),
                "budget_estimate": await self._estimate_development_budget(learning_resources),
                "manager_support_needed": await self._identify_manager_support(recommendations)
            }
            
            return development_plan
            
        except Exception as e:
            logger.error(f"Development plan creation error: {str(e)}")
            return {}

    async def _generate_learning_resources(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate learning resources based on recommendations"""
        try:
            resources = []
            
            # Map recommendation types to learning resources
            resource_mapping = {
                "skill_development": [
                    {"type": "online_course", "provider": "Coursera", "category": "technical"},
                    {"type": "certification", "provider": "AWS/Azure", "category": "cloud"},
                    {"type": "workshop", "provider": "Internal", "category": "hands_on"}
                ],
                "communication_improvement": [
                    {"type": "workshop", "provider": "Dale Carnegie", "category": "soft_skills"},
                    {"type": "book", "provider": "Various", "category": "communication"},
                    {"type": "coaching", "provider": "External Coach", "category": "personal"}
                ],
                "goal_management": [
                    {"type": "training", "provider": "Project Management Institute", "category": "methodology"},
                    {"type": "tool_training", "provider": "Jira/Asana", "category": "tools"},
                    {"type": "mentoring", "provider": "Internal", "category": "guidance"}
                ]
            }
            
            for rec in recommendations:
                rec_type = rec.get("type", "general_improvement")
                if rec_type in resource_mapping:
                    for resource_template in resource_mapping[rec_type]:
                        resource = {
                            "id": str(uuid.uuid4()),
                            "title": f"{resource_template['category'].title()} {resource_template['type'].title()}",
                            "type": resource_template["type"],
                            "provider": resource_template["provider"],
                            "category": resource_template["category"],
                            "priority": rec.get("priority", "medium"),
                            "estimated_duration": "4-8 weeks",
                            "cost_estimate": "$500-2000",
                            "related_recommendation": rec.get("id")
                        }
                        resources.append(resource)
            
            return resources[:8]  # Limit to 8 resources
            
        except Exception as e:
            logger.error(f"Learning resources generation error: {str(e)}")
            return []

    async def get_performance_dashboard(self, employee_id: str) -> Dict[str, Any]:
        """Get comprehensive performance dashboard"""
        try:
            # Get current performance data
            current_review = await self._get_latest_review(employee_id)
            
            # Get goal progress
            goal_progress = await self.goal_tracker.get_current_progress(employee_id)
            
            # Get performance trends
            performance_trends = await self._get_performance_trends(employee_id)
            
            # Get peer comparisons
            peer_comparison = await self._get_peer_comparison(employee_id)
            
            # Get development progress
            development_progress = await self._get_development_progress(employee_id)
            
            dashboard = {
                "employee_id": employee_id,
                "last_updated": datetime.utcnow().isoformat(),
                "current_performance": {
                    "overall_rating": current_review.get("final_rating", {}).get("overall_score", 0),
                    "rating_category": current_review.get("final_rating", {}).get("rating_category", "not_rated"),
                    "last_review_date": current_review.get("completed_at"),
                    "next_review_date": await self._calculate_next_review_date(employee_id)
                },
                "goal_progress": goal_progress,
                "performance_trends": performance_trends,
                "peer_comparison": peer_comparison,
                "development_progress": development_progress,
                "upcoming_actions": await self._get_upcoming_actions(employee_id),
                "achievements": await self._get_recent_achievements(employee_id),
                "areas_for_focus": await self._get_focus_areas(employee_id)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Performance dashboard error: {str(e)}")
            return {"error": str(e)}

    async def schedule_automated_reviews(self):
        """Schedule automated performance reviews for all employees"""
        try:
            # Get all active employees
            db = SessionLocal()
            employees = db.query(Employee).filter(Employee.is_active == True).all()
            db.close()
            
            scheduled_reviews = []
            
            for employee in employees:
                # Check if review is due
                last_review_date = await self._get_last_review_date(employee.id)
                
                for cycle_type, cycle_config in self.review_cycles.items():
                    if await self._is_review_due(employee.id, cycle_type, last_review_date):
                        # Schedule review
                        review_result = await self.start_performance_review(
                            employee_id=employee.id,
                            review_type=cycle_type
                        )
                        scheduled_reviews.append({
                            "employee_id": employee.id,
                            "review_type": cycle_type,
                            "review_id": review_result["review_id"]
                        })
            
            return {
                "scheduled_count": len(scheduled_reviews),
                "scheduled_reviews": scheduled_reviews,
                "scheduled_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Automated review scheduling error: {str(e)}")
            return {"error": str(e)}

    # Helper methods
    async def _get_employee_info(self, employee_id: str) -> Dict[str, Any]:
        """Get employee information"""
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
                    "manager_id": employee.manager_id,
                    "hire_date": employee.hire_date.isoformat() if employee.hire_date else None
                }
            return {}
        except Exception as e:
            logger.error(f"Employee info retrieval error: {str(e)}")
            return {}

    async def _calculate_review_period(self, review_type: str) -> Dict[str, str]:
        """Calculate review period dates"""
        try:
            end_date = datetime.utcnow()
            frequency = self.review_cycles.get(review_type, {}).get("frequency", 90)
            start_date = end_date - timedelta(days=frequency)
            
            return {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "frequency_days": frequency
            }
        except Exception as e:
            logger.error(f"Review period calculation error: {str(e)}")
            return {}

    async def _store_review_data(self, review_data: Dict[str, Any]):
        """Store review data in databases"""
        try:
            # Store in SQL
            db = SessionLocal()
            performance_review = PerformanceReview(
                id=review_data["id"],
                employee_id=review_data["employee_id"],
                reviewer_id=review_data["reviewer_id"],
                review_type=review_data["review_type"],
                status=review_data["status"],
                started_at=datetime.fromisoformat(review_data["started_at"]),
                overall_rating=review_data["final_rating"]
            )
            db.add(performance_review)
            db.commit()
            db.close()
            
            # Store detailed data in MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.performance_reviews.insert_one(review_data)
            
        except Exception as e:
            logger.error(f"Review data storage error: {str(e)}")
            raise

    async def _get_review_data(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get review data from MongoDB"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            review_data = await mongo_db.performance_reviews.find_one({"id": review_id})
            return review_data
        except Exception as e:
            logger.error(f"Review data retrieval error: {str(e)}")
            return None

    async def _update_review_data(self, review_data: Dict[str, Any]):
        """Update review data in databases"""
        try:
            # Update SQL
            db = SessionLocal()
            performance_review = db.query(PerformanceReview).filter(PerformanceReview.id == review_data["id"]).first()
            if performance_review:
                performance_review.status = review_data["status"]
                performance_review.overall_rating = review_data["final_rating"]
                if review_data.get("completed_at"):
                    performance_review.completed_at = datetime.fromisoformat(review_data["completed_at"])
                db.commit()
            db.close()
            
            # Update MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.performance_reviews.replace_one(
                {"id": review_data["id"]},
                review_data
            )
            
        except Exception as e:
            logger.error(f"Review data update error: {str(e)}")
