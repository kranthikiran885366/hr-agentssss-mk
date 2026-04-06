"""
Agent Orchestrator - Coordinates multi-agent workflows
Manages agent communication, task routing, and decision-making
"""

import logging
import json
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime
import asyncio
from dataclasses import dataclass, asdict

from backend.core.llm_client import LLMClient, LLMConfig, get_llm_client

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """HR Agent types"""
    RECRUITMENT = "recruitment"
    INTERVIEW = "interview"
    SCREENING = "screening"
    VERIFICATION = "verification"
    ONBOARDING = "onboarding"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    EXIT = "exit"
    LEAVE = "leave"
    PAYROLL = "payroll"


@dataclass
class Task:
    """Task to be executed by an agent"""
    id: str
    agent_type: AgentType
    description: str
    payload: Dict[str, Any]
    priority: int = 0
    created_at: str = None
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()


@dataclass
class AgentDecision:
    """Decision made by an agent"""
    agent_type: AgentType
    decision: str
    confidence: float
    reasoning: str
    next_steps: List[str]
    metadata: Dict[str, Any]


class HRAgent:
    """Base agent class with LLM integration"""

    def __init__(
        self,
        agent_type: AgentType,
        system_prompt: str,
        llm_client: Optional[LLMClient] = None,
    ):
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.llm_client = llm_client or get_llm_client()
        self.capabilities: List[str] = []
        self.processed_tasks: List[Task] = []

    async def process_task(self, task: Task) -> AgentDecision:
        """Process a task and return decision"""
        raise NotImplementedError("Subclasses must implement process_task")

    async def think(self, prompt: str) -> str:
        """Use LLM to think through a problem"""
        return await self.llm_client.complete(
            prompt=prompt,
            system_context=self.system_prompt
        )

    def _log_task(self, task: Task):
        """Log task processing"""
        logger.info(f"[{self.agent_type.value}] Processing task: {task.id}")


class RecruitmentAgent(HRAgent):
    """Agent for recruitment and candidate sourcing"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        system_prompt = """You are a Senior Recruitment Agent. Your responsibilities:
        - Analyze job descriptions and identify key requirements
        - Screen resumes and match candidates to jobs
        - Rank candidates by fit
        - Provide hiring recommendations
        - Be fair and unbiased
        
        Always provide structured decisions with clear reasoning."""

        super().__init__(
            agent_type=AgentType.RECRUITMENT,
            system_prompt=system_prompt,
            llm_client=llm_client
        )
        self.capabilities = ["resume_matching", "candidate_ranking", "jd_analysis"]

    async def process_task(self, task: Task) -> AgentDecision:
        """Process recruitment task"""
        self._log_task(task)
        
        if task.description == "screen_candidate":
            return await self._screen_candidate(task)
        elif task.description == "rank_candidates":
            return await self._rank_candidates(task)
        else:
            raise ValueError(f"Unknown task: {task.description}")

    async def _screen_candidate(self, task: Task) -> AgentDecision:
        """Screen a single candidate"""
        candidate = task.payload
        job_desc = task.payload.get("job_description", "")
        
        prompt = f"""
        Analyze this candidate for the role. Provide a structured decision.
        
        Candidate:
        - Name: {candidate.get('name')}
        - Experience: {candidate.get('experience')}
        - Skills: {candidate.get('skills')}
        - Education: {candidate.get('education')}
        
        Job Requirements:
        {job_desc}
        
        Provide JSON response with: score (0-100), fit_assessment, next_step, concerns
        """
        
        decision_text = await self.think(prompt)
        
        try:
            decision_json = json.loads(decision_text)
        except:
            decision_json = {"score": 0, "fit_assessment": decision_text}

        return AgentDecision(
            agent_type=self.agent_type,
            decision="proceed_to_interview" if decision_json.get("score", 0) >= 60 else "reject",
            confidence=decision_json.get("score", 0) / 100,
            reasoning=decision_json.get("fit_assessment", ""),
            next_steps=["schedule_interview"] if decision_json.get("score", 0) >= 60 else ["send_rejection"],
            metadata=decision_json
        )

    async def _rank_candidates(self, task: Task) -> AgentDecision:
        """Rank multiple candidates"""
        candidates = task.payload.get("candidates", [])
        
        if not candidates:
            return AgentDecision(
                agent_type=self.agent_type,
                decision="no_candidates",
                confidence=1.0,
                reasoning="No candidates to rank",
                next_steps=[],
                metadata={}
            )

        prompt = f"""
        Rank these {len(candidates)} candidates by fit for the role.
        
        Candidates:
        {json.dumps(candidates, indent=2)}
        
        Provide JSON response with ranked list: [{{name, score, reason}}]
        """
        
        ranking_text = await self.think(prompt)
        
        try:
            ranking_json = json.loads(ranking_text)
        except:
            ranking_json = {"ranked": candidates[:3]}

        return AgentDecision(
            agent_type=self.agent_type,
            decision="ranking_complete",
            confidence=0.8,
            reasoning="Candidates ranked by fit assessment",
            next_steps=["interview_top_candidate"],
            metadata={"ranking": ranking_json}
        )


class InterviewAgent(HRAgent):
    """Agent for conducting and evaluating interviews"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        system_prompt = """You are a Professional Interview Conductor. Your responsibilities:
        - Ask thoughtful, relevant interview questions
        - Evaluate responses objectively
        - Score candidates on communication, technical skills, and cultural fit
        - Provide detailed feedback
        - Make fair hiring recommendations
        
        Be conversational but professional. Adapt questions based on responses."""

        super().__init__(
            agent_type=AgentType.INTERVIEW,
            system_prompt=system_prompt,
            llm_client=llm_client
        )
        self.capabilities = ["question_generation", "response_evaluation", "scoring"]

    async def process_task(self, task: Task) -> AgentDecision:
        """Process interview task"""
        self._log_task(task)
        
        if task.description == "evaluate_response":
            return await self._evaluate_response(task)
        elif task.description == "generate_question":
            return await self._generate_question(task)
        else:
            raise ValueError(f"Unknown task: {task.description}")

    async def _evaluate_response(self, task: Task) -> AgentDecision:
        """Evaluate an interview response"""
        question = task.payload.get("question", "")
        response = task.payload.get("response", "")
        job_type = task.payload.get("job_type", "general")
        
        prompt = f"""
        Evaluate this interview response.
        
        Question: {question}
        Candidate Response: {response}
        Role Type: {job_type}
        
        Provide JSON with: score (0-100), communication_score, relevance_score, depth_score, feedback
        """
        
        evaluation_text = await self.think(prompt)
        
        try:
            evaluation = json.loads(evaluation_text)
        except:
            evaluation = {"score": 50, "feedback": evaluation_text}

        return AgentDecision(
            agent_type=self.agent_type,
            decision="response_evaluated",
            confidence=min(evaluation.get("score", 50) / 100, 0.95),
            reasoning=evaluation.get("feedback", ""),
            next_steps=["next_question" if evaluation.get("score", 50) > 40 else "conclude_interview"],
            metadata=evaluation
        )

    async def _generate_question(self, task: Task) -> AgentDecision:
        """Generate the next interview question"""
        role = task.payload.get("role", "")
        interview_stage = task.payload.get("stage", "screening")
        previous_answers = task.payload.get("previous_answers", [])
        
        prompt = f"""
        Generate the next interview question for a {role} role at {interview_stage} stage.
        
        Previous answers: {json.dumps(previous_answers[-2:]) if previous_answers else "None"}
        
        Generate JSON with: question, why_this_question, expected_areas
        """
        
        question_text = await self.think(prompt)
        
        try:
            question_data = json.loads(question_text)
        except:
            question_data = {"question": question_text}

        return AgentDecision(
            agent_type=self.agent_type,
            decision="question_generated",
            confidence=0.85,
            reasoning="Question tailored to role and interview stage",
            next_steps=["wait_for_response"],
            metadata=question_data
        )


class OnboardingAgent(HRAgent):
    """Agent for employee onboarding automation"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        system_prompt = """You are an Onboarding Specialist Agent. Your responsibilities:
        - Plan comprehensive onboarding workflows
        - Assign mentors and trainers
        - Track onboarding progress
        - Ensure all compliance requirements are met
        - Create personalized onboarding schedules
        
        Be thorough and ensure nothing is missed."""

        super().__init__(
            agent_type=AgentType.ONBOARDING,
            system_prompt=system_prompt,
            llm_client=llm_client
        )
        self.capabilities = ["workflow_planning", "mentor_assignment", "progress_tracking"]

    async def process_task(self, task: Task) -> AgentDecision:
        """Process onboarding task"""
        self._log_task(task)
        
        if task.description == "plan_onboarding":
            return await self._plan_onboarding(task)
        else:
            raise ValueError(f"Unknown task: {task.description}")

    async def _plan_onboarding(self, task: Task) -> AgentDecision:
        """Plan onboarding workflow for new employee"""
        employee = task.payload.get("employee", {})
        role = employee.get("role", "")
        department = employee.get("department", "")
        
        prompt = f"""
        Create a comprehensive onboarding plan for a new {role} in {department}.
        
        Provide JSON with: 
        - weeks: [{{week: number, activities: []}}, ...]
        - documents_needed: []
        - systems_access: []
        - mentoring_plan: {}
        """
        
        plan_text = await self.think(prompt)
        
        try:
            plan = json.loads(plan_text)
        except:
            plan = {"status": "plan_created"}

        return AgentDecision(
            agent_type=self.agent_type,
            decision="onboarding_planned",
            confidence=0.9,
            reasoning="Comprehensive onboarding plan created",
            next_steps=["assign_mentor", "create_accounts", "send_welcome_email"],
            metadata=plan
        )


class AgentOrchestrator:
    """Coordinates multiple agents and workflows"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or get_llm_client()
        self.agents: Dict[AgentType, HRAgent] = {
            AgentType.RECRUITMENT: RecruitmentAgent(self.llm_client),
            AgentType.INTERVIEW: InterviewAgent(self.llm_client),
            AgentType.ONBOARDING: OnboardingAgent(self.llm_client),
        }
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        logger.info("Agent Orchestrator initialized")

    def register_agent(self, agent_type: AgentType, agent: HRAgent):
        """Register an agent"""
        self.agents[agent_type] = agent
        logger.info(f"Agent registered: {agent_type.value}")

    async def execute_task(self, task: Task) -> AgentDecision:
        """Execute a task with appropriate agent"""
        if task.agent_type not in self.agents:
            raise ValueError(f"No agent registered for {task.agent_type.value}")

        agent = self.agents[task.agent_type]
        task.status = "in_progress"
        
        try:
            decision = await agent.process_task(task)
            task.status = "completed"
            task.result = asdict(decision)
            self.completed_tasks.append(task)
            return decision
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            logger.error(f"Task execution failed: {e}")
            raise

    async def execute_workflow(self, tasks: List[Task]) -> List[AgentDecision]:
        """Execute a series of tasks in workflow"""
        decisions = []
        for task in tasks:
            decision = await self.execute_task(task)
            decisions.append(decision)
        return decisions

    def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get status of a task"""
        for task in self.completed_tasks:
            if task.id == task_id:
                return task
        return None

    def get_agent_capabilities(self, agent_type: AgentType) -> List[str]:
        """Get capabilities of an agent"""
        if agent_type in self.agents:
            return self.agents[agent_type].capabilities
        return []


# Global orchestrator instance
_orchestrator: Optional[AgentOrchestrator] = None


def get_orchestrator(llm_client: Optional[LLMClient] = None) -> AgentOrchestrator:
    """Get or create global orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator(llm_client)
    return _orchestrator
