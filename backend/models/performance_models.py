"""
Performance Management Models
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.database.sql_database import Base
import uuid

class PerformanceGoal(Base):
    __tablename__ = "performance_goals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    target_value = Column(Float, default=0.0)
    current_value = Column(Float, default=0.0)
    progress = Column(Float, default=0.0)
    status = Column(String(20), default="Not Started")  # Not Started, In Progress, Completed, At Risk
    weight = Column(Float, default=1.0)
    kpis = Column(JSON)  # Store KPIs as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("User", back_populates="performance_goals")
    checkins = relationship("GoalCheckin", back_populates="goal")
    
    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "title": self.title,
            "description": self.description,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "progress": self.progress,
            "status": self.status,
            "weight": self.weight,
            "kpis": self.kpis,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class GoalCheckin(Base):
    __tablename__ = "goal_checkins"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = Column(String, ForeignKey("performance_goals.id"), nullable=False)
    checkin_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    current_value = Column(Float)
    updated_progress = Column(Float)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(String, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Relationships
    goal = relationship("PerformanceGoal", back_populates="checkins")
    approver = relationship("User", foreign_keys=[approved_by])
    
    def to_dict(self):
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "checkin_date": self.checkin_date.isoformat() if self.checkin_date else None,
            "notes": self.notes,
            "current_value": self.current_value,
            "updated_progress": self.updated_progress,
            "is_approved": self.is_approved,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None
        }

class PerformanceReview(Base):
    __tablename__ = "performance_reviews"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String, ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(String, ForeignKey("users.id"), nullable=False)
    review_period_start = Column(DateTime, nullable=False)
    review_period_end = Column(DateTime, nullable=False)
    status = Column(String(20), default="draft")  # draft, in_progress, completed, approved
    overall_rating = Column(Float)
    strengths = Column(Text)
    areas_for_improvement = Column(Text)
    employee_comments = Column(Text)
    reviewer_comments = Column(Text)
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = relationship("User", foreign_keys=[employee_id])
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    review_metrics = relationship("ReviewMetric", back_populates="review")
    
    def to_dict(self):
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "reviewer_id": self.reviewer_id,
            "review_period_start": self.review_period_start.isoformat() if self.review_period_start else None,
            "review_period_end": self.review_period_end.isoformat() if self.review_period_end else None,
            "status": self.status,
            "overall_rating": self.overall_rating,
            "strengths": self.strengths,
            "areas_for_improvement": self.areas_for_improvement,
            "employee_comments": self.employee_comments,
            "reviewer_comments": self.reviewer_comments,
            "is_finalized": self.is_finalized,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "review_metrics": [metric.to_dict() for metric in self.review_metrics] if self.review_metrics else []
        }

class ReviewMetric(Base):
    __tablename__ = "review_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String, ForeignKey("performance_reviews.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    rating = Column(Float, nullable=False)
    comments = Column(Text)
    
    # Relationships
    review = relationship("PerformanceReview", back_populates="review_metrics")
    
    def to_dict(self):
        return {
            "id": self.id,
            "review_id": self.review_id,
            "metric_name": self.metric_name,
            "rating": self.rating,
            "comments": self.comments
        }
