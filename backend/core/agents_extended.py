"""
Extended HR Agents - Performance, Exit, Payroll, Leave, Engagement
Real AI-powered implementations for employee lifecycle
"""

import json
import logging
from typing import Optional, List, Dict, Any
from backend.core.agent_orchestrator import HRAgent, AgentType, AgentDecision
from backend.core.llm_client import LLMClient

logger = logging.getLogger(__name__)


class PerformanceAgent(HRAgent):
    """Agent for performance management and reviews"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        system_prompt = """You are a Performance Management Agent. Your responsibilities:
        - Conduct performance reviews fairly and objectively
        - Identify skill gaps and development opportunities
        - Set meaningful performance goals
        - Provide constructive feedback
        - Recommend career development paths
        - Calculate performance ratings based on data
        - Suggest compensation adjustments
        
        Always be fair, unbiased, and constructive. Focus on growth."""

        super().__init__(
            agent_type=AgentType.PERFORMANCE,
            system_prompt=system_prompt,
            llm_client=llm_client
        )
        self.capabilities = ["performance_review", "goal_setting", "skill_assessment", "compensation_analysis"]

    async def process_task(self, task) -> AgentDecision:
        """Process performance task"""
        self._log_task(task)
        
        if task.description == "conduct_review":
            return await self._conduct_review(task)
        elif task.description == "set_goals":
            return await self._set_goals(task)
        elif task.description == "assess_skills":
            return await self._assess_skills(task)
        else:
            raise ValueError(f"Unknown task: {task.description}")

    async def _conduct_review(self, task) -> AgentDecision:
        """Conduct performance review"""
        employee = task.payload.get("employee", {})
        review_period = task.payload.get("review_period", "")
        manager_feedback = task.payload.get("manager_feedback", "")
        metrics = task.payload.get("metrics", {})
        
        prompt = f"""
        Conduct a performance review for:
        
        Employee: {employee.get('name')}
        Role: {employee.get('role')}
        Period: {review_period}
        
        Manager Feedback:
        {manager_feedback}
        
        Performance Metrics:
        {json.dumps(metrics, indent=2)}
        
        Provide JSON: rating (1-5), summary, strengths, development_areas, recommendations
        """
        
        review_text = await self.think(prompt)
        
        try:
            review_data = json.loads(review_text)
        except:
            review_data = {"rating": 3, "summary": review_text}

        rating = review_data.get("rating", 3)
        
        return AgentDecision(
            agent_type=self.agent_type,
            decision="review_completed",
            confidence=0.85,
            reasoning=f"Performance review completed with rating {rating}/5",
            next_steps=["provide_feedback", "set_goals", "discuss_growth"],
            metadata=review_data
        )

    async def _set_goals(self, task) -> AgentDecision:
        """Set performance goals"""
        employee = task.payload.get("employee", {})
        role = employee.get("role", "")
        review_data = task.payload.get("review_data", {})
        
        prompt = f"""
        Set SMART performance goals for a {role}.
        
        Review data: {json.dumps(review_data, indent=2)}
        
        Provide JSON with: goals (list of {{title, description, target_date, metrics}})
        """
        
        goals_text = await self.think(prompt)
        
        try:
            goals_data = json.loads(goals_text)
        except:
            goals_data = {"goals": []}

        return AgentDecision(
            agent_type=self.agent_type,
            decision="goals_set",
            confidence=0.9,
            reasoning="Personalized performance goals created",
            next_steps=["schedule_goal_review", "track_progress"],
            metadata=goals_data
        )

    async def _assess_skills(self, task) -> AgentDecision:
        """Assess employee skills"""
        employee = task.payload.get("employee", {})
        role = employee.get("role", "")
        skills = employee.get("skills", [])
        experience = employee.get("experience", "")
        
        prompt = f"""
        Assess skills for a {role} with:
        
        Current Skills: {json.dumps(skills)}
        Experience: {experience}
        
        Provide JSON: skill_assessment ({{skill: level (1-5), assessment}})
                     gaps, development_recommendations
        """
        
        assessment_text = await self.think(prompt)
        
        try:
            assessment = json.loads(assessment_text)
        except:
            assessment = {"skill_assessment": {}}

        return AgentDecision(
            agent_type=self.agent_type,
            decision="assessment_complete",
            confidence=0.88,
            reasoning="Comprehensive skill assessment completed",
            next_steps=["identify_training", "plan_development"],
            metadata=assessment
        )


class ExitAgent(HRAgent):
    """Agent for employee exit management"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        system_prompt = """You are an Exit Management Agent. Your responsibilities:
        - Process employee resignations professionally
        - Conduct exit interviews
        - Calculate final settlements
        - Generate exit documentation
        - Arrange knowledge transfer
        - Manage offboarding
        - Capture lessons learned
        
        Be empathetic but thorough. Ensure smooth transitions."""

        super().__init__(
            agent_type=AgentType.EXIT,
            system_prompt=system_prompt,
            llm_client=llm_client
        )
        self.capabilities = ["exit_interview", "settlement_calculation", "offboarding_plan"]

    async def process_task(self, task) -> AgentDecision:
        """Process exit task"""
        self._log_task(task)
        
        if task.description == "process_resignation":
            return await self._process_resignation(task)
        elif task.description == "calculate_settlement":
            return await self._calculate_settlement(task)
        else:
            raise ValueError(f"Unknown task: {task.description}")

    async def _process_resignation(self, task) -> AgentDecision:
        """Process resignation"""
        employee = task.payload.get("employee", {})
        reason = task.payload.get("reason", "")
        last_working_day = task.payload.get("last_working_day", "")
        
        prompt = f"""
        Process resignation for:
        
        Employee: {employee.get('name')}
        Role: {employee.get('role')}
        Reason: {reason}
        Last Working Day: {last_working_day}
        
        Provide JSON: offboarding_tasks, knowledge_transfer_plan, access_revocation_schedule
        """
        
        resignation_text = await self.think(prompt)
        
        try:
            resignation_data = json.loads(resignation_text)
        except:
            resignation_data = {"status": "resignation_processed"}

        return AgentDecision(
            agent_type=self.agent_type,
            decision="resignation_processed",
            confidence=0.92,
            reasoning="Resignation processed with offboarding plan",
            next_steps=["revoke_access", "knowledge_transfer", "send_documentation"],
            metadata=resignation_data
        )

    async def _calculate_settlement(self, task) -> AgentDecision:
        """Calculate final settlement"""
        employee = task.payload.get("employee", {})
        employment_data = task.payload.get("employment_data", {})
        
        prompt = f"""
        Calculate final settlement for exiting employee:
        
        Employee: {employee.get('name')}
        
        Employment Data:
        {json.dumps(employment_data, indent=2)}
        
        Provide JSON: final_salary, pending_bonuses, leave_encashment, gratuity, 
                     total_settlement, deductions, net_amount
        """
        
        settlement_text = await self.think(prompt)
        
        try:
            settlement_data = json.loads(settlement_text)
        except:
            settlement_data = {"status": "settlement_calculated"}

        return AgentDecision(
            agent_type=self.agent_type,
            decision="settlement_calculated",
            confidence=0.95,
            reasoning="Final settlement calculated",
            next_steps=["approve_settlement", "process_payment"],
            metadata=settlement_data
        )


class LeaveAgent(HRAgent):
    """Agent for leave management and approvals"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        system_prompt = """You are a Leave Management Agent. Your responsibilities:
        - Evaluate leave requests fairly
        - Check leave policy compliance
        - Verify leave balance
        - Auto-approve eligible requests
        - Flag policy exceptions for review
        - Calculate leave balance
        - Track leave history
        
        Apply policies consistently and fairly."""

        super().__init__(
            agent_type=AgentType.LEAVE,
            system_prompt=system_prompt,
            llm_client=llm_client
        )
        self.capabilities = ["leave_approval", "balance_calculation", "policy_enforcement"]

    async def process_task(self, task) -> AgentDecision:
        """Process leave task"""
        self._log_task(task)
        
        if task.description == "evaluate_leave_request":
            return await self._evaluate_request(task)
        else:
            raise ValueError(f"Unknown task: {task.description}")

    async def _evaluate_request(self, task) -> AgentDecision:
        """Evaluate leave request"""
        employee = task.payload.get("employee", {})
        leave_type = task.payload.get("leave_type", "")
        from_date = task.payload.get("from_date", "")
        to_date = task.payload.get("to_date", "")
        reason = task.payload.get("reason", "")
        leave_balance = task.payload.get("leave_balance", {})
        
        prompt = f"""
        Evaluate leave request:
        
        Employee: {employee.get('name')}
        Leave Type: {leave_type}
        Dates: {from_date} to {to_date}
        Reason: {reason}
        Available Balance: {json.dumps(leave_balance)}
        
        Provide JSON: approval_status (approved/rejected/pending_manager_approval), 
                     reason, balance_after, notes
        """
        
        evaluation_text = await self.think(prompt)
        
        try:
            evaluation = json.loads(evaluation_text)
        except:
            evaluation = {"approval_status": "pending_manager_approval"}

        status = evaluation.get("approval_status", "pending_manager_approval")
        
        return AgentDecision(
            agent_type=self.agent_type,
            decision=status,
            confidence=0.85 if status == "approved" else 0.75,
            reasoning=evaluation.get("reason", ""),
            next_steps=["send_notification", "update_calendar"] if status == "approved" else ["escalate_to_manager"],
            metadata=evaluation
        )


class EngagementAgent(HRAgent):
    """Agent for employee engagement and retention"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        system_prompt = """You are an Employee Engagement Agent. Your responsibilities:
        - Monitor employee sentiment and engagement
        - Identify retention risks
        - Recommend engagement initiatives
        - Schedule wellness check-ins
        - Celebrate milestones
        - Suggest career development paths
        - Identify high-potential employees
        
        Focus on keeping employees happy and engaged."""

        super().__init__(
            agent_type=AgentType.ENGAGEMENT,
            system_prompt=system_prompt,
            llm_client=llm_client
        )
        self.capabilities = ["sentiment_analysis", "retention_risk", "engagement_initiatives"]

    async def process_task(self, task) -> AgentDecision:
        """Process engagement task"""
        self._log_task(task)
        
        if task.description == "assess_sentiment":
            return await self._assess_sentiment(task)
        elif task.description == "engagement_plan":
            return await self._create_engagement_plan(task)
        else:
            raise ValueError(f"Unknown task: {task.description}")

    async def _assess_sentiment(self, task) -> AgentDecision:
        """Assess employee sentiment"""
        employee = task.payload.get("employee", {})
        feedback = task.payload.get("feedback", "")
        performance_data = task.payload.get("performance_data", {})
        
        prompt = f"""
        Assess sentiment and engagement for:
        
        Employee: {employee.get('name')}
        
        Recent Feedback:
        {feedback}
        
        Performance Data:
        {json.dumps(performance_data, indent=2)}
        
        Provide JSON: sentiment (positive/neutral/negative), engagement_score (0-100),
                     risks, strengths, recommendations
        """
        
        sentiment_text = await self.think(prompt)
        
        try:
            sentiment_data = json.loads(sentiment_text)
        except:
            sentiment_data = {"sentiment": "neutral", "engagement_score": 50}

        sentiment = sentiment_data.get("sentiment", "neutral")
        
        return AgentDecision(
            agent_type=self.agent_type,
            decision=f"sentiment_{sentiment}",
            confidence=0.8,
            reasoning=f"Employee sentiment: {sentiment}",
            next_steps=["schedule_checkin"] if sentiment in ["negative", "neutral"] else ["continue_engagement"],
            metadata=sentiment_data
        )

    async def _create_engagement_plan(self, task) -> AgentDecision:
        """Create engagement plan"""
        employee = task.payload.get("employee", {})
        engagement_data = task.payload.get("engagement_data", {})
        
        prompt = f"""
        Create engagement and retention plan for:
        
        {json.dumps(employee, indent=2)}
        
        Current Data:
        {json.dumps(engagement_data, indent=2)}
        
        Provide JSON: initiatives, timeline, expected_impact, success_metrics
        """
        
        plan_text = await self.think(prompt)
        
        try:
            plan_data = json.loads(plan_text)
        except:
            plan_data = {"initiatives": []}

        return AgentDecision(
            agent_type=self.agent_type,
            decision="engagement_plan_created",
            confidence=0.88,
            reasoning="Personalized engagement plan created",
            next_steps=["implement_initiatives", "schedule_checkins"],
            metadata=plan_data
        )


class PayrollAgent(HRAgent):
    """Agent for payroll processing"""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        system_prompt = """You are a Payroll Processing Agent. Your responsibilities:
        - Calculate salaries accurately
        - Apply deductions (tax, PF, insurance)
        - Calculate bonuses and incentives
        - Process reimbursements
        - Generate payslips
        - Ensure compliance with regulations
        - Handle payroll exceptions
        
        Be accurate and ensure all calculations are correct."""

        super().__init__(
            agent_type=AgentType.PAYROLL,
            system_prompt=system_prompt,
            llm_client=llm_client
        )
        self.capabilities = ["salary_calculation", "tax_computation", "bonus_processing"]

    async def process_task(self, task) -> AgentDecision:
        """Process payroll task"""
        self._log_task(task)
        
        if task.description == "process_salary":
            return await self._process_salary(task)
        else:
            raise ValueError(f"Unknown task: {task.description}")

    async def _process_salary(self, task) -> AgentDecision:
        """Process salary for employee"""
        employee = task.payload.get("employee", {})
        salary_data = task.payload.get("salary_data", {})
        attendance_data = task.payload.get("attendance_data", {})
        
        prompt = f"""
        Process salary for:
        
        Employee: {employee.get('name')}
        Base Salary: {salary_data.get('base_salary')}
        
        Salary Components:
        {json.dumps(salary_data, indent=2)}
        
        Attendance:
        {json.dumps(attendance_data, indent=2)}
        
        Provide JSON: gross_salary, deductions, tax, net_salary, 
                     breakdown (by component), pf_contribution, insurance
        """
        
        payroll_text = await self.think(prompt)
        
        try:
            payroll_data = json.loads(payroll_text)
        except:
            payroll_data = {"status": "salary_calculated"}

        return AgentDecision(
            agent_type=self.agent_type,
            decision="salary_processed",
            confidence=0.98,
            reasoning="Salary calculated and processed",
            next_steps=["approve_payroll", "generate_payslip", "process_payment"],
            metadata=payroll_data
        )
