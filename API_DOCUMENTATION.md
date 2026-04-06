# HR Agents System - API Documentation

## Overview

Production-grade AI-powered HR system with comprehensive APIs for recruitment, screening, interviews, verification, and onboarding.

## Base URLs

- **Frontend API**: `http://localhost:3000/api/v1`
- **Python Backend**: `http://localhost:8000/api/v1`

## Authentication

All API requests require Bearer token authentication:

```bash
Authorization: Bearer {API_SECRET_KEY}
```

---

## Recruitment APIs

### Screen Candidate

Screen a single candidate against job requirements with comprehensive analysis.

**Endpoint:** `POST /screening/screen-candidate`

**Request Body:**
```json
{
  "candidate": {
    "id": "cand_001",
    "name": "John Doe",
    "skills": [
      {"name": "Python", "level": "senior", "years": 5},
      {"name": "AWS", "level": "mid", "years": 3}
    ],
    "experience": {
      "total_years": 8,
      "positions": [
        {
          "title": "Senior Engineer",
          "company": "Tech Corp",
          "start_date": "2020-01-01",
          "end_date": "2023-12-31"
        }
      ]
    },
    "education": {
      "highest_degree": "master",
      "field_of_study": "Computer Science",
      "graduation_date": "2015-05-15"
    }
  },
  "jobRequirements": {
    "id": "job_001",
    "title": "Senior Software Engineer",
    "skills": [
      {"name": "Python", "level": "senior", "years": 3, "weight": 1.0},
      {"name": "AWS", "level": "mid", "years": 2, "weight": 0.8}
    ],
    "experience_years": 5,
    "education_level": "bachelor"
  }
}
```

**Response:**
```json
{
  "success": true,
  "screening": {
    "candidate_id": "cand_001",
    "candidate_name": "John Doe",
    "overall_score": 87.5,
    "match_level": "strong",
    "recommendation": "Hire",
    "criteria_scores": {
      "skills_match": 92.5,
      "experience_level": 85.0,
      "education_match": 100.0,
      "cultural_fit": 75.0
    },
    "strengths": [
      "Excellent skill match",
      "Relevant experience",
      "Strong technical background"
    ],
    "gaps": [
      "Limited cloud architecture experience"
    ]
  },
  "timestamp": "2026-04-06T10:30:00Z"
}
```

---

### Rank Candidates

Rank multiple candidates against a job, returning top candidates with scoring.

**Endpoint:** `POST /screening/rank-candidates`

**Request Body:**
```json
{
  "candidates": [
    { "id": "cand_001", "name": "John Doe", ... },
    { "id": "cand_002", "name": "Jane Smith", ... }
  ],
  "jobRequirements": {
    "id": "job_001",
    "title": "Senior Software Engineer",
    ...
  },
  "topN": 10
}
```

**Response:**
```json
{
  "success": true,
  "ranking": {
    "job_id": "job_001",
    "job_title": "Senior Software Engineer",
    "total_candidates": 15,
    "ranked_candidates": [
      ["cand_001", "John Doe", 87.5, "strong"],
      ["cand_002", "Jane Smith", 82.3, "strong"],
      ["cand_003", "Bob Wilson", 71.2, "good"]
    ],
    "statistics": {
      "average_score": 72.4,
      "max_score": 87.5,
      "min_score": 45.2,
      "excellent_count": 2,
      "strong_count": 5
    }
  },
  "candidatesProcessed": 15,
  "topCandidatesReturned": 10
}
```

---

## Interview APIs

### Start Interview Session

Start a new structured interview session for a candidate.

**Endpoint:** `POST /interviews/start-session`

**Request Body:**
```json
{
  "candidateId": "cand_001",
  "candidateName": "John Doe",
  "jobId": "job_001",
  "jobTitle": "Senior Software Engineer",
  "interviewType": "technical"
}
```

**Interview Types:**
- `screening` - Initial screening interview
- `technical` - Technical skills assessment
- `behavioral` - Behavioral and soft skills
- `culture_fit` - Company culture alignment
- `hybrid` - Combination of all types

**Response:**
```json
{
  "success": true,
  "session": {
    "session_id": "sess_001",
    "candidate_id": "cand_001",
    "status": "in_progress",
    "current_question": {
      "question_id": "tech_01",
      "text": "Explain your approach to designing a scalable system...",
      "category": "technical",
      "difficulty": "hard",
      "max_time_seconds": 180
    },
    "current_question_index": 0,
    "total_questions": 4
  }
}
```

---

### Submit Interview Response

Submit a candidate response to an interview question.

**Endpoint:** `POST /interviews/submit-response`

**Request Body:**
```json
{
  "sessionId": "sess_001",
  "responseText": "I would approach this by first...",
  "responseTimeSeconds": 145,
  "isVoice": false
}
```

**Response:**
```json
{
  "success": true,
  "evaluation": {
    "response_id": "resp_001",
    "quality_score": 82.5,
    "quality_level": "good",
    "skills_demonstrated": ["system_design", "scalability"],
    "communication_score": 0.85,
    "technical_accuracy": 0.88,
    "feedback": "Excellent response with concrete examples."
  },
  "nextQuestion": {
    "question_id": "tech_02",
    "text": "How would you handle a database bottleneck?",
    "max_time_seconds": 180
  },
  "sessionStatus": "in_progress"
}
```

---

## Document Verification APIs

### Assess Fraud Risk

Assess fraud risk and detect inconsistencies in candidate information.

**Endpoint:** `POST /verification/assess-fraud-risk`

**Request Body:**
```json
{
  "candidateData": {
    "id": "cand_001",
    "name": "John Doe"
  },
  "resumeData": {
    "education": {
      "highest_degree": "master",
      "field_of_study": "Computer Science"
    },
    "experience": {
      "positions": [
        {
          "title": "Senior Engineer",
          "company": "Tech Corp",
          "start_date": "2020-01-01",
          "end_date": "2023-12-31"
        }
      ]
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "assessment": {
    "overall_risk_level": "low",
    "risk_score": 15.5,
    "fraud_indicators": [],
    "red_flags": [],
    "recommendation": "proceed",
    "requires_manual_review": false
  },
  "requiresReview": false,
  "timestamp": "2026-04-06T10:30:00Z"
}
```

---

### Background Check

Initiate a background check for a candidate.

**Endpoint:** `POST /verification/background-check`

**Request Body:**
```json
{
  "candidateId": "cand_001",
  "candidateName": "John Doe",
  "ssn": "XXX-XX-1234",
  "includeEducationVerification": true,
  "includeEmploymentVerification": true,
  "includeCriminalCheck": true,
  "includeSanctionsCheck": true
}
```

**Response:**
```json
{
  "success": true,
  "checkResult": {
    "candidate_id": "cand_001",
    "check_status": "verified",
    "criminal_record_found": false,
    "sanctions_found": false,
    "credit_issues": false,
    "risk_level": "low"
  },
  "status": "verified",
  "riskLevel": "low"
}
```

---

## Onboarding APIs

### Create Onboarding Checklist

Create a comprehensive onboarding checklist for a new hire.

**Endpoint:** `POST /onboarding/create-checklist`

**Request Body:**
```json
{
  "hireId": "emp_001",
  "hireName": "John Doe",
  "jobTitle": "Senior Software Engineer",
  "department": "Engineering",
  "startDate": "2026-04-15",
  "roleType": "technical"
}
```

**Response:**
```json
{
  "success": true,
  "checklist": {
    "checklist_id": "check_001",
    "hire_id": "emp_001",
    "status": "not_started",
    "progress_percentage": 0.0,
    "tasks": [
      {
        "task_id": "doc_001",
        "task_name": "Complete I-9 Verification",
        "category": "documentation",
        "status": "pending",
        "due_date": "2026-04-18",
        "assigned_to": "HR"
      },
      {
        "task_id": "acct_001",
        "task_name": "Create Email Account",
        "category": "account_setup",
        "status": "pending",
        "due_date": "2026-04-16",
        "assigned_to": "System"
      }
    ]
  }
}
```

---

### Complete Onboarding Task

Mark an onboarding task as completed.

**Endpoint:** `POST /onboarding/complete-task`

**Request Body:**
```json
{
  "checklistId": "check_001",
  "taskId": "doc_001",
  "completionProof": "i9_verified_20260414"
}
```

**Response:**
```json
{
  "success": true,
  "checklist": {
    "checklist_id": "check_001",
    "progress_percentage": 8.3,
    "status": "in_progress",
    "tasks": [...]
  },
  "completedTask": {
    "task_id": "doc_001",
    "status": "completed",
    "completed_date": "2026-04-14T10:30:00Z"
  }
}
```

---

### Create Employee Account

Create an employee account with system setup.

**Endpoint:** `POST /onboarding/create-account`

**Request Body:**
```json
{
  "hireId": "emp_001",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@company.com",
  "phone": "+1-555-123-4567"
}
```

**Response:**
```json
{
  "success": true,
  "account": {
    "employee_id": "EMP202604061234",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@company.com",
    "username": "john.doe",
    "github_username": "john.doe",
    "slack_username": "john.doe",
    "status": "pending_setup",
    "password_reset_token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  }
}
```

---

## Error Responses

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": "Descriptive error message",
  "code": "ERROR_CODE",
  "timestamp": "2026-04-06T10:30:00Z"
}
```

**Common Error Codes:**
- `INVALID_REQUEST` - Missing or invalid request parameters
- `AUTHENTICATION_ERROR` - Auth token missing or invalid
- `RESOURCE_NOT_FOUND` - Resource not found
- `INTERNAL_ERROR` - Server error

---

## Rate Limiting

Rate limits are enforced per API key:
- Screening endpoints: 100 requests/minute
- Interview endpoints: 50 requests/minute
- Verification endpoints: 30 requests/minute
- Onboarding endpoints: 50 requests/minute

---

## Webhooks

Receive real-time notifications for important events:

```bash
POST {your_webhook_url}
```

**Events:**
- `screening.completed` - Candidate screening complete
- `interview.started` - Interview session started
- `interview.completed` - Interview session complete
- `verification.completed` - Verification complete
- `onboarding.task_completed` - Onboarding task completed
- `onboarding.completed` - All onboarding tasks complete

---

## Code Examples

### Python
```python
import requests

url = "http://localhost:3000/api/v1/screening/screen-candidate"
headers = {"Authorization": f"Bearer {API_KEY}"}
response = requests.post(url, json=payload, headers=headers)
result = response.json()
```

### JavaScript/Node.js
```javascript
const response = await fetch('/api/v1/screening/screen-candidate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${API_KEY}`
  },
  body: JSON.stringify(payload)
});
const result = await response.json();
```

### cURL
```bash
curl -X POST http://localhost:3000/api/v1/screening/screen-candidate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d @payload.json
```

---

## Support

For API issues or questions:
- Email: api-support@company.com
- Documentation: https://docs.company.com/hr-agents
- GitHub Issues: https://github.com/company/hr-agents
