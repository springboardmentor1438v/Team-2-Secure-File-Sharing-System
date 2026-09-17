from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


def log_activity(
    db,
    user_id,
    action,
    resource_type=None,
    resource_id=None,
    description=None,
    status="SUCCESS",
    ip_address=None
):

    print("Activity Logger Called")

    activity = ActivityLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        status=status,
        ip_address=ip_address
    )

    db.add(activity)
    db.commit()

    print("Activity Saved")