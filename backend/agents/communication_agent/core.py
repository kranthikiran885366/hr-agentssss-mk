"""
Communication Agent - Automated communication and outreach
Handles emails, calls, SMS, and multi-channel communication
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import openai
from datetime import datetime, timedelta
import json
import uuid
import aiohttp
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import twilio
from twilio.rest import Client as TwilioClient

from ..base_agent import BaseAgent
from .email_engine import EmailEngine
from .voice_calling import VoiceCalling
from .sms_handler import SMSHandler
from .template_manager import TemplateManager
from backend.database.mongo_database import get_mongo_client
from backend.database.sql_database import SessionLocal
from models.sql_models import CommunicationLog, Employee, Candidate
from backend.utils.config import settings

logger = logging.getLogger(__name__)

class CommunicationAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "communication_agent"
        self.email_engine = EmailEngine()
        self.voice_calling = VoiceCalling()
        self.sms_handler = SMSHandler()
        self.template_manager = TemplateManager()
        
        # Communication channels
        self.channels = {
            "email": {"priority": 1, "delivery_time": "immediate"},
            "sms": {"priority": 2, "delivery_time": "immediate"},
            "voice": {"priority": 3, "delivery_time": "scheduled"},
            "slack": {"priority": 4, "delivery_time": "immediate"},
            "whatsapp": {"priority": 5, "delivery_time": "immediate"}
        }
        
        # Communication types
        self.communication_types = {
            "interview_invitation": {"urgency": "high", "follow_up": True},
            "offer_letter": {"urgency": "high", "follow_up": True},
            "rejection_notice": {"urgency": "medium", "follow_up": False},
            "onboarding_reminder": {"urgency": "medium", "follow_up": True},
            "performance_feedback": {"urgency": "low", "follow_up": False},
            "policy_update": {"urgency": "low", "follow_up": False},
            "emergency_notification": {"urgency": "critical", "follow_up": True}
        }

    async def initialize(self):
        """Initialize communication agent components"""
        try:
            logger.info("Initializing Communication Agent...")
            
            await super().initialize()
            
            # Initialize sub-components
            await self.email_engine.initialize()
            await self.voice_calling.initialize()
            await self.sms_handler.initialize()
            await self.template_manager.initialize()
            
            self.is_initialized = True
            logger.info("Communication Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Communication Agent: {str(e)}")
            raise

    async def send_communication(self, recipient_id: str, communication_type: str, 
                                channel: str = "email", template_data: Dict[str, Any] = None,
                                priority: str = "normal", schedule_time: datetime = None) -> Dict[str, Any]:
        """Send communication through specified channel"""
        try:
            communication_id = str(uuid.uuid4())
            
            # Get recipient information
            recipient_info = await self._get_recipient_info(recipient_id)
            
            # Get communication template
            template = await self.template_manager.get_template(communication_type, channel)
            
            # Personalize content
            personalized_content = await self._personalize_content(template, recipient_info, template_data)
            
            # Create communication record
            communication_record = {
                "id": communication_id,
                "recipient_id": recipient_id,
                "recipient_info": recipient_info,
                "communication_type": communication_type,
                "channel": channel,
                "priority": priority,
                "status": "pending",
                "content": personalized_content,
                "template_data": template_data,
                "created_at": datetime.utcnow().isoformat(),
                "scheduled_time": schedule_time.isoformat() if schedule_time else None,
                "delivery_attempts": 0,
                "delivery_status": "pending"
            }
            
            # Store communication record
            await self._store_communication_record(communication_record)
            
            # Send immediately or schedule
            if schedule_time and schedule_time > datetime.utcnow():
                await self._schedule_communication(communication_record)
                result = {"status": "scheduled", "scheduled_time": schedule_time.isoformat()}
            else:
                result = await self._execute_communication(communication_record)
            
            return {
                "communication_id": communication_id,
                "recipient": recipient_info.get("name", "Unknown"),
                "channel": channel,
                "type": communication_type,
                **result
            }
            
        except Exception as e:
            logger.error(f"Communication sending error: {str(e)}")
            raise

    async def _execute_communication(self, communication_record: Dict[str, Any]) -> Dict[str, Any]:
        """Execute communication based on channel"""
        try:
            channel = communication_record["channel"]
            content = communication_record["content"]
            recipient_info = communication_record["recipient_info"]
            
            # Update delivery attempt
            communication_record["delivery_attempts"] += 1
            communication_record["last_attempt_at"] = datetime.utcnow().isoformat()
            
            if channel == "email":
                result = await self.email_engine.send_email(
                    to_email=recipient_info.get("email"),
                    subject=content.get("subject"),
                    body=content.get("body"),
                    attachments=content.get("attachments", [])
                )
            elif channel == "sms":
                result = await self.sms_handler.send_sms(
                    to_phone=recipient_info.get("phone"),
                    message=content.get("message")
                )
            elif channel == "voice":
                result = await self.voice_calling.make_call(
                    to_phone=recipient_info.get("phone"),
                    script=content.get("script"),
                    call_type=communication_record["communication_type"]
                )
            elif channel == "slack":
                result = await self._send_slack_message(recipient_info, content)
            elif channel == "whatsapp":
                result = await self._send_whatsapp_message(recipient_info, content)
            else:
                raise ValueError(f"Unsupported channel: {channel}")
            
            # Update communication record
            communication_record["delivery_status"] = result.get("status", "failed")
            communication_record["delivery_details"] = result
            communication_record["delivered_at"] = datetime.utcnow().isoformat()
            
            if result.get("status") == "delivered":
                communication_record["status"] = "delivered"
                
                # Schedule follow-up if needed
                if self._should_schedule_followup(communication_record):
                    await self._schedule_followup(communication_record)
            else:
                communication_record["status"] = "failed"
                
                # Retry logic
                if communication_record["delivery_attempts"] < 3:
                    await self._schedule_retry(communication_record)
            
            # Update record
            await self._update_communication_record(communication_record)
            
            return result
            
        except Exception as e:
            logger.error(f"Communication execution error: {str(e)}")
            communication_record["status"] = "failed"
            communication_record["error"] = str(e)
            await self._update_communication_record(communication_record)
            return {"status": "failed", "error": str(e)}

    async def _personalize_content(self, template: Dict[str, Any], recipient_info: Dict[str, Any], 
                                 template_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Personalize communication content"""
        try:
            # Merge data sources
            data = {
                **recipient_info,
                **(template_data or {}),
                "current_date": datetime.utcnow().strftime("%B %d, %Y"),
                "current_time": datetime.utcnow().strftime("%I:%M %p")
            }
            
            personalized_content = {}
            
            # Personalize each content field
            for field, content in template.get("content", {}).items():
                if isinstance(content, str):
                    # Simple string replacement
                    personalized_content[field] = content.format(**data)
                elif isinstance(content, dict):
                    # Complex content with AI enhancement
                    personalized_content[field] = await self._enhance_content_with_ai(content, data)
                else:
                    personalized_content[field] = content
            
            return personalized_content
            
        except Exception as e:
            logger.error(f"Content personalization error: {str(e)}")
            return template.get("content", {})

    async def _enhance_content_with_ai(self, content_config: Dict[str, Any], data: Dict[str, Any]) -> str:
        """Enhance content using AI"""
        try:
            base_content = content_config.get("base", "")
            enhancement_type = content_config.get("enhancement", "personalize")
            
            if enhancement_type == "personalize":
                prompt = f"""
                Personalize this communication content:
                
                Base Content: {base_content}
                Recipient Data: {json.dumps(data, indent=2)}
                
                Make it more personal and engaging while maintaining professionalism.
                Keep the same tone and key information.
                """
            elif enhancement_type == "formal":
                prompt = f"""
                Make this content more formal and professional:
                
                Content: {base_content}
                Recipient: {data.get('name', 'Recipient')}
                
                Maintain all key information while improving formality.
                """
            elif enhancement_type == "friendly":
                prompt = f"""
                Make this content more friendly and approachable:
                
                Content: {base_content}
                Recipient: {data.get('name', 'Recipient')}
                
                Keep it professional but warm and welcoming.
                """
            else:
                return base_content.format(**data)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert communication specialist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            enhanced_content = response.choices[0].message.content.strip()
            return enhanced_content.format(**data)
            
        except Exception as e:
            logger.error(f"AI content enhancement error: {str(e)}")
            return content_config.get("base", "").format(**data)

    async def send_bulk_communication(self, recipient_ids: List[str], communication_type: str,
                                    channel: str = "email", template_data: Dict[str, Any] = None,
                                    batch_size: int = 50) -> Dict[str, Any]:
        """Send bulk communications with rate limiting"""
        try:
            bulk_id = str(uuid.uuid4())
            total_recipients = len(recipient_ids)
            
            # Create bulk communication record
            bulk_record = {
                "id": bulk_id,
                "communication_type": communication_type,
                "channel": channel,
                "total_recipients": total_recipients,
                "status": "processing",
                "created_at": datetime.utcnow().isoformat(),
                "results": {
                    "delivered": 0,
                    "failed": 0,
                    "pending": total_recipients
                },
                "individual_results": []
            }
            
            # Store bulk record
            await self._store_bulk_record(bulk_record)
            
            # Process in batches
            for i in range(0, total_recipients, batch_size):
                batch = recipient_ids[i:i + batch_size]
                
                # Process batch
                batch_tasks = []
                for recipient_id in batch:
                    task = self.send_communication(
                        recipient_id=recipient_id,
                        communication_type=communication_type,
                        channel=channel,
                        template_data=template_data
                    )
                    batch_tasks.append(task)
                
                # Execute batch
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Update results
                for result in batch_results:
                    if isinstance(result, Exception):
                        bulk_record["results"]["failed"] += 1
                        bulk_record["individual_results"].append({
                            "status": "failed",
                            "error": str(result)
                        })
                    else:
                        if result.get("status") == "delivered":
                            bulk_record["results"]["delivered"] += 1
                        else:
                            bulk_record["results"]["failed"] += 1
                        bulk_record["individual_results"].append(result)
                    
                    bulk_record["results"]["pending"] -= 1
                
                # Update bulk record
                await self._update_bulk_record(bulk_record)
                
                # Rate limiting delay
                await asyncio.sleep(1)
            
            # Finalize bulk communication
            bulk_record["status"] = "completed"
            bulk_record["completed_at"] = datetime.utcnow().isoformat()
            await self._update_bulk_record(bulk_record)
            
            return {
                "bulk_id": bulk_id,
                "total_recipients": total_recipients,
                "delivered": bulk_record["results"]["delivered"],
                "failed": bulk_record["results"]["failed"],
                "success_rate": (bulk_record["results"]["delivered"] / total_recipients) * 100
            }
            
        except Exception as e:
            logger.error(f"Bulk communication error: {str(e)}")
            return {"error": str(e)}

    async def create_automated_campaign(self, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create automated communication campaign"""
        try:
            campaign_id = str(uuid.uuid4())
            
            # Validate campaign configuration
            required_fields = ["name", "trigger_event", "communications", "target_audience"]
            for field in required_fields:
                if field not in campaign_config:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create campaign record
            campaign = {
                "id": campaign_id,
                "name": campaign_config["name"],
                "description": campaign_config.get("description", ""),
                "trigger_event": campaign_config["trigger_event"],
                "target_audience": campaign_config["target_audience"],
                "communications": campaign_config["communications"],
                "status": "active",
                "created_at": datetime.utcnow().isoformat(),
                "statistics": {
                    "triggered_count": 0,
                    "delivered_count": 0,
                    "failed_count": 0
                }
            }
            
            # Store campaign
            await self._store_campaign(campaign)
            
            # Set up event listeners
            await self._setup_campaign_triggers(campaign)
            
            return {
                "campaign_id": campaign_id,
                "name": campaign["name"],
                "status": "active",
                "trigger_event": campaign["trigger_event"]
            }
            
        except Exception as e:
            logger.error(f"Campaign creation error: {str(e)}")
            raise

    async def handle_campaign_trigger(self, event_type: str, event_data: Dict[str, Any]):
        """Handle campaign trigger events"""
        try:
            # Get active campaigns for this event type
            active_campaigns = await self._get_active_campaigns_for_event(event_type)
            
            for campaign in active_campaigns:
                # Check if event matches campaign criteria
                if await self._matches_campaign_criteria(campaign, event_data):
                    # Execute campaign communications
                    await self._execute_campaign_communications(campaign, event_data)
                    
                    # Update campaign statistics
                    campaign["statistics"]["triggered_count"] += 1
                    await self._update_campaign(campaign)
            
        except Exception as e:
            logger.error(f"Campaign trigger handling error: {str(e)}")

    async def _execute_campaign_communications(self, campaign: Dict[str, Any], event_data: Dict[str, Any]):
        """Execute campaign communications sequence"""
        try:
            communications = campaign.get("communications", [])
            recipient_id = event_data.get("recipient_id") or event_data.get("employee_id") or event_data.get("candidate_id")
            
            if not recipient_id:
                logger.warning("No recipient ID found in event data")
                return
            
            for comm_config in communications:
                # Calculate delay if specified
                delay = comm_config.get("delay_hours", 0)
                if delay > 0:
                    schedule_time = datetime.utcnow() + timedelta(hours=delay)
                else:
                    schedule_time = None
                
                # Send communication
                result = await self.send_communication(
                    recipient_id=recipient_id,
                    communication_type=comm_config["type"],
                    channel=comm_config.get("channel", "email"),
                    template_data={**event_data, **comm_config.get("template_data", {})},
                    priority=comm_config.get("priority", "normal"),
                    schedule_time=schedule_time
                )
                
                # Update campaign statistics
                if result.get("status") == "delivered":
                    campaign["statistics"]["delivered_count"] += 1
                else:
                    campaign["statistics"]["failed_count"] += 1
            
        except Exception as e:
            logger.error(f"Campaign communications execution error: {str(e)}")

    async def get_communication_analytics(self, time_period: str = "30d") -> Dict[str, Any]:
        """Get communication analytics and insights"""
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
            
            # Get communication data
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            
            # Aggregate communication statistics
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
                        "_id": {
                            "channel": "$channel",
                            "type": "$communication_type",
                            "status": "$delivery_status"
                        },
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            results = await mongo_db.communication_logs.aggregate(pipeline).to_list(None)
            
            # Process analytics
            analytics = {
                "period": time_period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_communications": 0,
                "by_channel": {},
                "by_type": {},
                "delivery_rates": {},
                "trends": await self._calculate_communication_trends(start_date, end_date)
            }
            
            for result in results:
                channel = result["_id"]["channel"]
                comm_type = result["_id"]["type"]
                status = result["_id"]["status"]
                count = result["count"]
                
                analytics["total_communications"] += count
                
                # By channel
                if channel not in analytics["by_channel"]:
                    analytics["by_channel"][channel] = {"total": 0, "delivered": 0, "failed": 0}
                analytics["by_channel"][channel]["total"] += count
                analytics["by_channel"][channel][status] += count
                
                # By type
                if comm_type not in analytics["by_type"]:
                    analytics["by_type"][comm_type] = {"total": 0, "delivered": 0, "failed": 0}
                analytics["by_type"][comm_type]["total"] += count
                analytics["by_type"][comm_type][status] += count
            
            # Calculate delivery rates
            for channel, stats in analytics["by_channel"].items():
                if stats["total"] > 0:
                    analytics["delivery_rates"][channel] = (stats["delivered"] / stats["total"]) * 100
            
            return analytics
            
        except Exception as e:
            logger.error(f"Communication analytics error: {str(e)}")
            return {"error": str(e)}

    # Helper methods
    async def _get_recipient_info(self, recipient_id: str) -> Dict[str, Any]:
        """Get recipient information"""
        try:
            # Try employee first
            db = SessionLocal()
            employee = db.query(Employee).filter(Employee.id == recipient_id).first()
            if employee:
                db.close()
                return {
                    "id": employee.id,
                    "name": employee.name,
                    "email": employee.email,
                    "phone": employee.phone,
                    "type": "employee",
                    "department": employee.department
                }
            
            # Try candidate
            candidate = db.query(Candidate).filter(Candidate.id == recipient_id).first()
            if candidate:
                db.close()
                return {
                    "id": candidate.id,
                    "name": candidate.name,
                    "email": candidate.email,
                    "phone": candidate.phone,
                    "type": "candidate"
                }
            
            db.close()
            return {}
        except Exception as e:
            logger.error(f"Recipient info retrieval error: {str(e)}")
            return {}

    async def _store_communication_record(self, record: Dict[str, Any]):
        """Store communication record"""
        try:
            # Store in SQL
            db = SessionLocal()
            comm_log = CommunicationLog(
                id=record["id"],
                recipient_id=record["recipient_id"],
                communication_type=record["communication_type"],
                channel=record["channel"],
                status=record["status"],
                created_at=datetime.fromisoformat(record["created_at"])
            )
            db.add(comm_log)
            db.commit()
            db.close()
            
            # Store detailed data in MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.communication_logs.insert_one(record)
            
        except Exception as e:
            logger.error(f"Communication record storage error: {str(e)}")

    async def _update_communication_record(self, record: Dict[str, Any]):
        """Update communication record"""
        try:
            # Update SQL
            db = SessionLocal()
            comm_log = db.query(CommunicationLog).filter(CommunicationLog.id == record["id"]).first()
            if comm_log:
                comm_log.status = record["status"]
                comm_log.delivery_status = record.get("delivery_status")
                if record.get("delivered_at"):
                    comm_log.delivered_at = datetime.fromisoformat(record["delivered_at"])
                db.commit()
            db.close()
            
            # Update MongoDB
            mongo_client = get_mongo_client()
            mongo_db = mongo_client.hr_system
            await mongo_db.communication_logs.replace_one(
                {"id": record["id"]},
                record
            )
            
        except Exception as e:
            logger.error(f"Communication record update error: {str(e)}")
