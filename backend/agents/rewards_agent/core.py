"""
Rewards Agent - Automated recognition and rewards system
Detects achievements, manages points, and handles automated recognition
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import openai
from datetime import datetime, timedelta
import json
import uuid
import numpy as np

from ..base_agent import BaseAgent
from backend.database.mongo_database import get_mongo_client
from backend.database.sql_database import SessionLocal
from models.sql_models import Employee, Achievement, RewardTransaction
from backend.utils.config import settings

logger = logging.getLogger(__name__)

class RewardsAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "rewards_agent"
        
        # Achievement types and point values
        self.achievement_types = {
            "performance": {
                "high_performance_review": {"points": 500, "badge": "star_performer"},
                "goal_exceeded": {"points": 300, "badge": "goal_crusher"},
                "project_completion": {"points": 200, "badge": "project_hero"},
                "innovation": {"points": 400, "badge": "innovator"},
                "quality_excellence": {"points": 250, "badge": "quality_champion"}
            },
            "collaboration": {
                "team_player": {"points": 200, "badge": "team_spirit"},
                "mentorship": {"points": 300, "badge": "mentor"},
                "cross_team_collaboration": {"points": 250, "badge": "bridge_builder"},
                "knowledge_sharing": {"points": 150, "badge": "knowledge_guru"},
                "conflict_resolution": {"points": 200, "badge": "peacemaker"}
            },
            "learning": {
                "training_completion": {"points": 100, "badge": "learner"},
                "certification_earned": {"points": 400, "badge": "certified_expert"},
                "skill_mastery": {"points": 300, "badge": "skill_master"},
                "conference_attendance": {"points": 150, "badge": "knowledge_seeker"},
                "internal_presentation": {"points": 200, "badge": "presenter  "knowledge_seeker"},
                "internal_presentation": {"points": 200, "badge": "presenter"}
            },
            "attendance": {
                "perfect_attendance": {"points": 300, "badge": "always_present"},
                "early_bird": {"points": 50, "badge": "early_riser"},
                "punctuality": {"points": 100, "badge": "on_time"},
                "overtime_dedication": {"points": 150, "badge": "dedicated_worker"}
            },
            "milestones": {
                "work_anniversary": {"points": 500, "badge": "veteran"},
                "first_day": {"points": 100, "badge": "newcomer"},
                "promotion": {"points": 1000, "badge": "rising_star"},
                "long_service": {"points": 750, "badge": "loyal_employee"}
            },
            "wellness": {
                "wellness_participation": {"points": 100, "badge": "wellness_warrior"},
                "fitness_challenge": {"points": 150, "badge": "fitness_champion"},
                "mental_health_awareness": {"points": 100, "badge": "mindful_employee"}
            }
        }
        
        # Reward tiers and benefits
        self.reward_tiers = {
            "bronze": {"min_points": 0, "max_points": 999, "benefits": ["Basic recognition"]},
            "silver": {"min_points": 1000, "max_points": 2999, "benefits": ["Priority parking", "Flexible hours"]},
            "gold": {"min_points": 3000, "max_points": 7499, "benefits": ["Extra PTO day", "Learning budget"]},
            "platinum": {"min_points": 7500, "max_points": 14999, "benefits": ["Bonus eligibility", "Conference attendance"]},
            "diamond": {"min_points": 15000, "max_points": float('inf'), "benefits": ["Stock options", "Executive mentoring"]}
        }
        
        # Recognition triggers
        self.recognition_triggers = {
            "performance_review": {"threshold": 85, "auto_recognize": True},
            "goal_completion": {"threshold": 100, "auto_recognize": True},
            "peer_nomination": {"threshold": 3, "auto_recognize": True},
            "customer_feedback": {"threshold": 4.5, "auto_recognize": True},
            "project_delivery": {"threshold": "on_time", "auto_recognize": True}
        }

    async def initialize(self):
        """Initialize rewards agent"""
        try:
            logger.info("Initializing Rewards Agent...")
            await super().initialize()
            
            # Initialize OpenAI for achievement analysis
            openai.api_key = settings.OPENAI_API_KEY
            
            # Start automated processes
            asyncio.create_task(self._automated_achievement_detection())
            asyncio.create_task(self._automated_milestone_tracking())
            asyncio.create_task(self._automated_recognition_campaigns())
            
            self.is_initialized = True
            logger.info("Rewards Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Rewards Agent: {str(e)}")
            raise

    async def detect_achievements(self, employee_id: str, trigger_event: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically detect and award achievements"""
        try:
            logger.info(f"Detecting achievements for employee {employee_id}, trigger: {trigger_event}")
            
            detection_result = {
                "employee_id": employee_id,
                "trigger_event": trigger_event,
                "event_data": event_data,
                "detected_at": datetime.utcnow().isoformat(),
                "achievements_awarded": [],
                "points_earned": 0,
                "badges_earned": [],
                "tier_changes": [],
                "achievements_processed": 0
            }
            
            # Analyze event for potential achievements
            potential_achievements = await self._analyze_event_for_achievements(trigger_event, event_data)
            
            for achievement_data in potential_achievements:
                # Validate achievement eligibility
                if await self._validate_achievement_eligibility(employee_id, achievement_data):
                    # Award achievement
                    awarded_achievement = await self._award_achievement(employee_id, achievement_data)
                    
                    detection_result["achievements_awarded"].append(awarded_achievement)
                    detection_result["points_earned"] += awarded_achievement["points"]
                    detection_result["badges_earned"].append(awarded_achievement["badge"])
                    detection_result["achievements_processed"] += 1
            
            # Check for tier changes
            if detection_result["points_earned"] > 0:
                tier_change = await self._check_tier_progression(employee_id, detection_result["points_earned"])
                if tier_change:
                    detection_result["tier_changes"].append(tier_change)
            
            # Send recognition notifications
            if detection_result["achievements_awarded"]:
                await self._send_achievement_notifications(employee_id, detection_result)
            
            # Store achievement data
            await self._store_achievement_data(detection_result)
            
            return detection_result
            
        except Exception as e:
            logger.error(f"Achievement detection error: {str(e)}")
            return {"error": str(e), "achievements_processed": 0}

    async def _analyze_event_for_achievements(self, trigger_event: str, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze event to identify potential achievements"""
        try:
            potential_achievements = []
            
            if trigger_event == "performance_review_completed":
                score = event_data.get("overall_score", 0)
                if score >= 90:
                    potential_achievements.append({
                        "type": "performance",
                        "subtype": "high_performance_review",
                        "reason": f"Exceptional performance review score: {score}",
                        "evidence": event_data
                    })
                elif score >= 85:
                    potential_achievements.append({
                        "type": "performance",
                        "subtype": "goal_exceeded",
                        "reason": f"Strong performance review score: {score}",
                        "evidence": event_data
                    })
            
            elif trigger_event == "project_completed":
                if event_data.get("status") == "on_time" and event_data.get("quality_score", 0) >= 85:
                    potential_achievements.append({
                        "type": "performance",
                        "subtype": "project_completion",
                        "reason": "Project completed on time with high quality",
                        "evidence": event_data
                    })
            
            elif trigger_event == "training_completed":
                potential_achievements.append({
                    "type": "learning",
                    "subtype": "training_completion",
                    "reason": f"Completed training: {event_data.get('course_name', 'Unknown')}",
                    "evidence": event_data
                })
                
                if event_data.get("certification_earned"):
                    potential_achievements.append({
                        "type": "learning",
                        "subtype": "certification_earned",
                        "reason": f"Earned certification: {event_data.get('certification_name')}",
                        "evidence": event_data
                    })
            
            elif trigger_event == "work_anniversary":
                years = event_data.get("years_of_service", 0)
                if years >= 5:
                    potential_achievements.append({
                        "type": "milestones",
                        "subtype": "long_service",
                        "reason": f"{years} years of dedicated service",
                        "evidence": event_data
                    })
                else:
                    potential_achievements.append({
                        "type": "milestones",
                        "subtype": "work_anniversary",
                        "reason": f"{years} years with the company",
                        "evidence": event_data
                    })
            
            elif trigger_event == "peer_recognition":
                potential_achievements.append({
                    "type": "collaboration",
                    "subtype": "team_player",
                    "reason": "Recognized by peers for collaboration",
                    "evidence": event_data
                })
            
            elif trigger_event == "mentorship_activity":
                potential_achievements.append({
                    "type": "collaboration",
                    "subtype": "mentorship",
                    "reason": "Active mentoring of team members",
                    "evidence": event_data
                })
            
            elif trigger_event == "perfect_attendance":
                potential_achievements.append({
                    "type": "attendance",
                    "subtype": "perfect_attendance",
                    "reason": f"Perfect attendance for {event_data.get('period', 'period')}",
                    "evidence": event_data
                })
            
            elif trigger_event == "innovation_submission":
                potential_achievements.append({
                    "type": "performance",
                    "subtype": "innovation",
                    "reason": "Submitted innovative idea or solution",
                    "evidence": event_data
                })
            
            elif trigger_event == "hiring_completed":
                potential_achievements.append({
                    "type": "milestones",
                    "subtype": "first_day",
                    "reason": "Welcome to the team!",
                    "evidence": event_data
                })
            
            return potential_achievements
            
        except Exception as e:
            logger.error(f"Event analysis error: {str(e)}")
            return []

    async def _validate_achievement_eligibility(self, employee_id: str, achievement_data: Dict[str, Any]) -> bool:
        """Validate if employee is eligible for achievement"""
        try:
            achievement_type = achievement_data["type"]
            achievement_subtype = achievement_data["subtype"]
            
            # Check if achievement already awarded recently
            recent_achievements = await self._get_recent_achievements(employee_id, days=30)
            
            for recent in recent_achievements:
                if (recent["type"] == achievement_type and 
                    recent["subtype"] == achievement_subtype):
                    # Don't award same achievement within 30 days
                    return False
            
            # Check specific eligibility criteria
            if achievement_type == "milestones" and achievement_subtype == "work_anniversary":
                # Only award once per year
                anniversary_achievements = await self._get_achievements_by_type(
                    employee_id, "milestones", "work_anniversary"
                )
                
                current_year = datetime.utcnow().year
                for ach in anniversary_achievements:
                    ach_year = datetime.fromisoformat(ach["awarded_at"]).year
                    if ach_year == current_year:
                        return False
            
            elif achievement_type == "performance" and achievement_subtype == "high_performance_review":
                # Ensure performance score meets threshold
                evidence = achievement_data.get("evidence", {})
                if evidence.get("overall_score", 0) < 90:
                    return False
            
            elif achievement_type == "learning" and achievement_subtype == "certification_earned":
                # Ensure certification is valid and recognized
                evidence = achievement_data.get("evidence", {})
                if not evidence.get("certification_name"):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Achievement eligibility validation error: {str(e)}")
            return False

    async def _award_achievement(self, employee_id: str, achievement_data: Dict[str, Any]) -> Dict[str, Any]:
        """Award achievement to employee"""
        try:
            achievement_type = achievement_data["type"]
            achievement_subtype = achievement_data["subtype"]
            
            # Get achievement configuration
            achievement_config = self.achievement_types.get(achievement_type, {}).get(achievement_subtype, {})
            
            points = achievement_config.get("points", 100)
            badge = achievement_config.get("badge", "achiever")
            
            # Create achievement record
            achievement = {
                "id": str(uuid.uuid4()),
                "employee_id": employee_id,
                "type": achievement_type,
                "subtype": achievement_subtype,
                "points": points,
                "badge": badge,
                "reason": achievement_data.get("reason", "Achievement earned"),
                "evidence": achievement_data.get("evidence", {}),
                "awarded_at": datetime.utcnow().isoformat(),
                "awarded_by": "system"
            }
            
            # Update employee points
            await self._update_employee_points(employee_id, points)
            
            # Store achievement
            await self._store_achievement(achievement)
            
            # Create reward transaction
            await self._create_reward_transaction(employee_id, points, achievement["id"])
            
            return achievement
            
        except Exception as e:
            logger.error(f"Achievement awarding error: {str(e)}")
            raise

    async def _check_tier_progression(self, employee_id: str, points_earned: int) -> Optional[Dict[str, Any]]:
        """Check if employee progressed to new tier"""
        try:
            # Get current points
            current_points = await self._get_employee_total_points(employee_id)
            previous_points = current_points - points_earned
            
            # Determine previous and current tiers
            previous_tier = await self._determine_tier(previous_points)
            current_tier = await self._determine_tier(current_points)
            
            if previous_tier != current_tier:
                tier_change = {
                    "employee_id": employee_id,
                    "previous_tier": previous_tier,
                    "new_tier": current_tier,
                    "points_at_change": current_points,
                    "changed_at": datetime.utcnow().isoformat(),
                    "benefits_unlocked": self.reward_tiers[current_tier]["benefits"]
                }
                
                # Store tier change
                await self._store_tier_change(tier_change)
                
                return tier_change
            
            return None
            
        except Exception as e:
            logger.error(f"Tier progression check error: {str(e)}")
            return None

    async def _determine_tier(self, points: int) -> str:
        """Determine reward tier based on points"""
        for tier, config in self.reward_tiers.items():
            if config["min_points"] <= points <= config["max_points"]:
                return tier
        return "bronze"

    async def generate_recognition_campaign(self, campaign_type: str, target_group: str = "all") -> Dict[str, Any]:
        """Generate automated recognition campaign"""
        try:
            campaign_id = str(uuid.uuid4())
            
            campaign_data = {
                "id": campaign_id,
                "type": campaign_type,
                "target_group": target_group,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active",
                "participants": [],
                "achievements_awarded": 0,
                "total_points_distributed": 0
            }
            
            if campaign_type == "monthly_recognition":
                # Recognize top performers of the month
                top_performers = await self._identify_top_performers()
                
                for performer in top_performers:
                    achievement_result = await self.detect_achievements(
                        performer["employee_id"],
                        "monthly_recognition",
                        {"performance_rank": performer["rank"], "metrics": performer["metrics"]}
                    )
                    
                    campaign_data["participants"].append(performer["employee_id"])
                    campaign_data["achievements_awarded"] += achievement_result.get("achievements_processed", 0)
                    campaign_data["total_points_distributed"] += achievement_result.get("points_earned", 0)
            
            elif campaign_type == "team_appreciation":
                # Recognize collaborative efforts
                collaborative_teams = await self._identify_collaborative_teams()
                
                for team in collaborative_teams:
                    for member_id in team["members"]:
                        achievement_result = await self.detect_achievements(
                            member_id,
                            "team_collaboration",
                            {"team_id": team["id"], "collaboration_score": team["score"]}
                        )
                        
                        campaign_data["participants"].append(member_id)
                        campaign_data["achievements_awarded"] += achievement_result.get("achievements_processed", 0)
                        campaign_data["total_points_distributed"] += achievement_result.get("points_earned", 0)
            
            elif campaign_type == "learning_champions":
                # Recognize learning and development
                learning_champions = await self._identify_learning_champions()
                
                for champion in learning_champions:
                    achievement_result = await self.detect_achievements(
                        champion["employee_id"],
                        "learning_excellence",
                        {"courses_completed": champion["courses"], "certifications": champion["certifications"]}
                    )
                    
                    campaign_data["participants"].append(champion["employee_id"])
                    campaign_data["achievements_awarded"] += achievement_result.get("achievements_processed", 0)
                    campaign_data["total_points_distributed"] += achievement_result.get("points_earned", 0)
            
            # Store campaign data
            await self._store_recognition_campaign(campaign_data)
            
            # Send campaign notifications
            await self._send_campaign_notifications(campaign_data)
            
            return campaign_data
            
        except Exception as e:
            logger.error(f"Recognition campaign generation error: {str(e)}")
            raise

    async def get_employee_rewards_dashboard(self, employee_id: str) -> Dict[str, Any]:
        """Get comprehensive rewards dashboard for employee"""
        try:
            dashboard = {
                "employee_id": employee_id,
                "generated_at": datetime.utcnow().isoformat(),
                "current_points": await self._get_employee_total_points(employee_id),
                "current_tier": await self._get_employee_current_tier(employee_id),
                "achievements": await self._get_employee_achievements(employee_id),
                "recent_activities": await self._get_recent_reward_activities(employee_id),
                "tier_progress": await self._calculate_tier_progress(employee_id),
                "available_rewards": await self._get_available_rewards(employee_id),
                "leaderboard_position": await self._get_leaderboard_position(employee_id),
                "achievement_statistics": await self._get_achievement_statistics(employee_id),
                "upcoming_milestones": await self._get_upcoming_milestones(employee_id)
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Rewards dashboard error: {str(e)}")
            return {"error": str(e)}

    async def _automated_achievement_detection(self):
        """Automated background achievement detection"""
        while True:
            try:
                # Check for performance-based achievements
                await self._check_performance_achievements()
                
                # Check for attendance-based achievements
                await self._check_attendance_achievements()
                
                # Check for learning achievements
                await self._check_learning_achievements()
                
                # Check for collaboration achievements
                await self._check_collaboration_achievements()
                
                # Sleep for 6 hours
                await asyncio.sleep(21600)
                
            except Exception as e:
                logger.error(f"Automated achievement detection error: {str(e)}")
                await asyncio.sleep(3600)

    async def _automated_milestone_tracking(self):
        """Automated milestone tracking"""
        while True:
            try:
                # Check work anniversaries
                await self._check_work_anniversaries()
                
                # Check service milestones
                await self._check_service_milestones()
                
                # Check promotion milestones
                await self._check_promotion_milestones()
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Automated milestone tracking error: {str(e)}")
                await asyncio.sleep(3600)

    async def _automated_recognition_campaigns(self):
        """Automated recognition campaigns"""
        while True:
            try:
                # Monthly recognition campaign
                if datetime.utcnow().day == 1:  # First day of month
                    await self.generate_recognition_campaign("monthly_recognition")
                
                # Weekly team appreciation
                if datetime.utcnow().weekday() == 0:  # Monday
                    await self.generate_recognition_campaign("team_appreciation")
                
                # Quarterly learning champions
                if datetime.utcnow().day == 1 and datetime.utcnow().month % 3 == 1:
                    await self.generate_recognition_campaign("learning_champions")
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Automated recognition campaigns error: {str(e)}")
                await asyncio.sleep(3600)

    # Helper methods
    async def _get_employee_total_points(self, employee_id: str) -> int:
        """Get total points for employee"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            
            pipeline = [
                {"$match": {"employee_id": employee_id}},
                {"$group": {"_id": None, "total_points": {"$sum": "$points"}}}
            ]
            
            result = await mongo_db.achievements.aggregate(pipeline).to_list(None)
            return result[0]["total_points"] if result else 0
            
        except Exception as e:
            logger.error(f"Get employee points error: {str(e)}")
            return 0

    async def _store_achievement(self, achievement: Dict[str, Any]):
        """Store achievement in databases"""
        try:
            # Store in SQL
            db = SessionLocal()
            achievement_record = Achievement(
                id=achievement["id"],
                employee_id=achievement["employee_id"],
                achievement_type=achievement["type"],
                achievement_subtype=achievement["subtype"],
                points=achievement["points"],
                awarded_at=datetime.fromisoformat(achievement["awarded_at"])
            )
            db.add(achievement_record)
            db.commit()
            db.close()
            
            # Store detailed data in MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.achievements.insert_one(achievement)
            
        except Exception as e:
            logger.error(f"Achievement storage error: {str(e)}")

    async def _send_achievement_notifications(self, employee_id: str, detection_result: Dict[str, Any]):
        """Send achievement notifications"""
        try:
            from ..communication_agent.core import CommunicationAgent
            comm_agent = CommunicationAgent()
            
            # Send to employee
            await comm_agent.send_communication(
                recipient_id=employee_id,
                communication_type="achievement_notification",
                channel="email",
                template_data=detection_result
            )
            
            # Send to manager
            employee_data = await self._get_employee_data(employee_id)
            if employee_data.get("manager_id"):
                await comm_agent.send_communication(
                    recipient_id=employee_data["manager_id"],
                    communication_type="team_achievement_notification",
                    channel="email",
                    template_data=detection_result
                )
            
        except Exception as e:
            logger.error(f"Achievement notification error: {str(e)}")

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
                    "manager_id": employee.manager_id,
                    "department": employee.department,
                    "position": employee.position
                }
            return {}
        except Exception as e:
            logger.error(f"Employee data retrieval error: {str(e)}")
            return {}
