"""
Recruitment API v1 - Uses real agent orchestration
Routes for screening, ranking, and hiring decisions
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import asyncio

from backend.core import get_orchestrator, AgentType, Task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/agents/recruitment", tags=["recruitment"])


class CandidateInfo(BaseModel):
    """Candidate information"""
    id: str
    name: str
    email: str
    experience: str
    skills: List[str] = []


class JobInfo(BaseModel):
    """Job information"""
    id: str
    title: str
    description: str
    requirements: str


class ScreenCandidateRequest(BaseModel):
    """Request to screen a candidate"""
    candidate: CandidateInfo
    job: JobInfo


class ScreenCandidateResponse(BaseModel):
    """Response from screening"""
    decision: str
    confidence: float
    reasoning: str
    next_steps: List[str]
    score: float
    metadata: Dict[str, Any] = {}


class RankCandidatesRequest(BaseModel):
    """Request to rank candidates"""
    candidates: List[CandidateInfo]
    job: JobInfo


class RankCandidatesResponse(BaseModel):
    """Response from ranking"""
    ranking: List[Dict[str, Any]]
    top_candidate_id: Optional[str]
    reasoning: str


@router.post("/screen-candidate", response_model=ScreenCandidateResponse)
async def screen_candidate(request: ScreenCandidateRequest):
    """
    Screen a single candidate using AI agent
    
    The recruitment agent will:
    1. Analyze candidate resume/experience
    2. Match against job requirements
    3. Provide screening score (0-100)
    4. Recommend proceed or reject
    """
    try:
        orchestrator = get_orchestrator()

        # Create screening task
        task = Task(
            id=str(uuid.uuid4()),
            agent_type=AgentType.RECRUITMENT,
            description="screen_candidate",
            payload={
                "name": request.candidate.name,
                "email": request.candidate.email,
                "experience": request.candidate.experience,
                "skills": request.candidate.skills,
                "job_description": request.job.description,
            },
            priority=1
        )

        # Execute with agent
        decision = await orchestrator.execute_task(task)

        # Extract score
        metadata = decision.metadata
        score = metadata.get("score", 50) if isinstance(metadata, dict) else 50

        return ScreenCandidateResponse(
            decision=decision.decision,
            confidence=decision.confidence,
            reasoning=decision.reasoning,
            next_steps=decision.next_steps,
            score=score,
            metadata=metadata
        )

    except Exception as e:
        logger.error(f"Error screening candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to screen candidate"
        )


@router.post("/rank-candidates", response_model=RankCandidatesResponse)
async def rank_candidates(request: RankCandidatesRequest):
    """
    Rank multiple candidates for a job
    
    The agent will:
    1. Compare all candidates
    2. Score each against requirements
    3. Provide ranked list
    4. Recommend top candidate
    """
    try:
        orchestrator = get_orchestrator()

        # Create ranking task
        task = Task(
            id=str(uuid.uuid4()),
            agent_type=AgentType.RECRUITMENT,
            description="rank_candidates",
            payload={
                "candidates": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "experience": c.experience,
                        "skills": c.skills,
                    }
                    for c in request.candidates
                ],
                "job": {
                    "title": request.job.title,
                    "requirements": request.job.requirements,
                }
            },
            priority=2
        )

        # Execute with agent
        decision = await orchestrator.execute_task(task)

        ranking = decision.metadata.get("ranking", {}) if isinstance(decision.metadata, dict) else {}
        ranked_list = ranking.get("ranked", []) if isinstance(ranking, dict) else []

        top_candidate_id = None
        if ranked_list and isinstance(ranked_list, list) and len(ranked_list) > 0:
            top_candidate_id = ranked_list[0].get("id") if isinstance(ranked_list[0], dict) else None

        return RankCandidatesResponse(
            ranking=ranked_list,
            top_candidate_id=top_candidate_id,
            reasoning=decision.reasoning
        )

    except Exception as e:
        logger.error(f"Error ranking candidates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rank candidates"
        )


@router.get("/agents/status")
async def get_agent_status():
    """Get recruitment agent status and capabilities"""
    try:
        orchestrator = get_orchestrator()
        
        return {
            "agent_type": "recruitment",
            "status": "ready",
            "capabilities": orchestrator.get_agent_capabilities(AgentType.RECRUITMENT),
            "completed_tasks": len(orchestrator.completed_tasks),
        }

    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get agent status"
        )
