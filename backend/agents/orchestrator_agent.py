"""
Orchestrator Agent - shim that re-exports the real orchestrator
"""
from backend.agents.complete_orchestrator import CompleteHROrchestrator as OrchestratorAgent

__all__ = ["OrchestratorAgent"]
