"""
Performance Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from backend.database.sql_database import get_db
from backend.schemas.performance import (
    GoalCreate, GoalResponse, GoalUpdate, GoalListResponse,
    GoalCheckinCreate, GoalCheckinResponse,
    PerformanceReviewCreate, PerformanceReviewResponse, PerformanceReviewUpdate,
    ReviewListResponse, EmployeePerformance, GoalProgress, ReviewStatus, GoalStatus
)
from backend.models.performance_models import PerformanceGoal, GoalCheckin, PerformanceReview, ReviewMetric
from backend.models.sql_models import User
from backend.auth.deps import get_current_user

router = APIRouter(prefix="/performance", tags=["performance"])

# Goals Endpoints
@router.post("/goals/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new performance goal"""
    if goal_data.end_date <= goal_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    db_goal = PerformanceGoal(
        employee_id=current_user.id,
        **goal_data.dict()
    )
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    
    return db_goal

@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific goal by ID"""
    goal = db.query(PerformanceGoal).filter(
        PerformanceGoal.id == goal_id,
        PerformanceGoal.employee_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or access denied"
        )
        
    return goal

@router.get("/goals/", response_model=GoalListResponse)
async def list_goals(
    status: Optional[GoalStatus] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all goals for the current user with pagination"""
    query = db.query(PerformanceGoal).filter(
        PerformanceGoal.employee_id == current_user.id
    )
    
    if status:
        query = query.filter(PerformanceGoal.status == status)
    
    total = query.count()
    total_pages = (total + size - 1) // size
    
    goals = query.offset((page - 1) * size).limit(size).all()
    
    return GoalListResponse(
        items=goals,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )

@router.put("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a goal"""
    goal = db.query(PerformanceGoal).filter(
        PerformanceGoal.id == goal_id,
        PerformanceGoal.employee_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or access denied"
        )
    
    update_data = goal_data.dict(exclude_unset=True)
    
    # Update progress if current_value is provided
    if 'current_value' in update_data:
        update_data['progress'] = (update_data['current_value'] / goal.target_value) * 100
        
        # Auto-update status based on progress
        if update_data['progress'] >= 100:
            update_data['status'] = GoalStatus.COMPLETED
        elif update_data['progress'] > 0:
            update_data['status'] = GoalStatus.IN_PROGRESS
    
    for field, value in update_data.items():
        setattr(goal, field, value)
    
    db.commit()
    db.refresh(goal)
    
    return goal

@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a goal"""
    goal = db.query(PerformanceGoal).filter(
        PerformanceGoal.id == goal_id,
        PerformanceGoal.employee_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or access denied"
        )
    
    db.delete(goal)
    db.commit()
    
    return None

# Goal Checkins Endpoints
@router.post("/goals/{goal_id}/checkins", response_model=GoalCheckinResponse, status_code=status.HTTP_201_CREATED)
async def create_goal_checkin(
    goal_id: str,
    checkin_data: GoalCheckinCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a check-in for a goal"""
    goal = db.query(PerformanceGoal).filter(
        PerformanceGoal.id == goal_id,
        PerformanceGoal.employee_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or access denied"
        )
    
    # Update goal progress
    goal.current_value = checkin_data.current_value
    goal.progress = checkin_data.updated_progress
    
    # Auto-update status based on progress
    if goal.progress >= 100:
        goal.status = GoalStatus.COMPLETED
    elif goal.progress > 0:
        goal.status = GoalStatus.IN_PROGRESS
    
    # Create check-in
    db_checkin = GoalCheckin(
        goal_id=goal_id,
        **checkin_data.dict()
    )
    
    db.add(db_checkin)
    db.commit()
    db.refresh(db_checkin)
    
    return db_checkin

# Performance Reviews Endpoints
@router.post("/reviews/", response_model=PerformanceReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_performance_review(
    review_data: PerformanceReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new performance review"""
    # Check if user has permission to create reviews (e.g., manager role)
    # This is a simplified example - implement proper role-based access control
    
    db_review = PerformanceReview(
        **review_data.dict(exclude={"metrics"}),
        created_by=current_user.id
    )
    
    db.add(db_review)
    db.flush()  # Flush to get the review ID
    
    # Add metrics
    for metric_data in review_data.metrics:
        db_metric = ReviewMetric(
            review_id=db_review.id,
            **metric_data.dict()
        )
        db.add(db_metric)
    
    db.commit()
    db.refresh(db_review)
    
    return db_review

@router.get("/reviews/{review_id}", response_model=PerformanceReviewResponse)
async def get_performance_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific performance review"""
    review = db.query(PerformanceReview).filter(
        PerformanceReview.id == review_id,
        (PerformanceReview.employee_id == current_user.id) | 
        (PerformanceReview.reviewer_id == current_user.id)
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or access denied"
        )
        
    return review

@router.get("/reviews/", response_model=ReviewListResponse)
async def list_performance_reviews(
    status: Optional[ReviewStatus] = None,
    employee_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List performance reviews with filtering and pagination"""
    query = db.query(PerformanceReview)
    
    # Filter by employee or reviewer
    if employee_id:
        # Only allow managers/HR to filter by employee_id
        # Implement proper role check here
        query = query.filter(PerformanceReview.employee_id == employee_id)
    else:
        # Regular users can only see their own reviews
        query = query.filter(
            (PerformanceReview.employee_id == current_user.id) |
            (PerformanceReview.reviewer_id == current_user.id)
        )
    
    if status:
        query = query.filter(PerformanceReview.status == status)
    
    total = query.count()
    total_pages = (total + size - 1) // size
    
    reviews = query.offset((page - 1) * size).limit(size).all()
    
    return ReviewListResponse(
        items=reviews,
        total=total,
        page=page,
        size=size,
        total_pages=total_pages
    )

@router.put("/reviews/{review_id}", response_model=PerformanceReviewResponse)
async def update_performance_review(
    review_id: str,
    review_data: PerformanceReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a performance review"""
    review = db.query(PerformanceReview).filter(
        PerformanceReview.id == review_id,
        PerformanceReview.reviewer_id == current_user.id  # Only reviewer can update
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or access denied"
        )
    
    if review.is_finalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a finalized review"
        )
    
    update_data = review_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(review, field, value)
    
    db.commit()
    db.refresh(review)
    
    return review

@router.post("/reviews/{review_id}/submit", response_model=PerformanceReviewResponse)
async def submit_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a review for employee acknowledgment"""
    review = db.query(PerformanceReview).filter(
        PerformanceReview.id == review_id,
        PerformanceReview.reviewer_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or access denied"
        )
    
    if review.status == ReviewStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review is already completed"
        )
    
    review.status = ReviewStatus.IN_PROGRESS
    db.commit()
    db.refresh(review)
    
    return review

@router.post("/reviews/{review_id}/acknowledge", response_model=PerformanceReviewResponse)
async def acknowledge_review(
    review_id: str,
    comments: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Acknowledge a review by the employee"""
    review = db.query(PerformanceReview).filter(
        PerformanceReview.id == review_id,
        PerformanceReview.employee_id == current_user.id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or access denied"
        )
    
    if review.status != ReviewStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review is not in a state to be acknowledged"
        )
    
    review.status = ReviewStatus.COMPLETED
    review.employee_comments = comments
    db.commit()
    db.refresh(review)
    
    return review

# Analytics Endpoints
@router.get("/analytics/goal-progress", response_model=List[GoalProgress])
async def get_goal_progress_analytics(
    employee_id: Optional[str] = None,
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get goal progress analytics"""
    # Implement proper access control
    query = db.query(PerformanceGoal)
    
    if employee_id:
        query = query.filter(PerformanceGoal.employee_id == employee_id)
    elif department:
        # Join with users table to filter by department
        query = query.join(User).filter(User.department == department)
    else:
        # Default to current user's goals
        query = query.filter(PerformanceGoal.employee_id == current_user.id)
    
    goals = query.all()
    
    return [
        GoalProgress(
            goal_id=goal.id,
            title=goal.title,
            progress=goal.progress,
            status=goal.status,
            last_updated=goal.updated_at
        )
        for goal in goals
    ]

@router.get("/analytics/employee-performance", response_model=List[EmployeePerformance])
async def get_employee_performance_analytics(
    department: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get employee performance analytics"""
    # Implement proper access control
    query = db.query(User)
    
    if department:
        query = query.filter(User.department == department)
    
    employees = query.all()
    
    result = []
    
    for emp in employees:
        # Get latest review
        latest_review = db.query(PerformanceReview).filter(
            PerformanceReview.employee_id == emp.id,
            PerformanceReview.status == ReviewStatus.COMPLETED
        ).order_by(PerformanceReview.review_period_end.desc()).first()
        
        # Get goals
        goals = db.query(PerformanceGoal).filter(
            PerformanceGoal.employee_id == emp.id
        ).all()
        
        total_goals = len(goals)
        completed_goals = len([g for g in goals if g.status == GoalStatus.COMPLETED])
        avg_progress = sum(g.progress for g in goals) / total_goals if total_goals > 0 else 0
        
        result.append(
            EmployeePerformance(
                employee_id=emp.id,
                name=emp.name,
                overall_rating=latest_review.overall_rating if latest_review else 0,
                completed_goals=completed_goals,
                total_goals=total_goals,
                progress=avg_progress,
                last_review_date=latest_review.review_period_end if latest_review else None
            )
        )
    
    return result
