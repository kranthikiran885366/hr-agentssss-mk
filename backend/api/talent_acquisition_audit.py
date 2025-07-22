from fastapi import APIRouter, Query
from backend.models.sql_models import AuditLog
from backend.database.sql_database import SessionLocal

router = APIRouter()

@router.get("/api/talent-acquisition/audit-logs")
def get_audit_logs(
    entity_type: str = Query(None),
    entity_id: str = Query(None),
    user_id: str = Query(None),
):
    db = SessionLocal()
    query = db.query(AuditLog)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    logs = query.order_by(AuditLog.timestamp.desc()).all()
    db.close()
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "details": log.details,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ] 