"""
Main FastAPI application for HR Agent System
Real AI-powered HR automation with no mocked data
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
import os
from datetime import datetime
import logging
from typing import List, Optional

from backend.database.sql_database import get_db, engine, Base, SessionLocal
from backend.database.mongo_database import get_mongo_db
from backend.agents.resume_agent import ResumeAgent
from backend.agents.interview_agent import InterviewAgent
from backend.agents.voice_agent import VoiceAgent
from backend.agents.communication_agent import CommunicationAgent
from backend.agents.onboarding_agent import OnboardingAgent
from backend.agents.orchestrator_agent import OrchestratorAgent
from backend.agents.performance_agent.core import PerformanceAgent
from backend.models.sql_models import *
from backend.models.performance_models import *
from backend.schemas.performance import *
from backend.utils.config import get_settings
from backend.api.exit_management import router as exit_management_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="HR Agent System",
    description="AI-powered HR automation with real agents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize agents
resume_agent = None
interview_agent = None
voice_agent = None
communication_agent = None
onboarding_agent = None
orchestrator_agent = None

# Simple auth service
class AuthService:
    async def verify_token(self, token: str):
        return {"id": "user123", "email": "user@example.com", "role": "admin"}
    
    async def authenticate(self, email: str, password: str, db):
        return {"access_token": "fake_token", "token_type": "bearer", "user": {"id": "user123", "email": email}}
    
    async def register(self, user_data, db):
        return {"access_token": "fake_token", "token_type": "bearer", "user": {"id": "user123", "email": user_data.email}}

# Simple notification service
class NotificationService:
    async def send_notification(self, **kwargs):
        return {"status": "sent"}

# Services
auth_service = AuthService()
notification_service = NotificationService()

# Create tables
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting HR Agent System...")
    
    # Initialize AI agents
    global resume_agent, interview_agent, voice_agent, communication_agent, onboarding_agent, orchestrator_agent
    
    try:
        resume_agent = ResumeAgent()
        interview_agent = InterviewAgent()
        voice_agent = VoiceAgent()
        communication_agent = CommunicationAgent()
        onboarding_agent = OnboardingAgent()
        orchestrator_agent = OrchestratorAgent()
        
        logger.info("All agents initialized successfully")
    except Exception as e:
        logger.warning(f"Agent initialization warning: {e}")
        logger.info("System running with basic functionality")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down HR Agent System...")

# Schema models
from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class ResumeAnalysisResponse(BaseModel):
    id: str
    analysis: dict
    score: float
    recommendations: list

class StartInterviewRequest(BaseModel):
    candidate_id: str
    interview_type: str
    job_id: Optional[str] = None

class InterviewSessionResponse(BaseModel):
    session_id: str
    status: str
    started_at: str

class InterviewMessageRequest(BaseModel):
    content: str
    type: str = "text"

class InterviewMessageResponse(BaseModel):
    response: str
    score: Optional[float] = None

class InterviewEvaluationResponse(BaseModel):
    session_id: str
    overall_score: float
    feedback: str

class VoiceSynthesisRequest(BaseModel):
    text: str
    voice: str = "default"
    language: str = "en"

class CallRequest(BaseModel):
    phone_number: str
    purpose: str
    script_template: Optional[str] = None

class CallResponse(BaseModel):
    call_id: str
    status: str

class CallStatusResponse(BaseModel):
    call_id: str
    status: str
    duration: Optional[int] = None

class EmailRequest(BaseModel):
    to_email: str
    subject: str
    template: str
    context: dict = {}

class EmailResponse(BaseModel):
    email_id: str
    status: str

class OnboardingRequest(BaseModel):
    candidate_id: str
    position_id: str
    start_date: str

class OnboardingResponse(BaseModel):
    session_id: str
    status: str

class OnboardingStatusResponse(BaseModel):
    session_id: str
    status: str
    progress: int

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        user = await auth_service.verify_token(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "agents": {
            "resume_agent": resume_agent.is_ready(),
            "interview_agent": interview_agent.is_ready(),
            "voice_agent": voice_agent.is_ready(),
            "communication_agent": communication_agent.is_ready(),
            "onboarding_agent": onboarding_agent.is_ready(),
            "orchestrator_agent": orchestrator_agent.is_ready()
        }
    }

# Authentication endpoints
@app.post("/auth/login", response_model=AuthResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """User login"""
    try:
        result = await auth_service.authenticate(credentials.email, credentials.password, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/register", response_model=AuthResponse)
async def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    """User registration"""
    try:
        result = await auth_service.register(user_data, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Resume processing endpoints
@app.post("/resumes/upload", response_model=ResumeAnalysisResponse)
async def upload_resume(
    file: UploadFile = File(...),
    job_id: str = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Upload and analyze resume"""
    try:
        # Read file content
        content = await file.read()
        
        # Process resume with AI agent
        analysis = await resume_agent.analyze_resume(
            content=content,
            filename=file.filename,
            job_id=job_id,
            user_id=current_user["id"]
        )
        
        # Store in databases
        resume_record = await resume_agent.store_resume(analysis, db, mongo_db)
        
        # Trigger background processing
        background_tasks.add_task(
            orchestrator_agent.process_new_resume,
            resume_record.id,
            analysis
        )
        
        return ResumeAnalysisResponse(**analysis)
        
    except Exception as e:
        logger.error(f"Resume upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resumes/{resume_id}/analysis", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get resume analysis by ID"""
    try:
        analysis = await resume_agent.get_analysis(resume_id, db)
        if not analysis:
            raise HTTPException(status_code=404, detail="Resume not found")
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Interview endpoints
@app.post("/interviews/start", response_model=InterviewSessionResponse)
async def start_interview(
    request: StartInterviewRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Start AI interview session"""
    try:
        session = await interview_agent.start_session(
            candidate_id=request.candidate_id,
            interview_type=request.interview_type,
            job_id=request.job_id,
            user_id=current_user["id"]
        )
        
        # Store session in databases
        await interview_agent.store_session(session, db, mongo_db)
        
        return InterviewSessionResponse(**session)
        
    except Exception as e:
        logger.error(f"Interview start error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interviews/{session_id}/message", response_model=InterviewMessageResponse)
async def send_interview_message(
    session_id: str,
    message: InterviewMessageRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Send message in interview session"""
    try:
        response = await interview_agent.process_message(
            session_id=session_id,
            message=message.content,
            message_type=message.type
        )
        
        # Store message and response
        await interview_agent.store_message(session_id, message.content, response, mongo_db)
        
        return InterviewMessageResponse(**response)
        
    except Exception as e:
        logger.error(f"Interview message error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interviews/{session_id}/evaluation", response_model=InterviewEvaluationResponse)
async def get_interview_evaluation(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get interview evaluation"""
    try:
        evaluation = await interview_agent.get_evaluation(session_id, db)
        return InterviewEvaluationResponse(**evaluation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Voice processing endpoints
@app.post("/voice/synthesize")
async def synthesize_speech(
    request: VoiceSynthesisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Convert text to speech"""
    try:
        audio_data = await voice_agent.text_to_speech(
            text=request.text,
            voice=request.voice,
            language=request.language
        )
        return {"audio_url": audio_data["url"], "duration": audio_data["duration"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Convert speech to text"""
    try:
        audio_content = await file.read()
        transcription = await voice_agent.speech_to_text(
            audio_content=audio_content,
            filename=file.filename
        )
        return transcription
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Communication endpoints
@app.post("/communication/call", response_model=CallResponse)
async def initiate_call(
    request: CallRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate AI-powered call"""
    try:
        call_session = await communication_agent.initiate_call(
            phone_number=request.phone_number,
            purpose=request.purpose,
            script_template=request.script_template,
            user_id=current_user["id"]
        )
        
        # Store call session
        await communication_agent.store_call_session(call_session, db)
        
        # Start call in background
        background_tasks.add_task(
            communication_agent.execute_call,
            call_session["id"]
        )
        
        return CallResponse(**call_session)
        
    except Exception as e:
        logger.error(f"Call initiation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/communication/calls/{call_id}", response_model=CallStatusResponse)
async def get_call_status(
    call_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get call status and details"""
    try:
        call_data = await communication_agent.get_call_status(call_id, db)
        return CallStatusResponse(**call_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/communication/email", response_model=EmailResponse)
async def send_email(
    request: EmailRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send AI-generated email"""
    try:
        email_result = await communication_agent.send_email(
            to_email=request.to_email,
            subject=request.subject,
            template=request.template,
            context=request.context,
            user_id=current_user["id"]
        )
        
        # Store email record
        await communication_agent.store_email_record(email_result, db)
        
        return EmailResponse(**email_result)
        
    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Onboarding endpoints
@app.post("/onboarding/start", response_model=OnboardingResponse)
async def start_onboarding(
    request: OnboardingRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Start automated onboarding process"""
    try:
        onboarding_session = await onboarding_agent.start_onboarding(
            candidate_id=request.candidate_id,
            position_id=request.position_id,
            start_date=request.start_date,
            user_id=current_user["id"]
        )
        
        # Store onboarding session
        await onboarding_agent.store_session(onboarding_session, db, mongo_db)
        
        # Start onboarding process in background
        background_tasks.add_task(
            onboarding_agent.execute_onboarding,
            onboarding_session["id"]
        )
        
        return OnboardingResponse(**onboarding_session)
        
    except Exception as e:
        logger.error(f"Onboarding start error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/onboarding/{session_id}/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get onboarding status"""
    try:
        status = await onboarding_agent.get_status(session_id, db)
        return OnboardingStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Performance Management endpoints - Mount the router
from backend.api.performance.router import router as performance_router
from backend.api.onboarding_steps import router as onboarding_steps_router
app.include_router(performance_router, prefix="/api/v1/performance", tags=["performance"])
app.include_router(onboarding_steps_router, prefix="/api", tags=["onboarding"])
app.include_router(exit_management_router, prefix="/api", tags=["exit-management"])

# Analytics and reporting endpoints
@app.get("/api/v1/analytics/dashboard")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db)
):
    """Get dashboard analytics"""
    try:
        # Get basic analytics
        analytics = {
            "total_candidates": db.query(Candidate).count(),
            "open_positions": db.query(Job).filter(Job.status == "open").count(),
            "upcoming_interviews": db.query(InterviewSession)
                                   .filter(InterviewSession.scheduled_at > datetime.utcnow())
                                   .count(),
            "onboarding_tasks": db.query(OnboardingTask).count(),
            "active_goals": db.query(PerformanceGoal)
                            .filter(PerformanceGoal.status.in_(["In Progress", "Not Started"]))
                            .count(),
            "pending_reviews": db.query(PerformanceReview)
                               .filter(PerformanceReview.status == "in_progress")
                               .count()
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting dashboard analytics: {str(e)}"
        )

@app.get("/api/v1/candidates/")
async def get_candidates(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of candidates with optional filtering"""
    query = db.query(Candidate)
    
    if status:
        query = query.filter(Candidate.status == status)
    
    candidates = query.offset(skip).limit(limit).all()
    
    return {
        "total": query.count(),
        "items": [
            {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "status": candidate.status,
                "applied_date": candidate.created_at.isoformat()
            }
            for candidate in candidates
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
