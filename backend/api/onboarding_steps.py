from fastapi import APIRouter, Body
from backend.database.mongo_database import get_mongo_client
from datetime import datetime

router = APIRouter()

@router.post("/api/onboarding/equipment-provisioning")
async def equipment_provisioning(session_id: str = Body(...), equipment: list = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"equipment": equipment, "equipment_provisioned_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Equipment provisioned"}

@router.post("/api/onboarding/policy-acknowledgment")
async def policy_acknowledgment(session_id: str = Body(...), acknowledged: bool = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"policy_acknowledged": acknowledged, "policy_acknowledged_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Policy acknowledged"}

@router.post("/api/onboarding/benefits-enrollment")
async def benefits_enrollment(session_id: str = Body(...), benefits: list = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"benefits": benefits, "benefits_enrolled_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Benefits enrolled"}

@router.post("/api/onboarding/training-assignment")
async def training_assignment(session_id: str = Body(...), trainings: list = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"trainings": trainings, "trainings_assigned_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Training assigned"}

@router.post("/api/onboarding/system-access-setup")
async def system_access_setup(session_id: str = Body(...), systems: list = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"systems": systems, "system_access_setup_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "System access set up"}

@router.post("/api/onboarding/welcome-orientation")
async def welcome_orientation(session_id: str = Body(...), attended: bool = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"welcome_orientation_attended": attended, "welcome_orientation_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Welcome orientation attended"}

@router.post("/api/onboarding/workspace-setup")
async def workspace_setup(session_id: str = Body(...), workspace: dict = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"workspace": workspace, "workspace_setup_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Workspace set up"}

@router.post("/api/onboarding/probation-tracking")
async def probation_tracking(session_id: str = Body(...), status: str = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"probation_status": status, "probation_updated_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Probation status updated"}

@router.post("/api/onboarding/buddy-assignment")
async def buddy_assignment(session_id: str = Body(...), buddy: dict = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"buddy": buddy, "buddy_assigned_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Buddy assigned"}

@router.post("/api/onboarding/id-card-creation")
async def id_card_creation(session_id: str = Body(...), id_card: dict = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"id_card": id_card, "id_card_created_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "ID card created"}

@router.post("/api/onboarding/welcome-kit")
async def welcome_kit(session_id: str = Body(...), kit: dict = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"welcome_kit": kit, "welcome_kit_sent_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Welcome kit sent"}

@router.post("/api/onboarding/manager-introductions")
async def manager_introductions(session_id: str = Body(...), manager: dict = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"manager": manager, "manager_introduced_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Manager introduced"}

@router.post("/api/onboarding/policy-e-signing")
async def policy_e_signing(session_id: str = Body(...), signed: bool = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"policy_signed": signed, "policy_signed_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Policy signed"}

@router.post("/api/onboarding/completion-certification")
async def completion_certification(session_id: str = Body(...), certificate: dict = Body(...)):
    mongo_client = get_mongo_client()
    mongo_db = mongo_client.hr_system
    await mongo_db.onboarding_sessions.update_one(
        {"id": session_id},
        {"$set": {"certificate": certificate, "certificate_issued_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "message": "Completion certificate issued"} 