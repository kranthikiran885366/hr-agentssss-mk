"""
SQL Database Models
Structured data models for PostgreSQL
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, hr, candidate, mentor
    department = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = relationship("Resume", back_populates="user")
    interview_sessions = relationship("InterviewSession", back_populates="interviewer")
    call_logs = relationship("CallLog", back_populates="user")
    performance_goals = relationship("PerformanceGoal", back_populates="employee")
    given_reviews = relationship("PerformanceReview", 
                              foreign_keys="[PerformanceReview.reviewer_id]", 
                              back_populates="reviewer")
    received_reviews = relationship("PerformanceReview", 
                                  foreign_keys="[PerformanceReview.employee_id]", 
                                  back_populates="employee")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    department = Column(String)
    location = Column(String)
    employment_type = Column(String)  # full-time, part-time, contract
    salary_range = Column(String)
    status = Column(String, default="active")  # active, closed, draft
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Approval workflow fields
    approval_status = Column(String, default="pending_approval")  # pending_approval, approved, rejected
    approvers = Column(JSON, default=list)  # List of user IDs who must approve
    approval_history = Column(JSON, default=list)  # List of {approver_id, action, timestamp, comment}
    
    # Relationships
    resumes = relationship("Resume", back_populates="job")
    interview_sessions = relationship("InterviewSession", back_populates="job")
    candidates = relationship("Candidate", back_populates="job")

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String)
    status = Column(String, default="applied")  # applied, screening, interviewing, hired, rejected
    job_id = Column(String, ForeignKey("jobs.id"))
    source = Column(String)  # website, referral, linkedin, etc.
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="candidates")
    resumes = relationship("Resume", back_populates="candidate")
    interview_sessions = relationship("InterviewSession", back_populates="candidate")
    onboarding_sessions = relationship("OnboardingSession", back_populates="candidate")

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    candidate_id = Column(String, ForeignKey("candidates.id"))
    job_id = Column(String, ForeignKey("jobs.id"))
    user_id = Column(String, ForeignKey("users.id"))
    overall_score = Column(Float, default=0.0)
    technical_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    cultural_fit_score = Column(Float, default=0.0)
    status = Column(String, default="analyzed")  # uploaded, analyzing, analyzed, reviewed
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")
    job = relationship("Job", back_populates="resumes")
    user = relationship("User", back_populates="resumes")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    recipient_email = Column(String, index=True)
    recipient_phone = Column(String, index=True, nullable=True)
    message = Column(Text)
    type = Column(String)  # e.g., 'email', 'sms', 'system'
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    related_entity = Column(String, nullable=True)  # e.g., job_id, candidate_id
    event_type = Column(String, nullable=True)  # e.g., 'status_change', 'interview_scheduled'

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    action = Column(String)
    entity_type = Column(String)  # e.g., 'candidate', 'job', 'requisition'
    entity_id = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
