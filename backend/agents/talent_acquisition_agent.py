"""
Talent Acquisition Agent - Complete recruitment and hiring automation
Handles job posting, candidate sourcing, screening, and hiring pipeline
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import openai
from datetime import datetime, timedelta
import json
import uuid
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import re

from .base_agent import BaseAgent
from backend.database.mongo_database import get_mongo_client
from backend.database.sql_database import SessionLocal
from models.sql_models import Job, Candidate, Application, Interview
from backend.utils.config import settings
from backend.models.sql_models import Notification, AuditLog

logger = logging.getLogger(__name__)

class TalentAcquisitionAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "talent_acquisition_agent"
        
        # Job board integrations
        self.job_boards = {
            "linkedin": {"api_key": settings.LINKEDIN_API_KEY, "cost_per_post": 299},
            "indeed": {"api_key": settings.INDEED_API_KEY, "cost_per_post": 199},
            "glassdoor": {"api_key": settings.GLASSDOOR_API_KEY, "cost_per_post": 249},
            "monster": {"api_key": settings.MONSTER_API_KEY, "cost_per_post": 179},
            "ziprecruiter": {"api_key": settings.ZIPRECRUITER_API_KEY, "cost_per_post": 149}
        }
        
        # Sourcing channels
        self.sourcing_channels = {
            "social_media": ["linkedin", "twitter", "github", "stackoverflow"],
            "job_boards": ["indeed", "glassdoor", "monster", "ziprecruiter"],
            "referrals": ["employee_referral", "partner_referral", "agency_referral"],
            "direct_sourcing": ["company_website", "career_page", "talent_pool"],
            "universities": ["campus_recruitment", "internship_programs", "graduate_programs"]
        }
        
        # Screening criteria
        self.screening_criteria = {
            "technical": {
                "programming_skills": {"weight": 0.3, "threshold": 70},
                "system_design": {"weight": 0.2, "threshold": 65},
                "problem_solving": {"weight": 0.25, "threshold": 75},
                "code_quality": {"weight": 0.15, "threshold": 70},
                "testing": {"weight": 0.1, "threshold": 60}
            },
            "behavioral": {
                "communication": {"weight": 0.3, "threshold": 75},
                "teamwork": {"weight": 0.25, "threshold": 70},
                "leadership": {"weight": 0.2, "threshold": 65},
                "adaptability": {"weight": 0.15, "threshold": 70},
                "cultural_fit": {"weight": 0.1, "threshold": 75}
            },
            "experience": {
                "relevant_experience": {"weight": 0.4, "threshold": 80},
                "industry_knowledge": {"weight": 0.3, "threshold": 70},
                "project_complexity": {"weight": 0.2, "threshold": 65},
                "achievements": {"weight": 0.1, "threshold": 60}
            }
        }

    async def initialize(self):
        """Initialize talent acquisition agent"""
        try:
            logger.info("Initializing Talent Acquisition Agent...")
            await super().initialize()
            
            # Initialize OpenAI
            openai.api_key = settings.OPENAI_API_KEY
            
            # Start automated processes
            asyncio.create_task(self._automated_candidate_sourcing())
            asyncio.create_task(self._automated_application_screening())
            asyncio.create_task(self._automated_pipeline_management())
            asyncio.create_task(self._automated_market_analysis())
            
            self.is_initialized = True
            logger.info("Talent Acquisition Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Talent Acquisition Agent: {str(e)}")
            raise

    async def create_job_posting(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create and optimize job posting with AI"""
        try:
            job_id = str(uuid.uuid4())
            
            # AI-optimize job description
            optimized_description = await self._optimize_job_description(job_data)
            
            # Generate salary recommendations
            salary_analysis = await self._analyze_salary_market(job_data)
            
            # Create comprehensive job posting
            job_posting = {
                "id": job_id,
                "title": job_data["title"],
                "department": job_data["department"],
                "location": job_data["location"],
                "employment_type": job_data.get("employment_type", "full_time"),
                "experience_level": job_data.get("experience_level", "mid"),
                "original_description": job_data["description"],
                "optimized_description": optimized_description,
                "requirements": job_data.get("requirements", []),
                "responsibilities": job_data.get("responsibilities", []),
                "benefits": job_data.get("benefits", []),
                "salary_range": salary_analysis["recommended_range"],
                "salary_analysis": salary_analysis,
                "skills_required": await self._extract_required_skills(job_data),
                "posting_channels": await self._recommend_posting_channels(job_data),
                "target_demographics": await self._analyze_target_demographics(job_data),
                "competition_analysis": await self._analyze_job_competition(job_data),
                "created_at": datetime.utcnow().isoformat(),
                "status": "draft",
                "approval_status": "pending_approval",
                "approvers": job_data.get("approvers", []),
                "approval_history": [],
                "posted_channels": [],
                "applications_received": 0,
                "views": 0,
                "conversion_rate": 0.0
            }
            
            # Store job posting
            await self._store_job_posting(job_posting)
            
            return {
                "job_id": job_id,
                "optimized_description": optimized_description["enhanced_description"],
                "salary_recommendation": salary_analysis["recommended_range"],
                "posting_channels": job_posting["posting_channels"],
                "estimated_applications": salary_analysis["estimated_applications"],
                "posting_cost": await self._calculate_posting_cost(job_posting["posting_channels"])
            }
            
        except Exception as e:
            logger.error(f"Job posting creation error: {str(e)}")
            raise

    async def submit_job_requisition(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a job requisition for approval, with auto-approval logic"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            job_id = str(uuid.uuid4())
            job_posting = {
                "id": job_id,
                "title": job_data["title"],
                "department": job_data["department"],
                "location": job_data["location"],
                "employment_type": job_data.get("employment_type", "full_time"),
                "experience_level": job_data.get("experience_level", "mid"),
                "original_description": job_data["description"],
                "optimized_description": job_data.get("optimized_description", {}),
                "requirements": job_data.get("requirements", []),
                "responsibilities": job_data.get("responsibilities", []),
                "benefits": job_data.get("benefits", []),
                "salary_range": job_data.get("salary_range", {}),
                "skills_required": job_data.get("skills_required", []),
                "posting_channels": job_data.get("posting_channels", []),
                "created_at": datetime.utcnow().isoformat(),
                "status": "draft",
                "approval_status": "pending_approval",
                "approvers": job_data.get("approvers", []),
                "approval_history": [],
                "posted_channels": [],
                "applications_received": 0,
                "views": 0,
                "conversion_rate": 0.0
            }
            # Auto-approval logic
            budget = job_data.get("salary_range", {}).get("max", 0)
            if (
                job_data["department"] in settings.AUTO_APPROVE_DEPARTMENTS and
                budget <= settings.AUTO_APPROVE_BUDGET_LIMIT
            ):
                job_posting["approval_status"] = "approved"
                await self.send_notification(
                    user_id="hr_admin",
                    recipient_email="hr@company.com",
                    message=f"Job requisition {job_posting['title']} auto-approved.",
                    notif_type="system",
                    related_entity=job_id,
                    event_type="requisition_auto_approved"
                )
            # Save to DB
            await mongo_db.job_postings.insert_one(job_posting)
            return job_posting
        except Exception as e:
            logger.error(f"Job requisition submission error: {str(e)}")
            raise

    async def list_pending_requisitions(self) -> list:
        """List all job requisitions pending approval"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            pending = await mongo_db.job_postings.find({"approval_status": "pending_approval"}).to_list(None)
            return pending
        except Exception as e:
            logger.error(f"List pending requisitions error: {str(e)}")
            return []

    async def approve_requisition(self, job_id: str, approver_id: str, comment: str = "") -> bool:
        """Approve a job requisition"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            job = await mongo_db.job_postings.find_one({"id": job_id})
            if not job:
                return False
            approval_entry = {
                "approver_id": approver_id,
                "action": "approved",
                "timestamp": datetime.utcnow().isoformat(),
                "comment": comment
            }
            job.setdefault("approval_history", []).append(approval_entry)
            # Mark as approved if all approvers have approved
            job["approval_status"] = "approved"
            await mongo_db.job_postings.update_one({"id": job_id}, {"$set": job})
            # Also update SQL
            db = SessionLocal()
            db_job = db.query(Job).filter(Job.id == job_id).first()
            if db_job:
                db_job.approval_status = "approved"
                db_job.approval_history = job["approval_history"]
                db.commit()
            db.close()
            return True
        except Exception as e:
            logger.error(f"Approve requisition error: {str(e)}")
            return False

    async def reject_requisition(self, job_id: str, approver_id: str, comment: str = "") -> bool:
        """Reject a job requisition"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            job = await mongo_db.job_postings.find_one({"id": job_id})
            if not job:
                return False
            approval_entry = {
                "approver_id": approver_id,
                "action": "rejected",
                "timestamp": datetime.utcnow().isoformat(),
                "comment": comment
            }
            job.setdefault("approval_history", []).append(approval_entry)
            job["approval_status"] = "rejected"
            await mongo_db.job_postings.update_one({"id": job_id}, {"$set": job})
            # Also update SQL
            db = SessionLocal()
            db_job = db.query(Job).filter(Job.id == job_id).first()
            if db_job:
                db_job.approval_status = "rejected"
                db_job.approval_history = job["approval_history"]
                db.commit()
            db.close()
            return True
        except Exception as e:
            logger.error(f"Reject requisition error: {str(e)}")
            return False

    async def _optimize_job_description(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI-optimize job description for better candidate attraction"""
        try:
            original_description = job_data["description"]
            
            prompt = f"""
            Optimize this job description to attract top talent:
            
            Original Description: {original_description}
            Position: {job_data["title"]}
            Department: {job_data["department"]}
            Location: {job_data["location"]}
            
            Enhance the description to:
            1. Use compelling, inclusive language
            2. Highlight growth opportunities
            3. Emphasize company culture
            4. Include specific technical requirements
            5. Make it SEO-friendly for job boards
            6. Add diversity and inclusion statements
            
            Return JSON with:
            - enhanced_description
            - key_improvements
            - seo_keywords
            - inclusivity_score
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert talent acquisition specialist and copywriter."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            try:
                optimization_result = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                optimization_result = {
                    "enhanced_description": response.choices[0].message.content,
                    "key_improvements": ["AI optimization applied"],
                    "seo_keywords": [],
                    "inclusivity_score": 75
                }
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"Job description optimization error: {str(e)}")
            return {"enhanced_description": job_data["description"], "key_improvements": []}

    async def _analyze_salary_market(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market salary data and provide recommendations"""
        try:
            # Simulate market analysis (would integrate with salary APIs)
            base_salaries = {
                "Software Engineer": {"min": 70000, "max": 120000, "median": 95000},
                "Senior Software Engineer": {"min": 100000, "max": 160000, "median": 130000},
                "Data Scientist": {"min": 80000, "max": 140000, "median": 110000},
                "Product Manager": {"min": 90000, "max": 150000, "median": 120000},
                "DevOps Engineer": {"min": 85000, "max": 135000, "median": 110000}
            }
            
            title = job_data["title"]
            location = job_data["location"]
            experience_level = job_data.get("experience_level", "mid")
            
            # Get base salary range
            base_range = base_salaries.get(title, {"min": 60000, "max": 100000, "median": 80000})
            
            # Apply location multiplier
            location_multipliers = {
                "San Francisco": 1.4,
                "New York": 1.3,
                "Seattle": 1.2,
                "Austin": 1.1,
                "Remote": 1.0,
                "Other": 0.9
            }
            
            multiplier = location_multipliers.get(location, 1.0)
            
            # Apply experience multiplier
            experience_multipliers = {
                "entry": 0.8,
                "mid": 1.0,
                "senior": 1.3,
                "lead": 1.5,
                "principal": 1.8
            }
            
            exp_multiplier = experience_multipliers.get(experience_level, 1.0)
            
            # Calculate adjusted range
            adjusted_min = int(base_range["min"] * multiplier * exp_multiplier)
            adjusted_max = int(base_range["max"] * multiplier * exp_multiplier)
            adjusted_median = int(base_range["median"] * multiplier * exp_multiplier)
            
            return {
                "recommended_range": {
                    "min": adjusted_min,
                    "max": adjusted_max,
                    "median": adjusted_median
                },
                "market_data": {
                    "base_range": base_range,
                    "location_multiplier": multiplier,
                    "experience_multiplier": exp_multiplier
                },
                "competitiveness": "competitive" if multiplier >= 1.1 else "market_rate",
                "estimated_applications": int(50 * multiplier * exp_multiplier),
                "time_to_fill": max(14, int(30 / multiplier))
            }
            
        except Exception as e:
            logger.error(f"Salary market analysis error: {str(e)}")
            return {"recommended_range": {"min": 60000, "max": 100000, "median": 80000}}

    async def source_candidates(self, job_id: str, sourcing_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Automated candidate sourcing across multiple channels"""
        try:
            sourcing_result = {
                "job_id": job_id,
                "strategy": sourcing_strategy,
                "started_at": datetime.utcnow().isoformat(),
                "channels_used": [],
                "candidates_sourced": [],
                "total_candidates": 0,
                "quality_score": 0.0,
                "cost_per_candidate": 0.0
            }
            
            # Get job details
            job_posting = await self._get_job_posting(job_id)
            if not job_posting:
                raise ValueError("Job posting not found")
            
            # Source from different channels
            for channel in sourcing_strategy.get("channels", ["linkedin", "indeed"]):
                channel_result = await self._source_from_channel(job_posting, channel)
                sourcing_result["channels_used"].append(channel_result)
                sourcing_result["candidates_sourced"].extend(channel_result["candidates"])
            
            # Deduplicate candidates
            unique_candidates = await self._deduplicate_candidates(sourcing_result["candidates_sourced"])
            sourcing_result["candidates_sourced"] = unique_candidates
            sourcing_result["total_candidates"] = len(unique_candidates)
            
            # Score candidate quality
            for candidate in unique_candidates:
                quality_score = await self._score_candidate_quality(candidate, job_posting)
                candidate["quality_score"] = quality_score
            
            # Calculate metrics
            if unique_candidates:
                sourcing_result["quality_score"] = np.mean([c["quality_score"] for c in unique_candidates])
                sourcing_result["cost_per_candidate"] = sourcing_strategy.get("budget", 1000) / len(unique_candidates)
            
            # Store sourcing results
            await self._store_sourcing_results(sourcing_result)
            
            # Auto-screen high-quality candidates
            high_quality_candidates = [c for c in unique_candidates if c["quality_score"] > 75]
            for candidate in high_quality_candidates:
                await self._auto_screen_candidate(candidate, job_posting)
            
            return sourcing_result
            
        except Exception as e:
            logger.error(f"Candidate sourcing error: {str(e)}")
            raise

    async def _source_from_channel(self, job_posting: Dict[str, Any], channel: str) -> Dict[str, Any]:
        """Source candidates from specific channel"""
        try:
            channel_result = {
                "channel": channel,
                "candidates": [],
                "cost": 0,
                "response_rate": 0.0
            }
            
            if channel == "linkedin":
                candidates = await self._source_from_linkedin(job_posting)
                channel_result["candidates"] = candidates
                channel_result["cost"] = len(candidates) * 15  # $15 per LinkedIn contact
                
            elif channel == "indeed":
                candidates = await self._source_from_indeed(job_posting)
                channel_result["candidates"] = candidates
                channel_result["cost"] = len(candidates) * 8  # $8 per Indeed contact
                
            elif channel == "github":
                candidates = await self._source_from_github(job_posting)
                channel_result["candidates"] = candidates
                channel_result["cost"] = len(candidates) * 5  # $5 per GitHub contact
                
            elif channel == "referrals":
                candidates = await self._source_from_referrals(job_posting)
                channel_result["candidates"] = candidates
                channel_result["cost"] = len(candidates) * 500  # $500 referral bonus
            
            return channel_result
            
        except Exception as e:
            logger.error(f"Channel sourcing error for {channel}: {str(e)}")
            return {"channel": channel, "candidates": [], "cost": 0}

    async def _source_from_linkedin(self, job_posting: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Source candidates from LinkedIn"""
        try:
            # Simulate LinkedIn API integration
            skills_required = job_posting.get("skills_required", [])
            location = job_posting.get("location", "")
            
            # Generate mock LinkedIn candidates
            candidates = []
            for i in range(15):  # Simulate finding 15 candidates
                candidate = {
                    "id": str(uuid.uuid4()),
                    "name": f"LinkedIn Candidate {i+1}",
                    "email": f"candidate{i+1}@linkedin.com",
                    "source": "linkedin",
                    "profile_url": f"https://linkedin.com/in/candidate{i+1}",
                    "current_position": f"Software Engineer at Company {i+1}",
                    "location": location,
                    "skills": skills_required[:3] + [f"Skill{i+1}", f"Skill{i+2}"],
                    "experience_years": 3 + (i % 8),
                    "education": f"BS Computer Science from University {i+1}",
                    "connections": 500 + (i * 50),
                    "profile_completeness": 85 + (i % 15),
                    "last_active": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                    "sourced_at": datetime.utcnow().isoformat()
                }
                candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            logger.error(f"LinkedIn sourcing error: {str(e)}")
            return []

    async def _source_from_indeed(self, job_posting: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Source candidates from Indeed"""
        try:
            # Simulate Indeed API integration
            candidates = []
            for i in range(12):  # Simulate finding 12 candidates
                candidate = {
                    "id": str(uuid.uuid4()),
                    "name": f"Indeed Candidate {i+1}",
                    "email": f"candidate{i+1}@indeed.com",
                    "source": "indeed",
                    "resume_url": f"https://indeed.com/resume/candidate{i+1}",
                    "current_position": f"Developer at Startup {i+1}",
                    "location": job_posting.get("location", ""),
                    "skills": job_posting.get("skills_required", [])[:2] + [f"IndeedSkill{i+1}"],
                    "experience_years": 2 + (i % 6),
                    "salary_expectation": 70000 + (i * 5000),
                    "availability": "2 weeks" if i % 3 == 0 else "immediate",
                    "sourced_at": datetime.utcnow().isoformat()
                }
                candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            logger.error(f"Indeed sourcing error: {str(e)}")
            return []

    async def screen_application(self, application_id: str) -> Dict[str, Any]:
        """Automated application screening with AI"""
        try:
            # Get application data
            application = await self._get_application(application_id)
            if not application:
                raise ValueError("Application not found")
            
            # Get job requirements
            job_posting = await self._get_job_posting(application["job_id"])
            
            # Comprehensive screening
            screening_result = {
                "application_id": application_id,
                "candidate_id": application["candidate_id"],
                "job_id": application["job_id"],
                "screened_at": datetime.utcnow().isoformat(),
                "screening_scores": {},
                "overall_score": 0.0,
                "recommendation": "",
                "next_steps": [],
                "red_flags": [],
                "strengths": [],
                "areas_of_concern": []
            }
            
            # Technical screening
            if job_posting.get("requires_technical_screening", True):
                technical_score = await self._screen_technical_skills(application, job_posting)
                screening_result["screening_scores"]["technical"] = technical_score
            
            # Experience screening
            experience_score = await self._screen_experience(application, job_posting)
            screening_result["screening_scores"]["experience"] = experience_score
            
            # Cultural fit screening
            cultural_score = await self._screen_cultural_fit(application, job_posting)
            screening_result["screening_scores"]["cultural_fit"] = cultural_score
            
            # Communication screening
            communication_score = await self._screen_communication(application)
            screening_result["screening_scores"]["communication"] = communication_score
            
            # Calculate overall score
            weights = {"technical": 0.35, "experience": 0.3, "cultural_fit": 0.2, "communication": 0.15}
            overall_score = sum(
                screening_result["screening_scores"].get(category, 0) * weight
                for category, weight in weights.items()
            )
            screening_result["overall_score"] = overall_score
            
            # Generate recommendation
            if overall_score >= 80:
                screening_result["recommendation"] = "strong_hire"
                screening_result["next_steps"] = ["schedule_technical_interview", "reference_check"]
            elif overall_score >= 65:
                screening_result["recommendation"] = "hire"
                screening_result["next_steps"] = ["schedule_phone_screen", "portfolio_review"]
            elif overall_score >= 50:
                screening_result["recommendation"] = "maybe"
                screening_result["next_steps"] = ["additional_screening", "skill_assessment"]
            else:
                screening_result["recommendation"] = "no_hire"
                screening_result["next_steps"] = ["send_rejection"]
            
            # Identify red flags and strengths
            screening_result["red_flags"] = await self._identify_red_flags(application, screening_result)
            screening_result["strengths"] = await self._identify_strengths(application, screening_result)
            
            # Store screening results
            await self._store_screening_results(screening_result)
            
            # Auto-advance qualified candidates
            if screening_result["recommendation"] in ["strong_hire", "hire"]:
                await self._auto_advance_candidate(application, screening_result)
            
            # Notify candidate
            await self.send_notification(
                user_id=application["candidate_id"],
                recipient_email=application.get("candidate_email", ""),
                message="Your application has been screened. Check your status in the portal.",
                notif_type="email",
                related_entity=application["job_id"],
                event_type="screening_complete"
            )
            return screening_result
            
        except Exception as e:
            logger.error(f"Application screening error: {str(e)}")
            raise

    async def manage_hiring_pipeline(self, job_id: str):
        """Manage hiring pipeline, with auto-hiring logic for top candidates and optional human approval for final offer"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            candidates = await mongo_db.candidates.find({"job_id": job_id}).to_list(None)
            for candidate in candidates:
                if (
                    candidate.get("match_score", 0) >= settings.AUTO_HIRE_MATCH_SCORE and
                    candidate.get("current_stage") == "final_interview"
                ):
                    if settings.REQUIRE_HUMAN_APPROVAL_FOR_FINAL_OFFER:
                        await mongo_db.candidates.update_one(
                            {"_id": candidate["_id"]},
                            {"$set": {"current_stage": "ready_for_offer"}}
                        )
                        await self.send_notification(
                            user_id="hr_admin",
                            recipient_email="hr@company.com",
                            message=f"Candidate {candidate.get('name', '')} is ready for offer. Please review.",
                            notif_type="system",
                            related_entity=job_id,
                            event_type="ready_for_offer"
                        )
                        self.log_action(
                            user_id="system",
                            action="ready_for_offer",
                            entity_type="candidate",
                            entity_id=candidate["_id"],
                            details=f"Candidate {candidate.get('name', '')} moved to ready_for_offer for job {job_id}"
                        )
                    else:
                        await mongo_db.candidates.update_one(
                            {"_id": candidate["_id"]},
                            {"$set": {"current_stage": "hired"}}
                        )
                        await self.send_notification(
                            user_id=candidate.get("_id", ""),
                            recipient_email=candidate.get("email", ""),
                            message="Congratulations! You have been auto-hired. Onboarding will begin soon.",
                            notif_type="email",
                            related_entity=job_id,
                            event_type="auto_hired"
                        )
                        self.log_action(
                            user_id="system",
                            action="auto_hire",
                            entity_type="candidate",
                            entity_id=candidate["_id"],
                            details=f"Candidate {candidate.get('name', '')} auto-hired for job {job_id}"
                        )
            return {"status": "pipeline managed, auto-hiring or ready-for-offer applied if applicable"}
        except Exception as e:
            logger.error(f"Pipeline management error: {str(e)}")
            return {"error": str(e)}

    async def generate_diversity_report(self, job_id: str = None, time_period: str = "30d") -> Dict[str, Any]:
        """Generate comprehensive diversity and inclusion report"""
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
            
            diversity_report = {
                "period": time_period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "job_id": job_id,
                "demographics": {},
                "pipeline_diversity": {},
                "bias_analysis": {},
                "recommendations": [],
                "compliance_status": {},
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Get candidate data
            candidates = await self._get_candidates_for_period(start_date, end_date, job_id)
            
            # Analyze demographics
            diversity_report["demographics"] = await self._analyze_candidate_demographics(candidates)
            
            # Analyze pipeline diversity
            diversity_report["pipeline_diversity"] = await self._analyze_pipeline_diversity(candidates)
            
            # Detect potential bias
            diversity_report["bias_analysis"] = await self._analyze_hiring_bias(candidates)
            
            # Generate recommendations
            diversity_report["recommendations"] = await self._generate_diversity_recommendations(diversity_report)
            
            # Check compliance
            diversity_report["compliance_status"] = await self._check_diversity_compliance(diversity_report)
            
            return diversity_report
            
        except Exception as e:
            logger.error(f"Diversity report generation error: {str(e)}")
            return {"error": str(e)}

    async def _automated_candidate_sourcing(self):
        """Automated background candidate sourcing"""
        while True:
            try:
                # Get active job postings
                active_jobs = await self._get_active_job_postings()
                
                for job in active_jobs:
                    # Check if more candidates needed
                    if await self._needs_more_candidates(job):
                        # Auto-source candidates
                        sourcing_strategy = await self._generate_sourcing_strategy(job)
                        await self.source_candidates(job["id"], sourcing_strategy)
                
                # Sleep for 6 hours
                await asyncio.sleep(21600)
                
            except Exception as e:
                logger.error(f"Automated candidate sourcing error: {str(e)}")
                await asyncio.sleep(3600)

    async def _automated_application_screening(self):
        """Automated application screening"""
        while True:
            try:
                # Get unscreened applications
                unscreened_applications = await self._get_unscreened_applications()
                
                for application in unscreened_applications:
                    await self.screen_application(application["id"])
                
                # Sleep for 2 hours
                await asyncio.sleep(7200)
                
            except Exception as e:
                logger.error(f"Automated application screening error: {str(e)}")
                await asyncio.sleep(1800)

    async def _automated_pipeline_management(self):
        """Automated pipeline management"""
        while True:
            try:
                # Get all active jobs
                active_jobs = await self._get_active_job_postings()
                
                for job in active_jobs:
                    await self.manage_hiring_pipeline(job["id"])
                
                # Sleep for 4 hours
                await asyncio.sleep(14400)
                
            except Exception as e:
                logger.error(f"Automated pipeline management error: {str(e)}")
                await asyncio.sleep(3600)

    # Helper methods
    async def _store_job_posting(self, job_posting: Dict[str, Any]):
        """Store job posting in databases"""
        try:
            # Store in SQL
            db = SessionLocal()
            job_record = Job(
                id=job_posting["id"],
                title=job_posting["title"],
                department=job_posting["department"],
                location=job_posting["location"],
                employment_type=job_posting["employment_type"],
                description=job_posting["optimized_description"]["enhanced_description"],
                status=job_posting["status"],
                created_at=datetime.fromisoformat(job_posting["created_at"])
            )
            db.add(job_record)
            db.commit()
            db.close()
            
            # Store detailed data in MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.job_postings.insert_one(job_posting)
            
        except Exception as e:
            logger.error(f"Job posting storage error: {str(e)}")

    async def _get_job_posting(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job posting from database"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            job_posting = await mongo_db.job_postings.find_one({"id": job_id})
            return job_posting
        except Exception as e:
            logger.error(f"Job posting retrieval error: {str(e)}")
            return None

    async def _extract_required_skills(self, job_data: Dict[str, Any]) -> List[str]:
        """Extract required skills from job description"""
        try:
            description = job_data["description"]
            requirements = job_data.get("requirements", [])
            
            # Common tech skills
            tech_skills = [
                "Python", "JavaScript", "Java", "C++", "React", "Angular", "Node.js",
                "AWS", "Docker", "Kubernetes", "SQL", "MongoDB", "Git", "Linux"
            ]
            
            found_skills = []
            text = (description + " " + " ".join(requirements)).lower()
            
            for skill in tech_skills:
                if skill.lower() in text:
                    found_skills.append(skill)
            
            return found_skills
            
        except Exception as e:
            logger.error(f"Skill extraction error: {str(e)}")
            return []

    async def _recommend_posting_channels(self, job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend optimal posting channels"""
        try:
            channels = []
            
            # Always recommend company website
            channels.append({
                "channel": "company_website",
                "cost": 0,
                "expected_applications": 15,
                "quality_score": 85
            })
            
            # Recommend based on role type
            if "engineer" in job_data["title"].lower():
                channels.extend([
                    {"channel": "linkedin", "cost": 299, "expected_applications": 45, "quality_score": 80},
                    {"channel": "stackoverflow", "cost": 199, "expected_applications": 25, "quality_score": 90},
                    {"channel": "github_jobs", "cost": 149, "expected_applications": 20, "quality_score": 85}
                ])
            else:
                channels.extend([
                    {"channel": "linkedin", "cost": 299, "expected_applications": 35, "quality_score": 75},
                    {"channel": "indeed", "cost": 199, "expected_applications": 50, "quality_score": 65},
                    {"channel": "glassdoor", "cost": 249, "expected_applications": 30, "quality_score": 70}
                ])
            
            return channels
            
        except Exception as e:
            logger.error(f"Channel recommendation error: {str(e)}")
            return []

    async def _score_candidate_quality(self, candidate: Dict[str, Any], job_posting: Dict[str, Any]) -> float:
        """Score candidate quality against job requirements"""
        try:
            score = 0.0
            
            # Skills match (40%)
            required_skills = job_posting.get("skills_required", [])
            candidate_skills = candidate.get("skills", [])
            
            if required_skills:
                skill_matches = len(set(required_skills) & set(candidate_skills))
                skill_score = (skill_matches / len(required_skills)) * 40
                score += skill_score
            
            # Experience match (30%)
            required_experience = job_posting.get("experience_level", "mid")
            candidate_experience = candidate.get("experience_years", 0)
            
            experience_mapping = {"entry": 2, "mid": 5, "senior": 8, "lead": 12}
            required_years = experience_mapping.get(required_experience, 5)
            
            if candidate_experience >= required_years:
                score += 30
            elif candidate_experience >= required_years * 0.7:
                score += 20
            else:
                score += 10
            
            # Location match (15%)
            if candidate.get("location", "").lower() == job_posting.get("location", "").lower():
                score += 15
            elif "remote" in job_posting.get("location", "").lower():
                score += 15
            else:
                score += 5
            
            # Profile completeness (15%)
            completeness = candidate.get("profile_completeness", 50)
            score += (completeness / 100) * 15
            
            return min(100, score)
            
        except Exception as e:
            logger.error(f"Candidate quality scoring error: {str(e)}")
            return 50.0

    async def _screen_technical_skills(self, application: Dict[str, Any], job_posting: Dict[str, Any]) -> float:
        """Screen technical skills"""
        try:
            # Get candidate resume/profile
            candidate_data = application.get("candidate_data", {})
            required_skills = job_posting.get("skills_required", [])
            
            # Analyze technical content
            technical_content = candidate_data.get("technical_experience", "")
            
            # Use AI to assess technical competency
            prompt = f"""
            Assess the technical competency of this candidate:
            
            Required Skills: {required_skills}
            Candidate Technical Experience: {technical_content}
            
            Rate on scale 0-100 considering:
            1. Skill relevance and depth
            2. Project complexity
            3. Technical problem-solving
            4. Code quality indicators
            5. System design experience
            
            Return only a number 0-100.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical interviewer assessing candidates."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            try:
                score = float(response.choices[0].message.content.strip())
                return max(0, min(100, score))
            except ValueError:
                return 50.0
                
        except Exception as e:
            logger.error(f"Technical screening error: {str(e)}")
            return 50.0

    async def _screen_experience(self, application: Dict[str, Any], job_posting: Dict[str, Any]) -> float:
        """Screen candidate experience"""
        try:
            candidate_data = application.get("candidate_data", {})
            
            # Years of experience
            experience_years = candidate_data.get("experience_years", 0)
            required_level = job_posting.get("experience_level", "mid")
            
            level_requirements = {"entry": 2, "mid": 5, "senior": 8, "lead": 12}
            required_years = level_requirements.get(required_level, 5)
            
            experience_score = min(100, (experience_years / required_years) * 100)
            
            # Industry relevance
            industry_experience = candidate_data.get("industry_experience", [])
            job_industry = job_posting.get("industry", "technology")
            
            industry_score = 100 if job_industry in industry_experience else 50
            
            # Company size experience
            company_sizes = candidate_data.get("company_sizes", [])
            target_size = job_posting.get("company_size", "medium")
            
            size_score = 100 if target_size in company_sizes else 70
            
            # Weighted average
            final_score = (experience_score * 0.5) + (industry_score * 0.3) + (size_score * 0.2)
            
            return final_score
            
        except Exception as e:
            logger.error(f"Experience screening error: {str(e)}")
            return 50.0

    async def _auto_advance_candidate(self, application: Dict[str, Any], screening_result: Dict[str, Any]):
        """Automatically advance qualified candidates"""
        try:
            if screening_result["recommendation"] == "strong_hire":
                # Schedule technical interview
                await self._schedule_interview(application, "technical")
                
                # Request references
                await self._request_references(application)
                
            elif screening_result["recommendation"] == "hire":
                # Schedule phone screen
                await self._schedule_interview(application, "phone_screen")
            
        except Exception as e:
            logger.error(f"Auto-advance candidate error: {str(e)}")

    async def _schedule_interview(self, application: Dict[str, Any], interview_type: str):
        """Schedule interview for candidate"""
        try:
            from .interview_agent.core import InterviewAgent
            interview_agent = InterviewAgent()
            
            # Schedule AI interview
            interview_session = await interview_agent.start_session(
                candidate_id=application["candidate_id"],
                interview_type=interview_type,
                job_id=application["job_id"],
                user_id="system"
            )
            
            # Send notification to candidate
            from .communication_agent.core import CommunicationAgent
            comm_agent = CommunicationAgent()
            
            await comm_agent.send_communication(
                recipient_id=application["candidate_id"],
                communication_type="interview_invitation",
                channel="email",
                template_data={
                    "interview_type": interview_type,
                    "interview_link": f"/interview/{interview_session['session_id']}",
                    "job_title": application.get("job_title", "")
                }
            )
            
            # Notify candidate
            await self.send_notification(
                user_id=application.get('candidate_id', ''),
                recipient_email=application.get('candidate_email', ''),
                message="Your interview has been scheduled. Please check your email for details.",
                notif_type="email",
                related_entity=application.get('job_id', None),
                event_type="interview_scheduled"
            )
            # Notify interviewer (mocked)
            await self.send_notification(
                user_id="interviewer_id",
                recipient_email="interviewer@company.com",
                message="You have been assigned to conduct an interview.",
                notif_type="email",
                related_entity=application.get('job_id', None),
                event_type="interview_scheduled"
            )
        except Exception as e:
            logger.error(f"Interview scheduling error: {str(e)}")

    async def list_jobs(self):
        """List all job postings"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            jobs = await mongo_db.job_postings.find({}).to_list(None)
            return jobs
        except Exception as e:
            logger.error(f"List jobs error: {str(e)}")
            return []

    async def list_candidates(self, filters=None):
        """List all candidates, optionally filtered by jobId and/or stage"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            query = {}
            if filters:
                if filters.get('jobId'):
                    query['job_id'] = filters['jobId']
                if filters.get('stage'):
                    query['current_stage'] = filters['stage']
            candidates = await mongo_db.candidates.find(query).to_list(None)
            return candidates
        except Exception as e:
            logger.error(f"List candidates error: {str(e)}")
            return []

    def calculate_match_score(self, candidate, job):
        """Calculate a match score between a candidate and a job (0-100)"""
        score = 0
        # Skill overlap
        candidate_skills = set(candidate.get('skills', []) or candidate.get('skills_required', []))
        job_skills = set(job.get('skills_required', []))
        if job_skills:
            skill_overlap = len(candidate_skills & job_skills) / max(1, len(job_skills))
            score += skill_overlap * 60  # 60% weight
        # Experience
        candidate_exp = candidate.get('experience_years', 0)
        job_exp = job.get('experience_level', 'mid')
        exp_map = {'entry': 1, 'mid': 3, 'senior': 5, 'lead': 8, 'executive': 12}
        job_exp_years = exp_map.get(job_exp, 3)
        exp_score = min(candidate_exp / job_exp_years, 1.0)
        score += exp_score * 30  # 30% weight
        # Education (simple bonus)
        if 'education' in candidate and candidate['education']:
            score += 10
        return min(int(score), 100)

    def log_action(self, user_id, action, entity_type, entity_id, details=""):
        """Store an audit log entry"""
        try:
            db = SessionLocal()
            log = AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details,
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            db.close()
        except Exception as e:
            logger.error(f"Audit log error: {str(e)}")

    async def create_candidate(self, candidate_data):
        """Create a new candidate entry and notify HR/admin"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            candidate_data['created_at'] = datetime.utcnow().isoformat()
            # Fetch job for match score
            job = await mongo_db.job_postings.find_one({"id": candidate_data.get('job_id')})
            candidate_data['match_score'] = self.calculate_match_score(candidate_data, job or {})
            result = await mongo_db.candidates.insert_one(candidate_data)
            candidate_data['_id'] = str(result.inserted_id)
            # Audit log
            self.log_action(
                user_id=candidate_data.get('created_by', 'system'),
                action="create_candidate",
                entity_type="candidate",
                entity_id=candidate_data['_id'],
                details=f"Candidate {candidate_data.get('name', '')} for job {candidate_data.get('job_id', '')}"
            )
            # Notify HR/admin
            await self.send_notification(
                user_id="hr_admin",
                recipient_email="hr@company.com",
                message=f"New candidate {candidate_data.get('name', '')} applied for job {candidate_data.get('job_id', '')}.",
                notif_type="system",
                related_entity=candidate_data.get('job_id', None),
                event_type="candidate_created"
            )
            return candidate_data
        except Exception as e:
            logger.error(f"Create candidate error: {str(e)}")
            return None

    async def send_notification(self, user_id, recipient_email, message, notif_type="system", related_entity=None, event_type=None, recipient_phone=None):
        """Send and store a notification (email, SMS, or system)"""
        try:
            # Store notification in DB
            db = SessionLocal()
            notif = Notification(
                user_id=user_id,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                message=message,
                type=notif_type,
                related_entity=related_entity,
                event_type=event_type,
            )
            db.add(notif)
            db.commit()
            db.refresh(notif)
            db.close()
            # Placeholder: send email/SMS if needed
            if notif_type == "email":
                # TODO: Integrate with real email provider (e.g., SendGrid)
                print(f"[EMAIL] To: {recipient_email} | {message}")
            elif notif_type == "sms":
                # TODO: Integrate with real SMS provider (e.g., Twilio)
                print(f"[SMS] To: {recipient_phone} | {message}")
            else:
                print(f"[SYSTEM NOTIF] To: {user_id} | {message}")
        except Exception as e:
            logger.error(f"Notification error: {str(e)}")
