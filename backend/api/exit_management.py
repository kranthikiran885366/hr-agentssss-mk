from fastapi import APIRouter, Body, Query
from fastapi.responses import JSONResponse
from backend.database.mongo_database import get_mongo_client
from datetime import datetime

router = APIRouter()

@router.post("/api/exit/resignation")
async def initiate_resignation(employee_id: str = Body(...), reason: str = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    exit_id = f"exit_{employee_id}_{int(datetime.utcnow().timestamp())}"
    await mongo_db.exit_processes.insert_one({
        "id": exit_id,
        "employee_id": employee_id,
        "reason": reason,
        "status": "initiated",
        "initiated_at": datetime.utcnow().isoformat(),
        "steps": {"resignation": "completed"}
    })
    return {"success": True, "exit_id": exit_id, "message": "Resignation initiated"}

@router.post("/api/exit/interview")
async def schedule_exit_interview(exit_id: str = Body(...), scheduled_at: str = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.exit_processes.update_one(
        {"id": exit_id},
        {"$set": {"exit_interview": {"scheduled_at": scheduled_at, "status": "scheduled"}, "steps.exit_interview": "scheduled"}}
    )
    return {"success": True, "message": "Exit interview scheduled"}

@router.post("/api/exit/feedback")
async def submit_exit_feedback(exit_id: str = Body(...), feedback: dict = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.exit_processes.update_one(
        {"id": exit_id},
        {"$set": {"exit_feedback": feedback, "steps.exit_feedback": "submitted"}}
    )
    return {"success": True, "message": "Exit feedback submitted"}

@router.post("/api/exit/clearance")
async def update_clearance(exit_id: str = Body(...), checklist: list = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.exit_processes.update_one(
        {"id": exit_id},
        {"$set": {"clearance_checklist": checklist, "steps.clearance": "in_progress"}}
    )
    return {"success": True, "message": "Clearance checklist updated"}

@router.post("/api/exit/final-settlement")
async def process_final_settlement(exit_id: str = Body(...), settlement: dict = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.exit_processes.update_one(
        {"id": exit_id},
        {"$set": {"final_settlement": settlement, "steps.final_settlement": "processed"}}
    )
    return {"success": True, "message": "Final settlement processed"}

@router.post("/api/exit/documents")
async def generate_exit_documents(exit_id: str = Body(...), documents: list = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.exit_processes.update_one(
        {"id": exit_id},
        {"$set": {"exit_documents": documents, "steps.exit_documents": "generated"}}
    )
    return {"success": True, "message": "Exit documents generated"}

@router.get("/api/exit/process")
async def get_exit_process(employee_id: str = Query(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    doc = await mongo_db.exit_processes.find_one({"employee_id": employee_id}, sort=[("initiated_at", -1)])
    if not doc:
        return JSONResponse(status_code=404, content={"success": False, "message": "No exit process found"})
    doc["_id"] = str(doc["_id"])
    return {"success": True, "exit_process": doc} 