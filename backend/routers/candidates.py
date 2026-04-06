"""Candidates CRUD router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import uuid

from backend.database.sql_database import get_db

router = APIRouter(prefix="/candidates", tags=["Candidates"])


class CandidateCreate(BaseModel):
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    source: Optional[str] = "Direct"
    skills: Optional[List[str]] = []
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class CandidateUpdate(BaseModel):
    stage: Optional[str] = None
    score: Optional[float] = None
    notes: Optional[str] = None
    skills: Optional[List[str]] = None


class CandidateOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    phone: Optional[str]
    source: str
    stage: str
    score: float
    skills: List[str]
    applied_at: str
    updated_at: str

    class Config:
        from_attributes = True


# In-memory store (until DB models are finalized)
_CANDIDATES = [
    {
        "id": "c-001", "name": "Priya Sharma", "email": "priya@example.com",
        "role": "Senior Frontend Engineer", "phone": "+1-555-0101",
        "source": "LinkedIn", "stage": "interview", "score": 87.4,
        "skills": ["React", "TypeScript", "Node.js", "GraphQL"],
        "applied_at": "2026-04-03T10:00:00Z", "updated_at": "2026-04-06T09:00:00Z",
    },
    {
        "id": "c-002", "name": "Marcus Williams", "email": "marcus@example.com",
        "role": "Product Manager", "phone": "+1-555-0102",
        "source": "Referral", "stage": "offer", "score": 91.2,
        "skills": ["Strategy", "Analytics", "SQL", "Roadmapping"],
        "applied_at": "2026-04-01T14:00:00Z", "updated_at": "2026-04-06T08:00:00Z",
    },
    {
        "id": "c-003", "name": "Aisha Patel", "email": "aisha@example.com",
        "role": "DevOps Engineer", "phone": "+1-555-0103",
        "source": "Indeed", "stage": "screening", "score": 76.5,
        "skills": ["Kubernetes", "AWS", "Terraform", "Docker"],
        "applied_at": "2026-04-05T09:00:00Z", "updated_at": "2026-04-06T07:00:00Z",
    },
]


@router.get("/", response_model=List[dict])
async def list_candidates(
    stage: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """List all candidates with optional filters"""
    candidates = _CANDIDATES.copy()

    if stage:
        candidates = [c for c in candidates if c["stage"] == stage]

    if search:
        q = search.lower()
        candidates = [
            c for c in candidates
            if q in c["name"].lower() or q in c["role"].lower() or q in c["email"].lower()
        ]

    return candidates[offset : offset + limit]


@router.get("/{candidate_id}")
async def get_candidate(candidate_id: str):
    """Get a single candidate by ID"""
    for c in _CANDIDATES:
        if c["id"] == candidate_id:
            return c
    raise HTTPException(status_code=404, detail="Candidate not found")


@router.post("/", status_code=201)
async def create_candidate(data: CandidateCreate):
    """Create a new candidate"""
    new_id = f"c-{uuid.uuid4().hex[:6]}"
    now = datetime.utcnow().isoformat() + "Z"
    candidate = {
        "id": new_id,
        "name": data.name,
        "email": data.email,
        "role": data.role,
        "phone": data.phone,
        "source": data.source or "Direct",
        "stage": "sourced",
        "score": 0.0,
        "skills": data.skills or [],
        "linkedin_url": data.linkedin_url,
        "portfolio_url": data.portfolio_url,
        "applied_at": now,
        "updated_at": now,
    }
    _CANDIDATES.append(candidate)
    return candidate


@router.patch("/{candidate_id}")
async def update_candidate(candidate_id: str, data: CandidateUpdate):
    """Update candidate stage, score, or notes"""
    for i, c in enumerate(_CANDIDATES):
        if c["id"] == candidate_id:
            if data.stage is not None:
                _CANDIDATES[i]["stage"] = data.stage
            if data.score is not None:
                _CANDIDATES[i]["score"] = data.score
            if data.skills is not None:
                _CANDIDATES[i]["skills"] = data.skills
            _CANDIDATES[i]["updated_at"] = datetime.utcnow().isoformat() + "Z"
            return _CANDIDATES[i]
    raise HTTPException(status_code=404, detail="Candidate not found")


@router.delete("/{candidate_id}", status_code=204)
async def delete_candidate(candidate_id: str):
    """Remove a candidate"""
    global _CANDIDATES
    before = len(_CANDIDATES)
    _CANDIDATES = [c for c in _CANDIDATES if c["id"] != candidate_id]
    if len(_CANDIDATES) == before:
        raise HTTPException(status_code=404, detail="Candidate not found")
