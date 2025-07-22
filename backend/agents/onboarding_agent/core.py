"""
Onboarding Agent - Complete automated employee onboarding
Handles document collection, account creation, training assignment, and integration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import openai
from datetime import datetime, timedelta
import json
import uuid
import aiohttp

from ..base_agent import BaseAgent
from .document_processor import DocumentProcessor
from .account_creator import AccountCreator
from .training_scheduler import TrainingScheduler
from .integration_manager import IntegrationManager
from backend.database.mongo_database import get_mongo_client
from backend.database.sql_database import SessionLocal
from models.sql_models import OnboardingSession, Employee, Candidate
from backend.utils.config import settings

logger = logging.getLogger(__name__)

class OnboardingAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "onboarding_agent"
        self.document_processor = DocumentProcessor()
        self.account_creator = AccountCreator()
        self.training_scheduler = TrainingScheduler()
        self.integration_manager = IntegrationManager()
        
        # Onboarding workflow steps
        self.workflow_steps = {
            "document_collection": {
                "order": 1,
                "required": True,
                "estimated_time": 30,
                "dependencies": []
            },
            "document_verification": {
                "order": 2,
                "required": True,
                "estimated_time": 15,
                "dependencies": ["document_collection"]
            },
            "account_creation": {
                "order": 3,
                "required": True,
                "estimated_time": 20,
                "dependencies": ["document_verification"]
            },
            "system_access_setup": {
                "order": 4,
                "required": True,
                "estimated_time": 25,
                "dependencies": ["account_creation"]
            },
            "training_assignment": {
                "order": 5,
                "required": True,
                "estimated_time": 10,
                "dependencies": ["system_access_setup"]
            },
            "mentor_assignment": {
                "order": 6,
                "required": False,
                "estimated_time": 5,
                "dependencies": ["training_assignment"]
            },
            "workspace_setup": {
                "order": 7,
                "required": True,
                "estimated_time": 15,
                "dependencies": ["system_access_setup"]
            },
            "equipment_provisioning": {
                "order": 8,
                "required": True,
                "estimated_time": 20,
                "dependencies": ["workspace_setup"]
            },
            "policy_acknowledgment": {
                "order": 9,
                "required": True,
                "estimated_time": 10,
                "dependencies": ["equipment_provisioning"]
            },
            "benefits_enrollment": {
                "order": 10,
                "required": True,
                "estimated_time": 20,
                "dependencies": ["policy_acknowledgment"]
            },
            "welcome_orientation": {
                "order": 11,
                "required": True,
                "estimated_time": 60,
                "dependencies": ["benefits_enrollment", "training_assignment"]
            },
            "completion": {
                "order": 12,
                "required": True,
                "estimated_time": 5,
                "dependencies": ["welcome_orientation"]
            }
        }
        
        # Required documents by role
        self.required_documents = {
            "all_roles": [
                "government_id", "address_proof", "bank_details", 
                "emergency_contact", "tax_forms"
            ],
            "technical": [
                "degree_certificate", "experience_certificates", "portfolio"
            ],
            "management": [
                "degree_certificate", "experience_certificates", "references"
            ],
            "intern": [
                "student_id", "university_letter", "emergency_contact"
            ]
        }

    async def initialize(self):
        """Initialize onboarding agent components"""
        try:
            logger.info("Initializing Onboarding Agent...")
            
            await super().initialize()
            
            # Initialize sub-components
            await self.document_processor.initialize()
            await self.account_creator.initialize()
            await self.training_scheduler.initialize()
            await self.integration_manager.initialize()
            
            self.is_initialized = True
            logger.info("Onboarding Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Onboarding Agent: {str(e)}")
            raise

    async def start_onboarding_process(self, candidate_id: str, position_id: str, 
                                     start_date: str, hiring_manager_id: str = None) -> Dict[str, Any]:
        """Start comprehensive onboarding process"""
        try:
            session_id = str(uuid.uuid4())
            
            # Get candidate and position information
            candidate_info = await self._get_candidate_info(candidate_id)
            position_info = await self._get_position_info(position_id)
            
            # Determine required documents based on role
            required_docs = await self._determine_required_documents(position_info)
            
            # Create onboarding session
            session_data = {
                "id": session_id,
                "candidate_id": candidate_id,
                "position_id": position_id,
                "hiring_manager_id": hiring_manager_id,
                "start_date": start_date,
                "status": "initiated",
                "current_step": "document_collection",
                "created_at": datetime.utcnow().isoformat(),
                "candidate_info": candidate_info,
                "position_info": position_info,
                "required_documents": required_docs,
                "workflow_progress": {
                    step: {"status": "pending", "started_at": None, "completed_at": None}
                    for step in self.workflow_steps.keys()
                },
                "documents": {},
                "accounts_created": {},
                "training_assigned": [],
                "mentor_assigned": None,
                "completion_percentage": 0.0
            }
            
            # Store session
            await self._store_onboarding_session(session_data)
            
            # Send welcome email with onboarding portal link
            await self._send_onboarding_welcome(session_data)
            
            # Start first step
            await self._start_workflow_step(session_data, "document_collection")
            
            return {
                "session_id": session_id,
                "status": "initiated",
                "onboarding_portal_url": f"{settings.FRONTEND_URL}/onboarding/{session_id}",
                "estimated_completion_time": await self._calculate_estimated_completion(session_data),
                "next_steps": await self._get_next_steps(session_data),
                "required_documents": required_docs
            }
            
        except Exception as e:
            logger.error(f"Onboarding process start error: {str(e)}")
            raise

    async def process_document_submission(self, session_id: str, document_type: str, 
                                        document_data: bytes, filename: str) -> Dict[str, Any]:
        """Process submitted onboarding document"""
        try:
            # Get session data
            session_data = await self._get_onboarding_session(session_id)
            if not session_data:
                raise ValueError("Onboarding session not found")
            
            # Process document
            processing_result = await self.document_processor.process_document(
                document_type=document_type,
                document_data=document_data,
                filename=filename,
                session_context=session_data
            )
            
            # Store document information
            session_data["documents"][document_type] = {
                "filename": filename,
                "uploaded_at": datetime.utcnow().isoformat(),
                "verification_status": processing_result.get("verification_status", "pending"),
                "verification_details": processing_result.get("verification_details", {}),
                "extracted_data": processing_result.get("extracted_data", {}),
                "file_path": processing_result.get("file_path", "")
            }
            
            # Check if all required documents are submitted
            all_docs_submitted = await self._check_document_completeness(session_data)
            
            if all_docs_submitted:
                # Move to document verification step
                await self._complete_workflow_step(session_data, "document_collection")
                await self._start_workflow_step(session_data, "document_verification")
                
                # Start automated verification process
                await self._start_document_verification(session_data)
            
            # Update session
            await self._update_onboarding_session(session_data)
            
            return {
                "document_type": document_type,
                "verification_status": processing_result.get("verification_status", "pending"),
                "all_documents_submitted": all_docs_submitted,
                "next_steps": await self._get_next_steps(session_data),
                "completion_percentage": await self._calculate_completion_percentage(session_data)
            }
            
        except Exception as e:
            logger.error(f"Document submission processing error: {str(e)}")
            raise

    async def _start_document_verification(self, session_data: Dict[str, Any]):
        """Start automated document verification process"""
        try:
            verification_tasks = []
            
            for doc_type, doc_info in session_data["documents"].items():
                if doc_info.get("verification_status") == "pending":
                    task = self.document_processor.verify_document(
                        document_type=doc_type,
                        document_info=doc_info,
                        session_context=session_data
                    )
                    verification_tasks.append(task)
            
            # Execute verification tasks
            verification_results = await asyncio.gather(*verification_tasks, return_exceptions=True)
            
            # Process results
            all_verified = True
            for i, result in enumerate(verification_results):
                if isinstance(result, Exception):
                    logger.error(f"Document verification error: {str(result)}")
                    all_verified = False
                else:
                    doc_type = list(session_data["documents"].keys())[i]
                    session_data["documents"][doc_type]["verification_status"] = result.get("status", "failed")
                    session_data["documents"][doc_type]["verification_details"] = result.get("details", {})
                    
                    if result.get("status") != "verified":
                        all_verified = False
            
            if all_verified:
                # All documents verified, proceed to account creation
                await self._complete_workflow_step(session_data, "document_verification")
                await self._start_workflow_step(session_data, "account_creation")
                await self._start_account_creation(session_data)
            else:
                # Some documents failed verification, notify candidate
                await self._handle_verification_failures(session_data)
            
        except Exception as e:
            logger.error(f"Document verification start error: {str(e)}")

    async def _start_account_creation(self, session_data: Dict[str, Any]):
        """Start automated account creation process"""
        try:
            candidate_info = session_data["candidate_info"]
            position_info = session_data["position_info"]
            
            # Determine required accounts based on role
            required_accounts = await self._determine_required_accounts(position_info)
            
            account_creation_tasks = []
            
            for account_type in required_accounts:
                task = self.account_creator.create_account(
                    account_type=account_type,
                    user_info=candidate_info,
                    position_info=position_info,
                    session_context=session_data
                )
                account_creation_tasks.append((account_type, task))
            
            # Execute account creation
            for account_type, task in account_creation_tasks:
                try:
                    result = await task
                    session_data["accounts_created"][account_type] = {
                        "status": "created",
                        "account_details": result,
                        "created_at": datetime.utcnow().isoformat()
                    }
                except Exception as e:
                    logger.error(f"Account creation error for {account_type}: {str(e)}")
                    session_data["accounts_created"][account_type] = {
                        "status": "failed",
                        "error": str(e),
                        "created_at": datetime.utcnow().isoformat()
                    }
            
            # Check if all accounts created successfully
            all_accounts_created = all(
                acc_info.get("status") == "created" 
                for acc_info in session_data["accounts_created"].values()
            )
            
            if all_accounts_created:
                # Proceed to system access setup
                await self._complete_workflow_step(session_data, "account_creation")
                await self._start_workflow_step(session_data, "system_access_setup")
                await self._setup_system_access(session_data)
            else:
                # Handle account creation failures
                await self._handle_account_creation_failures(session_data)
            
        except Exception as e:
            logger.error(f"Account creation start error: {str(e)}")

    async def _setup_system_access(self, session_data: Dict[str, Any]):
        """Setup system access and permissions"""
        try:
            candidate_info = session_data["candidate_info"]
            position_info = session_data["position_info"]
            accounts_created = session_data["accounts_created"]
            
            # Setup access for each system
            access_setup_results = {}
            
            for account_type, account_info in accounts_created.items():
                if account_info.get("status") == "created":
                    access_result = await self.integration_manager.setup_system_access(
                        system_type=account_type,
                        account_details=account_info["account_details"],
                        user_info=candidate_info,
                        position_info=position_info
                    )
                    access_setup_results[account_type] = access_result
            
            # Store access setup results
            session_data["system_access"] = access_setup_results
            
            # Check if all access setup completed
            all_access_setup = all(
                result.get("status") == "completed" 
                for result in access_setup_results.values()
            )
            
            if all_access_setup:
                # Proceed to training assignment
                await self._complete_workflow_step(session_data, "system_access_setup")
                await self._start_workflow_step(session_data, "training_assignment")
                await self._assign_training(session_data)
            else:
                # Handle access setup failures
                await self._handle_access_setup_failures(session_data)
            
        except Exception as e:
            logger.error(f"System access setup error: {str(e)}")

    async def _assign_training(self, session_data: Dict[str, Any]):
        """Assign training modules and courses"""
        try:
            position_info = session_data["position_info"]
            candidate_info = session_data["candidate_info"]
            
            # Determine required training based on role
            required_training = await self._determine_required_training(position_info)
            
            # Assign training modules
            training_assignments = []
            
            for training_module in required_training:
                assignment_result = await self.training_scheduler.assign_training(
                    module_id=training_module["id"],
                    user_info=candidate_info,
                    position_info=position_info,
                    session_context=session_data
                )
                training_assignments.append(assignment_result)
            
            session_data["training_assigned"] = training_assignments
            
            # Complete training assignment step
            await self._complete_workflow_step(session_data, "training_assignment")
            
            # Start mentor assignment (optional)
            await self._start_workflow_step(session_data, "mentor_assignment")
            await self._assign_mentor(session_data)
            
        except Exception as e:
            logger.error(f"Training assignment error: {str(e)}")

    async def _assign_mentor(self, session_data: Dict[str, Any]):
        """Assign mentor to new employee"""
        try:
            position_info = session_data["position_info"]
            candidate_info = session_data["candidate_info"]
            
            # Find suitable mentor
            mentor = await self._find_suitable_mentor(position_info, candidate_info)
            
            if mentor:
                # Assign mentor
                mentor_assignment = await self.integration_manager.assign_mentor(
                    mentor_info=mentor,
                    mentee_info=candidate_info,
                    session_context=session_data
                )
                session_data["mentor_assigned"] = mentor_assignment
            
            # Complete mentor assignment step
            await self._complete_workflow_step(session_data, "mentor_assignment")
            
            # Start workspace setup
            await self._start_workflow_step(session_data, "workspace_setup")
            await self._setup_workspace(session_data)
            
        except Exception as e:
            logger.error(f"Mentor assignment error: {str(e)}")

    async def _setup_workspace(self, session_data: Dict[str, Any]):
        """Setup physical and digital workspace"""
        try:
            candidate_info = session_data["candidate_info"]
            position_info = session_data["position_info"]
            
            # Setup digital workspace
            workspace_setup = await self.integration_manager.setup_workspace(
                user_info=candidate_info,
                position_info=position_info,
                session_context=session_data
            )
            
            session_data["workspace_setup"] = workspace_setup
            
            # Complete workspace setup
            await self._complete_workflow_step(session_data, "workspace_setup")
            
            # Start welcome orientation
            await self._start_workflow_step(session_data, "welcome_orientation")
            await self._schedule_welcome_orientation(session_data)
            
        except Exception as e:
            logger.error(f"Workspace setup error: {str(e)}")

    async def _schedule_welcome_orientation(self, session_data: Dict[str, Any]):
        """Schedule welcome orientation session"""
        try:
            candidate_info = session_data["candidate_info"]
            start_date = datetime.fromisoformat(session_data["start_date"])
            
            # Schedule orientation for first day
            orientation_result = await self.integration_manager.schedule_orientation(
                user_info=candidate_info,
                orientation_date=start_date,
                session_context=session_data
            )
            
            session_data["welcome_orientation"] = orientation_result
            
            # Complete welcome orientation step
            await self._complete_workflow_step(session_data, "welcome_orientation")
            
            # Mark onboarding as completed
            session_data["status"] = "completed"
            session_data["completed_at"] = datetime.utcnow().isoformat()
            session_data["completion_percentage"] = 100.0
            
            # Send completion notification
            await self._send_onboarding_completion_notification(session_data)
            
        except Exception as e:
            logger.error(f"Welcome orientation scheduling error: {str(e)}")

    async def get_onboarding_status(self, session_id: str) -> Dict[str, Any]:
        """Get current onboarding status"""
        try:
            session_data = await self._get_onboarding_session(session_id)
            if not session_data:
                return {"error": "Session not found"}
            
            return {
                "session_id": session_id,
                "status": session_data.get("status"),
                "current_step": session_data.get("current_step"),
                "completion_percentage": await self._calculate_completion_percentage(session_data),
                "workflow_progress": session_data.get("workflow_progress", {}),
                "next_steps": await self._get_next_steps(session_data),
                "estimated_completion": await self._calculate_estimated_completion(session_data),
                "documents_status": await self._get_documents_status(session_data),
                "accounts_status": await self._get_accounts_status(session_data)
            }
            
        except Exception as e:
            logger.error(f"Onboarding status retrieval error: {str(e)}")
            return {"error": str(e)}

    async def get_onboarding_analytics(self, time_period: str = "30d") -> Dict[str, Any]:
        """Get onboarding analytics and insights"""
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
            
            # Get onboarding data
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            
            # Aggregate onboarding statistics
            pipeline = [
                {
                    "$match": {
                        "created_at": {
                            "$gte": start_date.isoformat(),
                            "$lte": end_date.isoformat()
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1},
                        "avg_completion_time": {"$avg": "$completion_time_hours"}
                    }
                }
            ]
            
            results = await mongo_db.onboarding_sessions.aggregate(pipeline).to_list(None)
            
            # Calculate analytics
            analytics = {
                "period": time_period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_onboardings": sum(result["count"] for result in results),
                "completion_rate": 0.0,
                "average_completion_time": 0.0,
                "status_breakdown": {},
                "bottlenecks": await self._identify_onboarding_bottlenecks(start_date, end_date),
                "trends": await self._calculate_onboarding_trends(start_date, end_date)
            }
            
            completed_count = 0
            total_completion_time = 0
            
            for result in results:
                status = result["_id"]
                count = result["count"]
                analytics["status_breakdown"][status] = count
                
                if status == "completed":
                    completed_count = count
                    total_completion_time = result.get("avg_completion_time", 0)
            
            if analytics["total_onboardings"] > 0:
                analytics["completion_rate"] = (completed_count / analytics["total_onboardings"]) * 100
            
            analytics["average_completion_time"] = total_completion_time
            
            return analytics
            
        except Exception as e:
            logger.error(f"Onboarding analytics error: {str(e)}")
            return {"error": str(e)}

    # Helper methods
    async def _get_candidate_info(self, candidate_id: str) -> Dict[str, Any]:
        """Get candidate information"""
        try:
            db = SessionLocal()
            candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
            db.close()
            
            if candidate:
                return {
                    "id": candidate.id,
                    "name": candidate.name,
                    "email": candidate.email,
                    "phone": candidate.phone,
                    "status": candidate.status
                }
            return {}
        except Exception as e:
            logger.error(f"Candidate info retrieval error: {str(e)}")
            return {}

    async def _determine_required_documents(self, position_info: Dict[str, Any]) -> List[str]:
        """Determine required documents based on position"""
        try:
            role_category = position_info.get("category", "all_roles")
            required_docs = self.required_documents.get("all_roles", []).copy()
            
            if role_category in self.required_documents:
                required_docs.extend(self.required_documents[role_category])
            
            return list(set(required_docs))  # Remove duplicates
        except Exception as e:
            logger.error(f"Required documents determination error: {str(e)}")
            return self.required_documents["all_roles"]

    async def _store_onboarding_session(self, session_data: Dict[str, Any]):
        """Store onboarding session"""
        try:
            # Store in SQL
            db = SessionLocal()
            onboarding_session = OnboardingSession(
                id=session_data["id"],
                candidate_id=session_data["candidate_id"],
                position_id=session_data["position_id"],
                status=session_data["status"],
                current_step=session_data["current_step"],
                start_date=datetime.fromisoformat(session_data["start_date"]),
                created_at=datetime.fromisoformat(session_data["created_at"]),
                completion_percentage=session_data["completion_percentage"]
            )
            db.add(onboarding_session)
            db.commit()
            db.close()
            
            # Store detailed data in MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.onboarding_sessions.insert_one(session_data)
            
        except Exception as e:
            logger.error(f"Onboarding session storage error: {str(e)}")

    async def _get_onboarding_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get onboarding session data"""
        try:
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            session_data = await mongo_db.onboarding_sessions.find_one({"id": session_id})
            return session_data
        except Exception as e:
            logger.error(f"Onboarding session retrieval error: {str(e)}")
            return None

    async def _update_onboarding_session(self, session_data: Dict[str, Any]):
        """Update onboarding session"""
        try:
            # Update SQL
            db = SessionLocal()
            onboarding_session = db.query(OnboardingSession).filter(OnboardingSession.id == session_data["id"]).first()
            if onboarding_session:
                onboarding_session.status = session_data["status"]
                onboarding_session.current_step = session_data["current_step"]
                onboarding_session.completion_percentage = session_data["completion_percentage"]
                if session_data.get("completed_at"):
                    onboarding_session.completed_at = datetime.fromisoformat(session_data["completed_at"])
                db.commit()
            db.close()
            
            # Update MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.onboarding_sessions.replace_one(
                {"id": session_data["id"]},
                session_data
            )
            
        except Exception as e:
            logger.error(f"Onboarding session update error: {str(e)}")

    # Placeholder methods for new steps
    async def _provision_equipment(self, session_data):
        # Logic for provisioning equipment (laptop, phone, etc.)
        pass

    async def _acknowledge_policies(self, session_data):
        # Logic for policy acknowledgment (handbook, code of conduct, etc.)
        pass

    async def _enroll_benefits(self, session_data):
        # Logic for benefits enrollment (health, dental, etc.)
        pass
