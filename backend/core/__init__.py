"""
Core backend components for HR Agent System
Includes LLM integration and agent orchestration
"""

from backend.core.llm_client import (
    LLMClient,
    LLMConfig,
    LLMProvider,
    Message,
    get_llm_client,
    reset_llm_client,
)

from backend.core.agent_orchestrator import (
    HRAgent,
    AgentType,
    Task,
    AgentDecision,
    RecruitmentAgent,
    InterviewAgent,
    OnboardingAgent,
    AgentOrchestrator,
    get_orchestrator,
)

from backend.core.agents_extended import (
    PerformanceAgent,
    ExitAgent,
    LeaveAgent,
    EngagementAgent,
    PayrollAgent,
)

__all__ = [
    # LLM
    "LLMClient",
    "LLMConfig",
    "LLMProvider",
    "Message",
    "get_llm_client",
    "reset_llm_client",
    # Base Agents
    "HRAgent",
    "AgentType",
    "Task",
    "AgentDecision",
    "RecruitmentAgent",
    "InterviewAgent",
    "OnboardingAgent",
    # Extended Agents
    "PerformanceAgent",
    "ExitAgent",
    "LeaveAgent",
    "EngagementAgent",
    "PayrollAgent",
    # Orchestrator
    "AgentOrchestrator",
    "get_orchestrator",
]
