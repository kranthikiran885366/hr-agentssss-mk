# HR Agent System - Quick Reference Guide

## Running the System

### 1. Start Python Backend
```bash
cd /path/to/project
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0
```

### 2. Start Next.js Frontend
```bash
pnpm dev
# Runs on http://localhost:5000
```

### 3. Set Environment Variables
```bash
# Create .env.local with:
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...
```

## Quick Examples

### Screen a Candidate
```bash
curl -X POST http://localhost:5000/api/v1/recruitment/screen-candidate \
  -H "Content-Type: application/json" \
  -d '{
    "candidateId": "cand-123",
    "jobId": "job-456"
  }'
```

### Rank Multiple Candidates
```bash
curl -X POST http://localhost:8000/api/v1/agents/recruitment/rank-candidates \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token" \
  -d '{
    "candidates": [
      {"id": "cand-1", "name": "Alice", "experience": "5 years", "skills": ["Python"]},
      {"id": "cand-2", "name": "Bob", "experience": "10 years", "skills": ["Python", "AWS"]}
    ],
    "job": {
      "id": "job-1",
      "title": "Senior Backend Engineer",
      "description": "Looking for..."
    }
  }'
```

## Agent Usage Guide

### Adding a New Task
```python
from backend.core import Task, AgentType

task = Task(
    id="unique-id",
    agent_type=AgentType.RECRUITMENT,  # or any agent type
    description="screen_candidate",     # agent-specific
    payload={...},                      # agent-specific data
    priority=1                          # higher = more urgent
)
```

### Processing a Task
```python
from backend.core import get_orchestrator

orchestrator = get_orchestrator()
decision = await orchestrator.execute_task(task)

# Results
print(decision.decision)        # The actual decision
print(decision.confidence)      # 0.0 to 1.0
print(decision.reasoning)       # Why this decision
print(decision.next_steps)      # What happens next
print(decision.metadata)        # Additional data
```

### Getting Agent Info
```python
from backend.core import get_orchestrator, AgentType

orchestrator = get_orchestrator()

# Get capabilities
capabilities = orchestrator.get_agent_capabilities(AgentType.RECRUITMENT)
# Returns: ["resume_matching", "candidate_ranking", "jd_analysis"]

# Get task status
task = orchestrator.get_task_status("task-id")

# Get completed tasks
count = len(orchestrator.completed_tasks)
```

## Available Agents

| Agent | Type | Key Methods | Capabilities |
|-------|------|-------------|--------------|
| RecruitmentAgent | RECRUITMENT | screen_candidate, rank_candidates | resume_matching, candidate_ranking, jd_analysis |
| InterviewAgent | INTERVIEW | evaluate_response, generate_question | question_generation, response_evaluation, scoring |
| OnboardingAgent | ONBOARDING | plan_onboarding | workflow_planning, mentor_assignment, progress_tracking |
| PerformanceAgent | PERFORMANCE | conduct_review, set_goals, assess_skills | performance_review, goal_setting, skill_assessment |
| ExitAgent | EXIT | process_resignation, calculate_settlement | exit_interview, settlement_calculation, offboarding_plan |
| LeaveAgent | LEAVE | evaluate_request | leave_approval, balance_calculation, policy_enforcement |
| EngagementAgent | ENGAGEMENT | assess_sentiment, create_engagement_plan | sentiment_analysis, retention_risk, engagement_initiatives |
| PayrollAgent | PAYROLL | process_salary | salary_calculation, tax_computation, bonus_processing |

## Common Tasks

### Recruitment Workflow
```python
# 1. Screen candidate
recruitment_task = Task(
    agent_type=AgentType.RECRUITMENT,
    description="screen_candidate",
    payload={"name": "...", "experience": "...", "job_description": "..."}
)
decision = await orchestrator.execute_task(recruitment_task)

# 2. If passed, generate interview questions
if decision.decision == "proceed_to_interview":
    interview_task = Task(
        agent_type=AgentType.INTERVIEW,
        description="generate_question",
        payload={"role": "Backend Engineer", "stage": "screening"}
    )
    question = await orchestrator.execute_task(interview_task)
```

### Performance Review Workflow
```python
# 1. Conduct review
review_task = Task(
    agent_type=AgentType.PERFORMANCE,
    description="conduct_review",
    payload={
        "employee": {"name": "John", "role": "Engineer"},
        "manager_feedback": "Great performer",
        "metrics": {"delivery_rate": 0.95, "quality": 0.92}
    }
)
review = await orchestrator.execute_task(review_task)

# 2. Set goals based on review
goals_task = Task(
    agent_type=AgentType.PERFORMANCE,
    description="set_goals",
    payload={"employee": {...}, "review_data": review.metadata}
)
goals = await orchestrator.execute_task(goals_task)
```

## Error Handling

All agent methods can raise exceptions. Always wrap in try-except:

```python
try:
    decision = await orchestrator.execute_task(task)
except Exception as e:
    # Agent failed
    # Check logs: task.error
    print(f"Task failed: {e}")
    # Fallback logic or escalation
```

## Debugging

### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
export DEBUG=true
```

### Check Agent Status
```bash
curl http://localhost:8000/api/v1/agents/recruitment/agents/status
```

### View Completed Tasks
```python
orchestrator = get_orchestrator()
for task in orchestrator.completed_tasks[-10:]:  # Last 10
    print(f"Task: {task.id}, Status: {task.status}, Result: {task.result}")
```

## Performance Tips

1. **Batch Tasks**: Process multiple candidates at once
2. **Use Caching**: Cache JD analysis for same job
3. **Async Processing**: Don't wait for agent responses synchronously
4. **Monitor Latency**: Track decision times
5. **Error Recovery**: Implement retry logic

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "OPENAI_API_KEY not set" | Missing env var | Add to .env.local |
| "No agent registered" | Unknown agent type | Check AgentType enum |
| "LLM API error" | API failure | Check quota, rate limits |
| "Database connection" | DB unavailable | Verify DATABASE_URL |
| "Timeout" | Task taking too long | Increase timeout or optimize |

## API Response Format

All agent endpoints return:
```json
{
  "decision": "string",           // The decision made
  "confidence": 0.0-1.0,          // Confidence level
  "reasoning": "string",          // Why this decision
  "next_steps": ["string"],       // What happens next
  "score": 0-100,                 // If applicable
  "metadata": {}                  // Additional data
}
```

## Development Workflow

1. Create Task with agent_type and description
2. Set payload with agent-specific data
3. Call `orchestrator.execute_task(task)`
4. Receive AgentDecision
5. Extract decision.decision for business logic
6. Use decision.next_steps to trigger downstream tasks
7. Store decision.metadata for audit trail

## File Locations

Core System:
- `backend/core/llm_client.py` - LLM integration
- `backend/core/agent_orchestrator.py` - Base agents
- `backend/core/agents_extended.py` - Extended agents
- `backend/core/__init__.py` - Exports

API:
- `backend/api/v1_recruitment.py` - Recruitment endpoints
- `app/api/v1/recruitment/...` - Frontend bridges

Configuration:
- `backend/utils/config.py` - Settings
- `.env.local` - Environment variables

## Next: Implement More Features

See `PHASE_3_COMPLETION.md` for what's next:
- Resume parsing with NLP
- Voice interviews with Twilio
- Document verification with OCR
- Email integrations
- Slack notifications
