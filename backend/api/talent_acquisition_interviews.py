from fastapi import APIRouter, Body, Query
from datetime import datetime, timedelta

router = APIRouter()

# Placeholder: In production, integrate with Google/Outlook Calendar APIs

def get_mock_slots():
    now = datetime.utcnow()
    return [
        {
            "start": (now + timedelta(days=1, hours=9)).isoformat(),
            "end": (now + timedelta(days=1, hours=10)).isoformat(),
        },
        {
            "start": (now + timedelta(days=1, hours=11)).isoformat(),
            "end": (now + timedelta(days=1, hours=12)).isoformat(),
        },
        {
            "start": (now + timedelta(days=2, hours=14)).isoformat(),
            "end": (now + timedelta(days=2, hours=15)).isoformat(),
        },
    ]

@router.get("/api/talent-acquisition/interviews/slots")
def get_available_slots(job_id: str = Query(...)):
    # In production, fetch from Google/Outlook Calendar
    return get_mock_slots()

@router.post("/api/talent-acquisition/interviews/schedule")
def schedule_interview(
    candidate_id: str = Body(...),
    job_id: str = Body(...),
    slot: dict = Body(...),
    interviewer_email: str = Body(...),
    candidate_email: str = Body(...),
):
    # In production, create Google/Outlook Calendar event and store event link
    event_link = f"https://calendar.google.com/event?eid=mock_{candidate_id}_{job_id}"
    # Store event details in DB (not shown here)
    return {
        "status": "scheduled",
        "event_link": event_link,
        "slot": slot,
        "candidate_id": candidate_id,
        "job_id": job_id,
    } 