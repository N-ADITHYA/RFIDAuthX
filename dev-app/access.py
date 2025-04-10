from schemas import Access_log, User
import models
from sqlalchemy.orm import Session
from fastapi import HTTPException



def create_user(db: Session, user: User):
    user_data = models.User(**user.dict())
    if not user_data.name or not user_data.mobile_number:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data


def verify_user(db: Session, log: Access_log):
    if log.rfid_uid:
        db_query = (
            db.query(models.User.rfid_uid)
            .filter(models.User.rfid_uid==log.rfid_uid)
            .first()
    )
    if not db_query:
        raise HTTPException(status_code=404, detail="Rfid UID not found")
    user_id = db.query(models.User.id).filter(models.User.rfid_uid == log.rfid_uid)
    latest_log = (
        db.query(models.AccessLog)
        .filter(models.AccessLog.user_id == user_id)
        .order_by(models.AccessLog.logging_time.desc())
        .first()
    )
    if not latest_log:
        is_active = False
    if latest_log and latest_log.is_active == True:
        is_active = False
    elif latest_log and latest_log.is_active == False:
        is_active = True
    elif not latest_log:
        is_active = True

    db_log = models.AccessLog(user_id=user_id, rfid_uid=log.rfid_uid, is_active=is_active)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

