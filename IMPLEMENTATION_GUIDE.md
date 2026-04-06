# HR Agent System - Implementation Guide

## Phase 2: Backend Architecture Setup (COMPLETE)

This guide outlines the new production-ready backend architecture implemented.

### Core Components Implemented

#### 1. LLM Client (`backend/core/llm_client.py`)
Real integration with OpenAI and Claude APIs.

**Features:**
- Support for multiple LLM providers (OpenAI, Claude, Groq)
- Async and sync API calls
- Streaming responses
- Structured JSON output
- Conversation history management
- Configurable models and parameters

**Usage:**
```python
from backend.core import get_llm_client, LLMConfig, LLMProvider

# Get default client (OpenAI)
client = get_llm_client()

# Or with custom config
config = LLMConfig(
    provider=LLMProvider.CLAUDE,
    model="claude-3-sonnet-20240229",
    temperature=0.7
)
client = LLMClient(config)

# Simple completion
response = await client.complete("Tell me about this candidate...")

# Streaming
async for chunk in client.stream_complete(prompt):
    print(chunk, end='')

# Structured output
schema = {
    "score": "number",
    "fit_assessment": "string",
    "next_step": "string"
}
result = client.structured_output(prompt, schema)
```

#### 2. Agent Orchestrator (`backend/core/agent_orchestrator.py`)
Multi-agent system with real LLM-powered decision making.

**Components:**
- **HRAgent**: Base agent class
- **RecruitmentAgent**: Candidate screening and ranking
- **InterviewAgent**: Interview conduction and evaluation
- **OnboardingAgent**: New hire workflow planning
- **AgentOrchestrator**: Coordinates all agents

**Features:**
- LLM-powered decision making
- Agent communication protocol
- Task queuing and execution
- Status tracking
- Confidence scoring
- Structured decisions

**Usage:**
```python
from backend.core import get_orchestrator, Task, AgentType

orchestrator = get_orchestrator()

# Create a task
task = Task(
    id="task-123",
    agent_type=AgentType.RECRUITMENT,
    description="screen_candidate",
    payload={
        "name": "John Doe",
        "experience": "5 years backend",
        "skills": ["Python", "FastAPI"],
        "job_description": "Senior Backend Engineer..."
    }
)

# Execute task
decision = await orchestrator.execute_task(task)

# Results
print(f"Decision: {decision.decision}")
print(f"Confidence: {decision.confidence}")
print(f"Reasoning: {decision.reasoning}")
print(f"Next steps: {decision.next_steps}")
```

### API Endpoints

#### Recruitment API (`backend/api/v1_recruitment.py`)
Real agent-powered recruitment endpoints.

**POST** `/api/v1/agents/recruitment/screen-candidate`
- Input: Candidate + Job details
- Output: Screening decision with score
- Agent: RecruitmentAgent
- Response:
  ```json
  {
    "decision": "proceed_to_interview",
    "confidence": 0.87,
    "reasoning": "Strong technical background matching JD...",
    "next_steps": ["schedule_interview"],
    "score": 87,
    "metadata": {...}
  }
  ```

**POST** `/api/v1/agents/recruitment/rank-candidates`
- Input: Multiple candidates + Job
- Output: Ranked list with top candidate
- Agent: RecruitmentAgent
- Response:
  ```json
  {
    "ranking": [
      {"name": "Candidate A", "score": 92, "reason": "..."},
      {"name": "Candidate B", "score": 85, "reason": "..."}
    ],
    "top_candidate_id": "cand-123",
    "reasoning": "Comprehensive ranking based on fit..."
  }
  ```

**GET** `/api/v1/agents/recruitment/agents/status`
- Output: Agent status and capabilities

### Frontend Integration

**TypeScript Endpoint** (`app/api/v1/recruitment/screen-candidate/route.ts`)

Bridges Next.js frontend with Python FastAPI backend:
```typescript
POST /api/v1/recruitment/screen-candidate
Body: { candidateId, jobId }

Response:
{
  success: true,
  decision: {...},
  screening_score: 87,
  recommendation: "proceed_to_interview",
  next_steps: [...]
}
```

Updates database with agent decision:
```typescript
// Candidate score updated
await prisma.candidate.update({
  where: { id: candidateId },
  data: {
    score: screening_score,
    status: "SCREENING"
  }
})
```

### Environment Configuration

Required environment variables:

```bash
# LLM Configuration
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Backend
SECRET_KEY=your-secret
DATABASE_URL=postgresql://...
MONGO_URL=mongodb://...

# CORS & URLs
BACKEND_CORS_ORIGINS=http://localhost:5000
FASTAPI_BASE=http://localhost:8000
```

### Data Flow

1. **User Action** (Frontend)
   ```
   HR User clicks "Screen Candidate"
   ```

2. **API Request** (Next.js)
   ```
   POST /api/v1/recruitment/screen-candidate
   { candidateId: "cand-123", jobId: "job-456" }
   ```

3. **Data Fetch** (TypeScript Backend)
   ```
   - Query Prisma for candidate details
   - Query Prisma for job details
   - Fetch resume content from database
   ```

4. **Agent Processing** (FastAPI)
   ```
   POST to Python backend
   Recruitment Agent analyzes candidate
   Uses LLM to make decision
   ```

5. **LLM Call** (OpenAI/Claude)
   ```
   async LLM.complete(
     "Screen this candidate for Senior Backend..."
   )
   ```

6. **Decision** (Agent Returns)
   ```json
   {
     "decision": "proceed_to_interview",
     "confidence": 0.87,
     "score": 87
   }
   ```

7. **Database Update** (TypeScript)
   ```
   Update candidate status & score
   Store decision in audit log
   ```

8. **Response** (Frontend)
   ```json
   {
     "success": true,
     "screening_score": 87,
     "recommendation": "proceed_to_interview"
   }
   ```

### Running the System

#### 1. Start Python Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

#### 2. Configure LLM
Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`

#### 3. Start Next.js Frontend
```bash
pnpm dev
# Runs on http://localhost:5000
```

#### 4. Test Endpoint
```bash
curl -X POST http://localhost:5000/api/v1/recruitment/screen-candidate \
  -H "Content-Type: application/json" \
  -d '{
    "candidateId": "cand-123",
    "jobId": "job-456"
  }'
```

### Agent Capabilities

#### RecruitmentAgent
- ✅ Resume parsing and analysis
- ✅ Candidate-to-JD matching
- ✅ Skill assessment
- ✅ Experience evaluation
- ✅ Candidate ranking
- ✅ Fit scoring

#### InterviewAgent
- ✅ Interview question generation
- ✅ Response evaluation
- ✅ Communication scoring
- ✅ Technical depth assessment
- ✅ Hiring recommendation

#### OnboardingAgent
- ✅ Workflow planning
- ✅ Task assignment
- ✅ Mentor assignment logic
- ✅ Document requirement tracking

### Security

**Authentication:**
- JWT tokens required
- Role-based access control
- HR/Admin only for agent endpoints

**API Security:**
- CORS configured
- Input validation
- Error handling without exposure
- Audit logging

**Data Security:**
- Database transactions
- Encrypted credentials
- No sensitive data in logs

### Error Handling

All agent endpoints handle:
- LLM API failures → graceful degradation
- Database errors → transaction rollback
- Invalid input → 400 Bad Request
- Unauthorized access → 401 Unauthorized
- Server errors → 500 with logging

### Monitoring

Track agent performance:
```python
orchestrator.get_agent_capabilities(AgentType.RECRUITMENT)
# Returns: ["resume_matching", "candidate_ranking", ...]

orchestrator.get_task_status(task_id)
# Returns: Task status and result

len(orchestrator.completed_tasks)
# Total processed tasks
```

### Next Steps

**Phase 3: Complete More Agents**
- Interview evaluation system
- Verification agent
- Onboarding automation
- Performance management

**Phase 4: External Integrations**
- Twilio for voice calls
- SendGrid for emails
- Google Workspace API
- Document verification APIs

### Troubleshooting

**LLM errors:**
```
"OPENAI_API_KEY environment variable not set"
→ Add OPENAI_API_KEY to .env.local
```

**Agent not responding:**
```
Check FastAPI is running: http://localhost:8000/docs
Check logs: uvicorn output
```

**Database connection failed:**
```
Verify DATABASE_URL in .env
Check PostgreSQL is running
```

### References

- LLM Client: `backend/core/llm_client.py`
- Agent Orchestrator: `backend/core/agent_orchestrator.py`
- Recruitment API: `backend/api/v1_recruitment.py`
- Frontend Route: `app/api/v1/recruitment/screen-candidate/route.ts`
- Configuration: `backend/utils/config.py`
