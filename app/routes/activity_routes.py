from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.activity_log import ActivityLog
from app.schemas.activity_schema import ActivityResponse

router = APIRouter(tags=["Activity Logs"])


@router.get("/activity", response_model=list[ActivityResponse])
def get_activity_logs(db: Session = Depends(get_db)):

    logs = (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .all()
    )

    return logs