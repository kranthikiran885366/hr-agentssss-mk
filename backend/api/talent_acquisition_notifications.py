from fastapi import APIRouter, Query
from backend.models.sql_models import Notification
from backend.database.sql_database import SessionLocal

router = APIRouter()

@router.get("/api/talent-acquisition/notifications")
def get_notifications(user_id: str = Query(...)):
    db = SessionLocal()
    notifs = db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
    db.close()
    return [
        {
            "id": n.id,
            "message": n.message,
            "type": n.type,
            "read": n.read,
            "created_at": n.created_at.isoformat(),
            "event_type": n.event_type,
            "related_entity": n.related_entity,
        }
        for n in notifs
    ] 