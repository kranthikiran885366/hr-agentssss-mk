"""Jobs / Requisitions router"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/jobs", tags=["Jobs"])


class JobCreate(BaseModel):
    title: str
    department: str
    location: str
    type: Optional[str] = "full-time"
    level: Optional[str] = "mid"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = []
    skills_required: Optional[List[str]] = []


class JobUpdate(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


_JOBS = [
    {
        "id": "j-001", "title": "Senior Frontend Engineer", "department": "Engineering",
        "location": "Remote", "type": "full-time", "level": "senior",
        "salary_min": 150000, "salary_max": 200000, "status": "active",
        "candidates": 14, "posted_at": "2026-03-15T00:00:00Z",
        "requirements": ["5+ years React", "TypeScript", "System design"],
        "skills_required": ["React", "TypeScript", "Node.js", "GraphQL"],
        "description": "Build world-class UI experiences at scale.",
    },
    {
        "id": "j-002", "title": "Product Manager", "department": "Product",
        "location": "Hybrid - NYC", "type": "full-time", "level": "senior",
        "salary_min": 130000, "salary_max": 180000, "status": "active",
        "candidates": 8, "posted_at": "2026-03-20T00:00:00Z",
        "requirements": ["4+ years PM experience", "SQL", "Data-driven"],
        "skills_required": ["Strategy", "Analytics", "SQL", "Figma"],
        "description": "Define and execute our product vision.",
    },
    {
        "id": "j-003", "title": "DevOps Engineer", "department": "Infrastructure",
        "location": "Remote", "type": "full-time", "level": "mid",
        "salary_min": 120000, "salary_max": 160000, "status": "active",
        "candidates": 5, "posted_at": "2026-04-01T00:00:00Z",
        "requirements": ["Kubernetes", "AWS certified", "CI/CD pipelines"],
        "skills_required": ["Kubernetes", "AWS", "Terraform", "Docker", "ArgoCD"],
        "description": "Own our cloud infrastructure and reliability.",
    },
    {
        "id": "j-004", "title": "Data Scientist", "department": "Data",
        "location": "Remote", "type": "full-time", "level": "senior",
        "salary_min": 140000, "salary_max": 190000, "status": "filled",
        "candidates": 21, "posted_at": "2026-02-10T00:00:00Z",
        "requirements": ["PhD or 5+ yrs", "ML pipelines", "Python"],
        "skills_required": ["Python", "PyTorch", "Spark", "SQL", "Statistics"],
        "description": "Drive data-driven decision making.",
    },
]


@router.get("/")
async def list_jobs(
    status: Optional[str] = None,
    department: Optional[str] = None,
    limit: int = Query(50, le=200),
):
    """List all open jobs"""
    jobs = _JOBS.copy()
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    if department:
        jobs = [j for j in jobs if j["department"].lower() == department.lower()]
    return jobs[:limit]


@router.get("/{job_id}")
async def get_job(job_id: str):
    """Get a single job posting"""
    for j in _JOBS:
        if j["id"] == job_id:
            return j
    raise HTTPException(status_code=404, detail="Job not found")


@router.post("/", status_code=201)
async def create_job(data: JobCreate):
    """Create a new job posting"""
    new_job = {
        "id": f"j-{uuid.uuid4().hex[:6]}",
        "title": data.title,
        "department": data.department,
        "location": data.location,
        "type": data.type,
        "level": data.level,
        "salary_min": data.salary_min,
        "salary_max": data.salary_max,
        "status": "active",
        "candidates": 0,
        "posted_at": datetime.utcnow().isoformat() + "Z",
        "requirements": data.requirements or [],
        "skills_required": data.skills_required or [],
        "description": data.description or "",
    }
    _JOBS.append(new_job)
    return new_job


@router.patch("/{job_id}")
async def update_job(job_id: str, data: JobUpdate):
    """Update job status or details"""
    for i, j in enumerate(_JOBS):
        if j["id"] == job_id:
            if data.status:
                _JOBS[i]["status"] = data.status
            if data.title:
                _JOBS[i]["title"] = data.title
            if data.description:
                _JOBS[i]["description"] = data.description
            return _JOBS[i]
    raise HTTPException(status_code=404, detail="Job not found")


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: str):
    """Remove a job posting"""
    global _JOBS
    before = len(_JOBS)
    _JOBS = [j for j in _JOBS if j["id"] != job_id]
    if len(_JOBS) == before:
        raise HTTPException(status_code=404, detail="Job not found")
