from schemas import User, Access_log
from fastapi import HTTPException
from sqlalchemy.orm import Session
import models
from state import pending_user_data
from datetime import datetime, timedelta


def create_user(db: Session, user: User):
    user_data = models.User(**user.dict())
    if not user_data.name or not user_data.mobile_number:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return user_data


# def verify_user(db: Session, log: Access_log):
#     if log.rfid_uid:
#         db_query = (
#             db.query(models.User.rfid_uid)
#             .filter(models.User.rfid_uid==log.rfid_uid)
#             .first()
#     )
#     if not db_query:
#         raise HTTPException(status_code=404, detail="Rfid UID not found")
#     user_id = db.query(models.User.id).filter(models.User.rfid_uid == log.rfid_uid).first()
#     latest_log = (
#         db.query(models.AccessLog)
#         .filter(models.AccessLog.user_id == user_id)
#         .order_by(models.AccessLog.logging_time.desc())
#         .first()
#     )
#     if not latest_log:
#         is_active = False
#     if latest_log and latest_log.is_active == True:
#         is_active = False
#     elif latest_log and latest_log.is_active == False:
#         is_active = True
#     elif not latest_log:
#         is_active = True
#
#     db_log = models.AccessLog(user_id=user_id, rfid_uid=log.rfid_uid, is_active=is_active)
#     db.add(db_log)
#     db.commit()
#     db.refresh(db_log)
#     return db_log

def verify_user(db: Session, log: Access_log):

    # ✅ 1. If we're in admin registration mode
    if pending_user_data:

        created_time = pending_user_data.get("created_time")

        if created_time and datetime.utcnow() - created_time > timedelta(seconds=30):
            pending_user_data.clear()
            raise HTTPException(status_code=408, detail="⏰ Registration expired. Please start again.")
        name = pending_user_data.get("name")
        mobile = pending_user_data.get("mobile_number")
        # print(pending_user_data)

        # Check if RFID already exists
        existing = db.query(models.User).filter(models.User.rfid_uid == log.rfid_uid).first()
        existing_mob = db.query(models.User).filter(models.User.mobile_number == mobile).first()
        if existing or existing_mob:
            pending_user_data.clear()  # clear to avoid retry issues
            raise HTTPException(status_code=400, detail="User already exists.")

        # Register new user
        new_user = models.User(
            name=name,
            rfid_uid=log.rfid_uid,
            mobile_number=mobile
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        pending_user_data.clear()  # reset after use

        return {
            "message": "✅ User registered successfully",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "rfid_uid": new_user.rfid_uid,
                "mobile_number": new_user.mobile_number
            }
        }

    user = db.query(models.User).filter(models.User.rfid_uid == log.rfid_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="RFID UID not found")

    user_id = user.id

    latest_log = (
        db.query(models.AccessLog)
        .filter(models.AccessLog.user_id == user_id)
        .order_by(models.AccessLog.logging_time.desc())
        .first()
    )

    if not latest_log or latest_log.is_active == False:
        is_active = True   # Logging IN
    else:
        is_active = False  # Logging OUT

    db_log = models.AccessLog(
        user_id=user_id,
        rfid_uid=log.rfid_uid,
        is_active=is_active
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return {
        "message": f"✅ {'Login' if is_active else 'Logout'} successful",
        "user_id": user.id,
        "name": user.name,
        "logged_at": db_log.logging_time.isoformat()
    }


