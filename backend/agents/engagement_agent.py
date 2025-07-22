
"""
Employee Engagement & Wellness Agent
Handles pulse surveys, mood tracking, wellness programs, and gamification
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import uuid
import random
import numpy as np
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class EmployeeEngagementAgent:
    def __init__(self):
        self.agent_name = "engagement_agent"
        self.wellness_programs = []
        self.gamification_rules = {}
        self.mood_analytics = {}
        
    async def conduct_pulse_survey(self, survey_config: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct automated pulse survey"""
        try:
            survey_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Generate survey questions based on config
            questions = await self._generate_survey_questions(survey_config)
            
            # Determine target employees
            target_employees = await self._get_target_employees(survey_config.get("target_criteria", {}))
            
            # Create survey instance
            survey = {
                "id": survey_id,
                "title": survey_config.get("title", "Employee Pulse Survey"),
                "description": survey_config.get("description", "Help us understand your workplace experience"),
                "questions": questions,
                "target_employees": target_employees,
                "launch_date": current_time.isoformat(),
                "expiry_date": (current_time + timedelta(days=survey_config.get("duration_days", 7))).isoformat(),
                "status": "active",
                "anonymous": survey_config.get("anonymous", True),
                "frequency": survey_config.get("frequency", "monthly")
            }
            
            # Send survey invitations
            invitation_results = await self._send_survey_invitations(survey)
            
            # Schedule follow-up reminders
            await self._schedule_survey_reminders(survey_id, survey["expiry_date"])
            
            return {
                "success": True,
                "survey_id": survey_id,
                "survey": survey,
                "invitation_results": invitation_results,
                "message": f"Pulse survey launched successfully to {len(target_employees)} employees"
            }
            
        except Exception as e:
            logger.error(f"Pulse survey creation error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def track_employee_mood(self, employee_id: str, mood_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track and analyze employee mood"""
        try:
            mood_entry = {
                "id": str(uuid.uuid4()),
                "employee_id": employee_id,
                "timestamp": datetime.utcnow().isoformat(),
                "mood_score": mood_data.get("mood_score", 5),  # 1-10 scale
                "energy_level": mood_data.get("energy_level", 5),  # 1-10 scale
                "stress_level": mood_data.get("stress_level", 5),  # 1-10 scale
                "satisfaction_level": mood_data.get("satisfaction_level", 5),  # 1-10 scale
                "factors": mood_data.get("factors", []),  # Contributing factors
                "notes": mood_data.get("notes", ""),
                "source": mood_data.get("source", "self_report")  # self_report, ai_analysis, biometric
            }
            
            # Save mood entry
            await self._save_mood_entry(mood_entry)
            
            # Analyze mood trends
            mood_analysis = await self._analyze_mood_trends(employee_id)
            
            # Check for alerts (significant mood changes)
            alerts = await self._check_mood_alerts(employee_id, mood_entry, mood_analysis)
            
            # Generate recommendations
            recommendations = await self._generate_mood_recommendations(mood_entry, mood_analysis)
            
            # Update gamification points
            gamification_update = await self._update_wellness_points(employee_id, "mood_check", mood_entry)
            
            return {
                "success": True,
                "mood_entry": mood_entry,
                "analysis": mood_analysis,
                "alerts": alerts,
                "recommendations": recommendations,
                "gamification": gamification_update
            }
            
        except Exception as e:
            logger.error(f"Mood tracking error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def manage_wellness_program(self, program_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create and manage wellness programs"""
        try:
            program_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            wellness_program = {
                "id": program_id,
                "title": program_config.get("title", "Employee Wellness Program"),
                "description": program_config.get("description", ""),
                "type": program_config.get("type", "general"),  # fitness, mental_health, nutrition, etc.
                "duration_days": program_config.get("duration_days", 30),
                "start_date": current_time.isoformat(),
                "end_date": (current_time + timedelta(days=program_config.get("duration_days", 30))).isoformat(),
                "activities": program_config.get("activities", []),
                "goals": program_config.get("goals", []),
                "rewards": program_config.get("rewards", []),
                "target_participants": program_config.get("target_participants", []),
                "status": "active",
                "enrollment_count": 0,
                "completion_rate": 0
            }
            
            # Add default activities based on program type
            if not wellness_program["activities"]:
                wellness_program["activities"] = await self._generate_wellness_activities(program_config.get("type", "general"))
            
            # Save program
            await self._save_wellness_program(wellness_program)
            
            # Send enrollment invitations
            enrollment_results = await self._send_wellness_invitations(wellness_program)
            
            # Set up tracking and reminders
            await self._setup_wellness_tracking(program_id)
            
            return {
                "success": True,
                "program_id": program_id,
                "program": wellness_program,
                "enrollment_results": enrollment_results
            }
            
        except Exception as e:
            logger.error(f"Wellness program creation error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def implement_gamification_system(self, employee_id: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Implement gamification for employee engagement"""
        try:
            current_time = datetime.utcnow()
            
            # Get current employee gamification status
            employee_status = await self._get_employee_gamification_status(employee_id)
            
            # Calculate points for action
            points_earned = await self._calculate_action_points(action, context, employee_status)
            
            # Update employee points and level
            updated_status = await self._update_employee_gamification(employee_id, points_earned, action)
            
            # Check for achievements
            new_achievements = await self._check_for_achievements(employee_id, updated_status, action, context)
            
            # Check for level up
            level_up_info = await self._check_level_progression(employee_id, updated_status)
            
            # Generate rewards if applicable
            rewards = await self._generate_engagement_rewards(employee_id, updated_status, new_achievements)
            
            # Create activity log
            activity_log = {
                "id": str(uuid.uuid4()),
                "employee_id": employee_id,
                "action": action,
                "points_earned": points_earned,
                "total_points": updated_status["total_points"],
                "level": updated_status["level"],
                "achievements": new_achievements,
                "timestamp": current_time.isoformat(),
                "context": context
            }
            
            await self._log_gamification_activity(activity_log)
            
            return {
                "success": True,
                "points_earned": points_earned,
                "total_points": updated_status["total_points"],
                "level": updated_status["level"],
                "new_achievements": new_achievements,
                "level_up": level_up_info,
                "rewards": rewards,
                "leaderboard_position": await self._get_leaderboard_position(employee_id)
            }
            
        except Exception as e:
            logger.error(f"Gamification system error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def generate_engagement_analytics(self, time_period: str = "30d") -> Dict[str, Any]:
        """Generate comprehensive engagement analytics"""
        try:
            end_date = datetime.utcnow()
            if time_period == "7d":
                start_date = end_date - timedelta(days=7)
            elif time_period == "30d":
                start_date = end_date - timedelta(days=30)
            elif time_period == "90d":
                start_date = end_date - timedelta(days=90)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Gather analytics data
            survey_analytics = await self._analyze_survey_responses(start_date, end_date)
            mood_analytics = await self._analyze_mood_trends_period(start_date, end_date)
            wellness_analytics = await self._analyze_wellness_participation(start_date, end_date)
            gamification_analytics = await self._analyze_gamification_engagement(start_date, end_date)
            
            # Calculate overall engagement score
            overall_engagement = await self._calculate_overall_engagement_score(
                survey_analytics, mood_analytics, wellness_analytics, gamification_analytics
            )
            
            # Generate insights and recommendations
            insights = await self._generate_engagement_insights(
                survey_analytics, mood_analytics, wellness_analytics, gamification_analytics
            )
            
            # Identify at-risk employees
            at_risk_employees = await self._identify_at_risk_employees()
            
            analytics_report = {
                "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
                "overall_engagement_score": overall_engagement,
                "survey_analytics": survey_analytics,
                "mood_analytics": mood_analytics,
                "wellness_analytics": wellness_analytics,
                "gamification_analytics": gamification_analytics,
                "insights": insights,
                "at_risk_employees": at_risk_employees,
                "recommendations": await self._generate_engagement_recommendations(insights),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "analytics": analytics_report
            }
            
        except Exception as e:
            logger.error(f"Engagement analytics error: {str(e)}")
            return {"success": False, "error": str(e)}

    # Helper methods
    async def _generate_survey_questions(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate survey questions based on configuration"""
        question_banks = {
            "engagement": [
                {"id": "eng1", "text": "How satisfied are you with your current role?", "type": "scale", "scale": "1-10"},
                {"id": "eng2", "text": "Would you recommend this company as a great place to work?", "type": "scale", "scale": "1-10"},
                {"id": "eng3", "text": "Do you feel valued for your contributions?", "type": "scale", "scale": "1-10"}
            ],
            "wellbeing": [
                {"id": "wb1", "text": "How would you rate your work-life balance?", "type": "scale", "scale": "1-10"},
                {"id": "wb2", "text": "How often do you feel stressed at work?", "type": "multiple_choice", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"]},
                {"id": "wb3", "text": "Do you have access to wellness resources you need?", "type": "yes_no"}
            ],
            "leadership": [
                {"id": "ld1", "text": "How effectively does your manager communicate?", "type": "scale", "scale": "1-10"},
                {"id": "ld2", "text": "Do you receive regular feedback on your performance?", "type": "yes_no"},
                {"id": "ld3", "text": "Does your manager support your professional development?", "type": "scale", "scale": "1-10"}
            ]
        }
        
        survey_type = config.get("type", "engagement")
        num_questions = config.get("num_questions", 5)
        
        available_questions = question_banks.get(survey_type, question_banks["engagement"])
        selected_questions = random.sample(available_questions, min(num_questions, len(available_questions)))
        
        return selected_questions
    
    async def _get_target_employees(self, criteria: Dict[str, Any]) -> List[str]:
        """Get target employees based on criteria"""
        # Mock data - in real implementation, query database based on criteria
        all_employees = ["emp1", "emp2", "emp3", "emp4", "emp5"]
        
        department = criteria.get("department")
        role = criteria.get("role")
        tenure = criteria.get("min_tenure_months")
        
        # Apply filters (mock logic)
        target_employees = all_employees  # In real implementation, apply actual filters
        
        return target_employees
    
    async def _send_survey_invitations(self, survey: Dict[str, Any]) -> Dict[str, Any]:
        """Send survey invitations to target employees"""
        invitations_sent = len(survey["target_employees"])
        return {
            "total_invitations": invitations_sent,
            "delivery_status": "sent",
            "estimated_responses": int(invitations_sent * 0.7)  # 70% response rate estimate
        }
    
    async def _schedule_survey_reminders(self, survey_id: str, expiry_date: str):
        """Schedule follow-up reminders for survey"""
        logger.info(f"Scheduled reminders for survey {survey_id} until {expiry_date}")
    
    async def _save_mood_entry(self, mood_entry: Dict[str, Any]):
        """Save mood entry to database"""
        logger.info(f"Saving mood entry for employee: {mood_entry['employee_id']}")
    
    async def _analyze_mood_trends(self, employee_id: str) -> Dict[str, Any]:
        """Analyze mood trends for an employee"""
        # Mock analysis - in real implementation, analyze historical data
        return {
            "current_average": 7.2,
            "7_day_trend": 0.3,  # Positive trend
            "30_day_trend": -0.1,  # Slight negative trend
            "mood_stability": 0.8,  # High stability
            "risk_factors": ["workload_increase", "project_deadline"],
            "positive_factors": ["team_collaboration", "skill_development"]
        }
    
    async def _check_mood_alerts(self, employee_id: str, current_mood: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for mood-related alerts"""
        alerts = []
        
        if current_mood["mood_score"] <= 3:
            alerts.append({
                "type": "low_mood",
                "severity": "high",
                "message": "Employee reporting consistently low mood",
                "recommended_action": "Manager check-in recommended"
            })
        
        if current_mood["stress_level"] >= 8:
            alerts.append({
                "type": "high_stress",
                "severity": "medium",
                "message": "High stress level reported",
                "recommended_action": "Wellness resources should be offered"
            })
        
        return alerts
    
    async def _generate_mood_recommendations(self, mood_entry: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generate mood improvement recommendations"""
        recommendations = []
        
        if mood_entry["stress_level"] > 6:
            recommendations.append("Consider taking short breaks throughout the day")
            recommendations.append("Try our guided meditation sessions")
        
        if mood_entry["energy_level"] < 4:
            recommendations.append("Review your sleep schedule and aim for 7-8 hours")
            recommendations.append("Take a walk outside during lunch break")
        
        if mood_entry["satisfaction_level"] < 5:
            recommendations.append("Schedule a career development discussion with your manager")
            recommendations.append("Consider participating in skill-building workshops")
        
        return recommendations
    
    async def _update_wellness_points(self, employee_id: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Update employee wellness gamification points"""
        points_awarded = 10  # Base points for mood check-in
        
        return {
            "action": action,
            "points_awarded": points_awarded,
            "category": "wellness",
            "message": f"Earned {points_awarded} wellness points for mood check-in"
        }
    
    async def _generate_wellness_activities(self, program_type: str) -> List[Dict[str, Any]]:
        """Generate wellness activities based on program type"""
        activity_templates = {
            "fitness": [
                {"name": "Daily Step Challenge", "description": "Walk 8,000 steps daily", "points": 50},
                {"name": "Lunch Hour Workout", "description": "30-minute workout sessions", "points": 100},
                {"name": "Stairs Challenge", "description": "Use stairs instead of elevator", "points": 25}
            ],
            "mental_health": [
                {"name": "Mindfulness Monday", "description": "10-minute meditation session", "points": 75},
                {"name": "Gratitude Journal", "description": "Write 3 things you're grateful for", "points": 50},
                {"name": "Digital Detox Hour", "description": "1 hour without digital devices", "points": 100}
            ],
            "general": [
                {"name": "Hydration Goal", "description": "Drink 8 glasses of water daily", "points": 25},
                {"name": "Healthy Lunch Choice", "description": "Choose a healthy lunch option", "points": 50},
                {"name": "Team Building Activity", "description": "Participate in team activities", "points": 75}
            ]
        }
        
        return activity_templates.get(program_type, activity_templates["general"])
    
    async def _save_wellness_program(self, program: Dict[str, Any]):
        """Save wellness program to database"""
        logger.info(f"Saving wellness program: {program['id']}")
    
    async def _send_wellness_invitations(self, program: Dict[str, Any]) -> Dict[str, Any]:
        """Send wellness program invitations"""
        target_count = len(program["target_participants"]) if program["target_participants"] else 100
        return {
            "invitations_sent": target_count,
            "expected_enrollment": int(target_count * 0.4)  # 40% enrollment rate
        }
    
    async def _setup_wellness_tracking(self, program_id: str):
        """Set up tracking for wellness program"""
        logger.info(f"Setting up tracking for wellness program: {program_id}")
    
    async def _get_employee_gamification_status(self, employee_id: str) -> Dict[str, Any]:
        """Get employee's current gamification status"""
        # Mock data - in real implementation, fetch from database
        return {
            "total_points": 1250,
            "level": 3,
            "achievements": ["Early Bird", "Team Player", "Wellness Warrior"],
            "current_streak": 7,
            "badges": ["Collaborator", "Innovator"]
        }
    
    async def _calculate_action_points(self, action: str, context: Dict[str, Any], employee_status: Dict[str, Any]) -> int:
        """Calculate points for a specific action"""
        point_values = {
            "mood_check": 10,
            "survey_completion": 50,
            "wellness_activity": 25,
            "peer_recognition": 75,
            "goal_completion": 100,
            "training_completion": 150,
            "innovation_submission": 200
        }
        
        base_points = point_values.get(action, 10)
        
        # Apply multipliers based on streaks, level, etc.
        multiplier = 1.0
        if employee_status.get("current_streak", 0) > 7:
            multiplier += 0.2  # 20% bonus for 7+ day streak
        
        return int(base_points * multiplier)
    
    async def _update_employee_gamification(self, employee_id: str, points_earned: int, action: str) -> Dict[str, Any]:
        """Update employee's gamification status"""
        # Mock update - in real implementation, update database
        current_status = await self._get_employee_gamification_status(employee_id)
        new_total = current_status["total_points"] + points_earned
        
        # Calculate new level (every 500 points = 1 level)
        new_level = min(10, new_total // 500 + 1)
        
        return {
            "total_points": new_total,
            "level": new_level,
            "points_to_next_level": (new_level * 500) - new_total,
            "achievements": current_status["achievements"],
            "current_streak": current_status["current_streak"] + 1 if action in ["mood_check", "wellness_activity"] else current_status["current_streak"]
        }
    
    async def _check_for_achievements(self, employee_id: str, status: Dict[str, Any], action: str, context: Dict[str, Any]) -> List[str]:
        """Check for new achievements"""
        new_achievements = []
        
        # Check various achievement conditions
        if status["total_points"] >= 1000 and "Point Master" not in status["achievements"]:
            new_achievements.append("Point Master")
        
        if status["current_streak"] >= 30 and "Consistency Champion" not in status["achievements"]:
            new_achievements.append("Consistency Champion")
        
        if action == "peer_recognition" and "Team Player" not in status["achievements"]:
            new_achievements.append("Team Player")
        
        return new_achievements
    
    async def _check_level_progression(self, employee_id: str, status: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if employee leveled up"""
        # Mock level up check
        return None  # No level up in this case
    
    async def _generate_engagement_rewards(self, employee_id: str, status: Dict[str, Any], achievements: List[str]) -> List[Dict[str, Any]]:
        """Generate rewards based on engagement"""
        rewards = []
        
        for achievement in achievements:
            if achievement == "Point Master":
                rewards.append({
                    "type": "badge",
                    "name": "Point Master Badge",
                    "description": "Earned 1000+ engagement points",
                    "value": "recognition"
                })
        
        return rewards
    
    async def _log_gamification_activity(self, activity_log: Dict[str, Any]):
        """Log gamification activity"""
        logger.info(f"Logging gamification activity: {activity_log['action']}")
    
    async def _get_leaderboard_position(self, employee_id: str) -> int:
        """Get employee's leaderboard position"""
        return random.randint(1, 100)  # Mock position
    
    async def _analyze_survey_responses(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze survey responses for the period"""
        return {
            "surveys_conducted": 3,
            "total_responses": 127,
            "response_rate": 0.73,
            "average_satisfaction": 7.2,
            "engagement_trend": 0.15,
            "top_concerns": ["workload", "communication", "career_growth"],
            "top_positives": ["team_collaboration", "flexibility", "company_culture"]
        }
    
    async def _analyze_mood_trends_period(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze mood trends for the period"""
        return {
            "average_mood_score": 7.1,
            "mood_volatility": 0.8,
            "trending_up": 65,  # percentage of employees with improving mood
            "trending_down": 12,  # percentage with declining mood
            "stress_levels": {"low": 45, "medium": 40, "high": 15},
            "energy_levels": {"low": 20, "medium": 55, "high": 25}
        }
    
    async def _analyze_wellness_participation(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze wellness program participation"""
        return {
            "active_programs": 5,
            "total_participants": 234,
            "participation_rate": 0.68,
            "completion_rate": 0.45,
            "most_popular_activities": ["Step Challenge", "Meditation Sessions", "Healthy Lunch"],
            "wellness_score_improvement": 0.23
        }
    
    async def _analyze_gamification_engagement(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze gamification engagement"""
        return {
            "active_participants": 189,
            "total_points_awarded": 45230,
            "achievements_unlocked": 78,
            "average_level": 2.8,
            "top_activities": ["Survey Completion", "Peer Recognition", "Goal Achievement"],
            "engagement_increase": 0.34
        }
    
    async def _calculate_overall_engagement_score(self, survey_analytics: Dict[str, Any], 
                                                mood_analytics: Dict[str, Any], wellness_analytics: Dict[str, Any], 
                                                gamification_analytics: Dict[str, Any]) -> float:
        """Calculate overall engagement score"""
        # Weighted calculation of overall engagement
        survey_weight = 0.4
        mood_weight = 0.3
        wellness_weight = 0.2
        gamification_weight = 0.1
        
        survey_score = survey_analytics.get("average_satisfaction", 0) / 10
        mood_score = mood_analytics.get("average_mood_score", 0) / 10
        wellness_score = wellness_analytics.get("participation_rate", 0)
        gamification_score = min(1.0, gamification_analytics.get("active_participants", 0) / 200)
        
        overall_score = (
            survey_score * survey_weight +
            mood_score * mood_weight +
            wellness_score * wellness_weight +
            gamification_score * gamification_weight
        ) * 100
        
        return round(overall_score, 1)
    
    async def _generate_engagement_insights(self, survey_analytics: Dict[str, Any], mood_analytics: Dict[str, Any], 
                                          wellness_analytics: Dict[str, Any], gamification_analytics: Dict[str, Any]) -> List[str]:
        """Generate engagement insights"""
        insights = []
        
        if survey_analytics.get("response_rate", 0) < 0.6:
            insights.append("Survey response rate is below optimal. Consider shorter surveys or better incentives.")
        
        if mood_analytics.get("trending_down", 0) > 20:
            insights.append(f"{mood_analytics.get('trending_down', 0)}% of employees show declining mood trends.")
        
        if wellness_analytics.get("participation_rate", 0) < 0.5:
            insights.append("Wellness program participation is low. Review program offerings and accessibility.")
        
        if gamification_analytics.get("active_participants", 0) < 150:
            insights.append("Gamification engagement could be improved with more diverse activities and rewards.")
        
        return insights
    
    async def _identify_at_risk_employees(self) -> List[Dict[str, Any]]:
        """Identify employees at risk of disengagement"""
        # Mock at-risk analysis
        return [
            {
                "employee_id": "emp_123",
                "risk_level": "high",
                "factors": ["low_survey_scores", "declining_mood", "low_participation"],
                "recommended_actions": ["manager_checkin", "wellness_resources", "career_discussion"]
            },
            {
                "employee_id": "emp_456", 
                "risk_level": "medium",
                "factors": ["missed_surveys", "stress_indicators"],
                "recommended_actions": ["wellness_resources", "workload_review"]
            }
        ]
    
    async def _generate_engagement_recommendations(self, insights: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        return [
            "Implement more frequent pulse surveys with shorter formats",
            "Launch targeted wellness programs for high-stress departments",
            "Enhance gamification rewards and recognition systems",
            "Provide manager training on employee engagement techniques",
            "Create peer recognition programs to boost morale",
            "Offer flexible work arrangements to improve work-life balance"
        ]
