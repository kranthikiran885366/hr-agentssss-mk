"""
Performance Management Pydantic Models
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum

class GoalStatus(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    AT_RISK = "At Risk"
    ON_HOLD = "On Hold"

class ReviewStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"

# Base schemas
class GoalBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    target_value: float = 0.0
    weight: float = 1.0
    kpis: Optional[Dict[str, Any]] = None

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    progress: Optional[float] = None
    status: Optional[GoalStatus] = None
    weight: Optional[float] = None
    kpis: Optional[Dict[str, Any]] = None

class GoalResponse(GoalBase):
    id: str
    employee_id: str
    current_value: float = 0.0
    progress: float = 0.0
    status: GoalStatus = GoalStatus.NOT_STARTED
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GoalCheckinBase(BaseModel):
    notes: Optional[str] = None
    current_value: float
    updated_progress: float = Field(..., ge=0, le=100)

class GoalCheckinCreate(GoalCheckinBase):
    pass

class GoalCheckinResponse(GoalCheckinBase):
    id: str
    goal_id: str
    checkin_date: datetime
    is_approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ReviewMetricBase(BaseModel):
    metric_name: str = Field(..., max_length=100)
    rating: float = Field(..., ge=0, le=5)
    comments: Optional[str] = None

class ReviewMetricCreate(ReviewMetricBase):
    pass

class ReviewMetricResponse(ReviewMetricBase):
    id: str
    review_id: str

    class Config:
        orm_mode = True

class PerformanceReviewBase(BaseModel):
    employee_id: str
    reviewer_id: str
    review_period_start: datetime
    review_period_end: datetime
    status: ReviewStatus = ReviewStatus.DRAFT
    overall_rating: Optional[float] = Field(None, ge=0, le=5)
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    employee_comments: Optional[str] = None
    reviewer_comments: Optional[str] = None

class PerformanceReviewCreate(PerformanceReviewBase):
    metrics: List[ReviewMetricCreate] = []

class PerformanceReviewUpdate(BaseModel):
    status: Optional[ReviewStatus] = None
    overall_rating: Optional[float] = Field(None, ge=0, le=5)
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    employee_comments: Optional[str] = None
    reviewer_comments: Optional[str] = None
    is_finalized: Optional[bool] = None

class PerformanceReviewResponse(PerformanceReviewBase):
    id: str
    is_finalized: bool = False
    created_at: datetime
    updated_at: datetime
    metrics: List[ReviewMetricResponse] = []

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Response models for lists
class GoalListResponse(BaseModel):
    items: List[GoalResponse]
    total: int
    page: int
    size: int
    total_pages: int

class ReviewListResponse(BaseModel):
    items: List[PerformanceReviewResponse]
    total: int
    page: int
    size: int
    total_pages: int

# Analytics models
class GoalProgress(BaseModel):
    goal_id: str
    title: str
    progress: float
    status: str
    last_updated: datetime

class EmployeePerformance(BaseModel):
    employee_id: str
    name: str
    overall_rating: float
    completed_goals: int
    total_goals: int
    progress: float
    last_review_date: Optional[datetime] = None
