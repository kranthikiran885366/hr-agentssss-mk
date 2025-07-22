"""
Conflict Resolution Agent - Automated workplace conflict detection and resolution
Uses AI to detect, analyze, and resolve workplace conflicts without human intervention
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import openai
from datetime import datetime, timedelta
import json
import uuid
import numpy as np
from textblob import TextBlob
import networkx as nx

from ..base_agent import BaseAgent
from .sentiment_analyzer import SentimentAnalyzer
from .mediation_engine import MediationEngine
from .resolution_tracker import ResolutionTracker
from backend.database.mongo_database import get_mongo_client
from backend.database.sql_database import SessionLocal
from models.sql_models import ConflictCase, Employee
from backend.utils.config import settings

logger = logging.getLogger(__name__)

class ConflictResolutionAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "conflict_resolution_agent"
        self.sentiment_analyzer = SentimentAnalyzer()
        self.mediation_engine = MediationEngine()
        self.resolution_tracker = ResolutionTracker()
        
        # Conflict types and severity levels
        self.conflict_types = {
            "interpersonal": {"severity_base": 3, "resolution_time": 7},
            "performance": {"severity_base": 4, "resolution_time": 14},
            "harassment": {"severity_base": 9, "resolution_time": 3},
            "discrimination": {"severity_base": 9, "resolution_time": 3},
            "workload": {"severity_base": 2, "resolution_time": 5},
            "communication": {"severity_base": 2, "resolution_time": 3},
            "resource": {"severity_base": 3, "resolution_time": 7},
            "policy_violation": {"severity_base": 6, "resolution_time": 5},
            "team_dynamics": {"severity_base": 4, "resolution_time": 10},
            "leadership": {"severity_base": 5, "resolution_time": 14}
        }
        
        # Resolution strategies
        self.resolution_strategies = {
            "mediation": {"success_rate": 0.75, "time_required": 3},
            "coaching": {"success_rate": 0.65, "time_required": 7},
            "training": {"success_rate": 0.70, "time_required": 14},
            "policy_clarification": {"success_rate": 0.80, "time_required": 2},
            "team_restructuring": {"success_rate": 0.85, "time_required": 21},
            "disciplinary_action": {"success_rate": 0.60, "time_required": 5},
            "counseling": {"success_rate": 0.70, "time_required": 10},
            "workflow_adjustment": {"success_rate": 0.75, "time_required": 7}
        }

    async def initialize(self):
        """Initialize conflict resolution agent"""
        try:
            logger.info("Initializing Conflict Resolution Agent...")
            await super().initialize()
            
            # Initialize OpenAI for conflict analysis
            openai.api_key = settings.OPENAI_API_KEY
            
            # Start automated monitoring
            asyncio.create_task(self._automated_conflict_monitoring())
            asyncio.create_task(self._automated_sentiment_monitoring())
            asyncio.create_task(self._automated_resolution_tracking())
            
            self.is_initialized = True
            logger.info("Conflict Resolution Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Conflict Resolution Agent: {str(e)}")
            raise

    async def detect_potential_conflicts(self, communication_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Automatically detect potential conflicts from communication patterns"""
        try:
            logger.info("Analyzing communication for potential conflicts...")
            
            conflict_indicators = {
                "high_risk_communications": [],
                "sentiment_deterioration": [],
                "communication_breakdowns": [],
                "escalation_patterns": [],
                "overall_risk_score": 0.0
            }
            
            for comm in communication_data:
                # Analyze sentiment
                sentiment_analysis = await self._analyze_communication_sentiment(comm)
                
                # Detect conflict keywords
                conflict_keywords = await self._detect_conflict_keywords(comm["content"])
                
                # Analyze communication patterns
                pattern_analysis = await self._analyze_communication_patterns(comm)
                
                # Calculate risk score
                risk_score = await self._calculate_conflict_risk_score(
                    sentiment_analysis, conflict_keywords, pattern_analysis
                )
                
                if risk_score > 0.7:  # High risk threshold
                    conflict_indicators["high_risk_communications"].append({
                        "communication_id": comm["id"],
                        "participants": comm["participants"],
                        "risk_score": risk_score,
                        "indicators": {
                            "sentiment": sentiment_analysis,
                            "keywords": conflict_keywords,
                            "patterns": pattern_analysis
                        },
                        "detected_at": datetime.utcnow().isoformat()
                    })
            
            # Calculate overall risk
            if conflict_indicators["high_risk_communications"]:
                conflict_indicators["overall_risk_score"] = np.mean([
                    comm["risk_score"] for comm in conflict_indicators["high_risk_communications"]
                ])
            
            # Auto-create conflict cases for high-risk situations
            if conflict_indicators["overall_risk_score"] > 0.8:
                await self._auto_create_conflict_cases(conflict_indicators)
            
            return conflict_indicators
            
        except Exception as e:
            logger.error(f"Conflict detection error: {str(e)}")
            raise

    async def create_conflict_case(self, reporter_id: str, involved_parties: List[str], 
                                 description: str, conflict_type: str) -> Dict[str, Any]:
        """Create and automatically process conflict case"""
        try:
            case_id = str(uuid.uuid4())
            
            # Analyze conflict severity
            severity_analysis = await self._analyze_conflict_severity(description, conflict_type)
            
            # Generate resolution plan
            resolution_plan = await self._generate_resolution_plan(
                conflict_type, severity_analysis, involved_parties
            )
            
            # Create conflict case
            conflict_case = {
                "id": case_id,
                "reporter_id": reporter_id,
                "involved_parties": involved_parties,
                "conflict_type": conflict_type,
                "description": description,
                "severity": severity_analysis["severity"],
                "priority": severity_analysis["priority"],
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "resolution_plan": resolution_plan,
                "timeline": resolution_plan["estimated_timeline"],
                "auto_generated": False,
                "resolution_progress": []
            }
            
            # Store conflict case
            await self._store_conflict_case(conflict_case)
            
            # Start automated resolution process
            await self._start_automated_resolution(conflict_case)
            
            # Send notifications
            await self._send_conflict_notifications(conflict_case)
            
            return conflict_case
            
        except Exception as e:
            logger.error(f"Conflict case creation error: {str(e)}")
            raise

    async def _analyze_conflict_severity(self, description: str, conflict_type: str) -> Dict[str, Any]:
        """Analyze conflict severity using AI"""
        try:
            # Base severity from conflict type
            base_severity = self.conflict_types.get(conflict_type, {}).get("severity_base", 5)
            
            # AI analysis of description
            prompt = f"""
            Analyze this workplace conflict description and rate its severity:
            
            Conflict Type: {conflict_type}
            Description: {description}
            
            Rate severity on scale 1-10 and provide:
            1. Severity score (1-10)
            2. Priority level (low/medium/high/critical)
            3. Urgency factors
            4. Potential impact
            5. Recommended immediate actions
            
            Return as JSON.
            """
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert HR conflict resolution specialist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            try:
                ai_analysis = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                ai_analysis = {"severity_score": base_severity, "priority": "medium"}
            
            # Combine base and AI analysis
            final_severity = (base_severity + ai_analysis.get("severity_score", base_severity)) / 2
            
            return {
                "severity": final_severity,
                "priority": ai_analysis.get("priority", "medium"),
                "urgency_factors": ai_analysis.get("urgency_factors", []),
                "potential_impact": ai_analysis.get("potential_impact", ""),
                "immediate_actions": ai_analysis.get("recommended_immediate_actions", [])
            }
            
        except Exception as e:
            logger.error(f"Severity analysis error: {str(e)}")
            return {"severity": 5, "priority": "medium"}

    async def _generate_resolution_plan(self, conflict_type: str, severity_analysis: Dict[str, Any], 
                                      involved_parties: List[str]) -> Dict[str, Any]:
        """Generate automated resolution plan"""
        try:
            # Select appropriate resolution strategies
            strategies = await self._select_resolution_strategies(conflict_type, severity_analysis)
            
            # Create timeline
            timeline = await self._create_resolution_timeline(strategies, severity_analysis)
            
            # Generate specific actions
            actions = await self._generate_resolution_actions(strategies, involved_parties)
            
            resolution_plan = {
                "strategies": strategies,
                "timeline": timeline,
                "actions": actions,
                "estimated_timeline": timeline["total_days"],
                "success_probability": np.mean([s["success_rate"] for s in strategies.values()]),
                "resource_requirements": await self._calculate_resource_requirements(strategies),
                "milestones": await self._create_resolution_milestones(timeline),
                "contingency_plans": await self._create_contingency_plans(conflict_type)
            }
            
            return resolution_plan
            
        except Exception as e:
            logger.error(f"Resolution plan generation error: {str(e)}")
            return {"strategies": [], "timeline": {"total_days": 14}}

    async def _select_resolution_strategies(self, conflict_type: str, severity_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Select appropriate resolution strategies using AI"""
        try:
            severity = severity_analysis["severity"]
            priority = severity_analysis["priority"]
            
            selected_strategies = {}
            
            # Strategy selection logic based on conflict type and severity
            if conflict_type in ["harassment", "discrimination"]:
                selected_strategies["investigation"] = {"success_rate": 0.90, "time_required": 5}
                selected_strategies["disciplinary_action"] = self.resolution_strategies["disciplinary_action"]
                selected_strategies["policy_clarification"] = self.resolution_strategies["policy_clarification"]
                
            elif conflict_type == "interpersonal":
                selected_strategies["mediation"] = self.resolution_strategies["mediation"]
                if severity > 6:
                    selected_strategies["coaching"] = self.resolution_strategies["coaching"]
                    
            elif conflict_type == "performance":
                selected_strategies["coaching"] = self.resolution_strategies["coaching"]
                selected_strategies["training"] = self.resolution_strategies["training"]
                
            elif conflict_type == "team_dynamics":
                selected_strategies["team_restructuring"] = self.resolution_strategies["team_restructuring"]
                selected_strategies["mediation"] = self.resolution_strategies["mediation"]
                
            elif conflict_type == "workload":
                selected_strategies["workflow_adjustment"] = self.resolution_strategies["workflow_adjustment"]
                selected_strategies["coaching"] = self.resolution_strategies["coaching"]
                
            else:
                # Default strategies
                selected_strategies["mediation"] = self.resolution_strategies["mediation"]
                selected_strategies["policy_clarification"] = self.resolution_strategies["policy_clarification"]
            
            # Add counseling for high-severity cases
            if severity > 7:
                selected_strategies["counseling"] = self.resolution_strategies["counseling"]
            
            return selected_strategies
            
        except Exception as e:
            logger.error(f"Strategy selection error: {str(e)}")
            return {"mediation": self.resolution_strategies["mediation"]}

    async def _start_automated_resolution(self, conflict_case: Dict[str, Any]):
        """Start automated resolution process"""
        try:
            case_id = conflict_case["id"]
            resolution_plan = conflict_case["resolution_plan"]
            
            # Execute immediate actions
            for action in resolution_plan.get("actions", {}).get("immediate", []):
                await self._execute_resolution_action(case_id, action)
            
            # Schedule follow-up actions
            for action in resolution_plan.get("actions", {}).get("scheduled", []):
                await self._schedule_resolution_action(case_id, action)
            
            # Start monitoring progress
            asyncio.create_task(self._monitor_resolution_progress(case_id))
            
        except Exception as e:
            logger.error(f"Automated resolution start error: {str(e)}")

    async def _execute_resolution_action(self, case_id: str, action: Dict[str, Any]):
        """Execute a specific resolution action"""
        try:
            action_type = action["type"]
            
            if action_type == "send_notification":
                await self._send_resolution_notification(action)
                
            elif action_type == "schedule_meeting":
                await self._schedule_resolution_meeting(action)
                
            elif action_type == "assign_mediator":
                await self._assign_automated_mediator(action)
                
            elif action_type == "create_training":
                await self._create_conflict_training(action)
                
            elif action_type == "policy_review":
                await self._initiate_policy_review(action)
                
            elif action_type == "documentation":
                await self._create_conflict_documentation(case_id, action)
            
            # Log action completion
            await self._log_resolution_action(case_id, action, "completed")
            
        except Exception as e:
            logger.error(f"Resolution action execution error: {str(e)}")
            await self._log_resolution_action(case_id, action, "failed", str(e))

    async def _automated_conflict_monitoring(self):
        """Automated background conflict monitoring"""
        while True:
            try:
                # Monitor communication patterns
                await self._monitor_communication_patterns()
                
                # Analyze team dynamics
                await self._analyze_team_dynamics()
                
                # Check for escalation patterns
                await self._check_escalation_patterns()
                
                # Update conflict predictions
                await self._update_conflict_predictions()
                
                # Sleep for 2 hours
                await asyncio.sleep(7200)
                
            except Exception as e:
                logger.error(f"Automated conflict monitoring error: {str(e)}")
                await asyncio.sleep(600)

    async def generate_conflict_insights(self, time_period: str = "30d") -> Dict[str, Any]:
        """Generate comprehensive conflict insights and analytics"""
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
            
            insights = {
                "period": time_period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "conflict_statistics": await self._calculate_conflict_statistics(start_date, end_date),
                "resolution_effectiveness": await self._analyze_resolution_effectiveness(start_date, end_date),
                "conflict_patterns": await self._identify_conflict_patterns(start_date, end_date),
                "prevention_opportunities": await self._identify_prevention_opportunities(),
                "team_health_scores": await self._calculate_team_health_scores(),
                "predictive_insights": await self._generate_predictive_insights(),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Conflict insights error: {str(e)}")
            return {"error": str(e)}

    # Helper methods
    async def _analyze_communication_sentiment(self, communication: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of communication"""
        try:
            content = communication.get("content", "")
            
            # Use TextBlob for basic sentiment
            blob = TextBlob(content)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "polarity": polarity,
                "subjectivity": subjectivity,
                "confidence": abs(polarity)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {"sentiment": "neutral", "polarity": 0, "confidence": 0}

    async def _detect_conflict_keywords(self, content: str) -> Dict[str, Any]:
        """Detect conflict-related keywords"""
        try:
            conflict_keywords = {
                "aggressive": ["angry", "furious", "hostile", "aggressive", "attack", "blame"],
                "negative": ["hate", "dislike", "terrible", "awful", "worst", "stupid"],
                "conflict": ["conflict", "dispute", "argument", "fight", "disagree", "oppose"],
                "harassment": ["harassment", "bullying", "intimidation", "threatening", "abuse"],
                "discrimination": ["discrimination", "bias", "unfair", "prejudice", "racist", "sexist"]
            }
            
            content_lower = content.lower()
            detected_keywords = {}
            
            for category, keywords in conflict_keywords.items():
                found = [kw for kw in keywords if kw in content_lower]
                if found:
                    detected_keywords[category] = found
            
            return {
                "detected_categories": list(detected_keywords.keys()),
                "keywords_by_category": detected_keywords,
                "total_keywords": sum(len(kws) for kws in detected_keywords.values()),
                "risk_level": "high" if len(detected_keywords) > 2 else "medium" if detected_keywords else "low"
            }
            
        except Exception as e:
            logger.error(f"Keyword detection error: {str(e)}")
            return {"detected_categories": [], "risk_level": "low"}

    async def _store_conflict_case(self, conflict_case: Dict[str, Any]):
        """Store conflict case in databases"""
        try:
            # Store in SQL
            db = SessionLocal()
            case_record = ConflictCase(
                id=conflict_case["id"],
                reporter_id=conflict_case["reporter_id"],
                conflict_type=conflict_case["conflict_type"],
                severity=conflict_case["severity"],
                status=conflict_case["status"],
                created_at=datetime.fromisoformat(conflict_case["created_at"])
            )
            db.add(case_record)
            db.commit()
            db.close()
            
            # Store detailed data in MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.conflict_cases.insert_one(conflict_case)
            
        except Exception as e:
            logger.error(f"Conflict case storage error: {str(e)}")
