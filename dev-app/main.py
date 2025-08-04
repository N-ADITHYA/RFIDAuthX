from fastapi import FastAPI, Depends, Body, HTTPException
from sqlalchemy.orm import Session
import access, models, schemas
from database import session_local, engine
from security import authenticate_admin, create_access_token, get_current_admin
from fastapi.security import OAuth2PasswordRequestForm
from state import pending_user_data
from datetime import datetime
from sqlalchemy import func, and_
from typing import List


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# pending_user_data = {}


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

@app.post("/access")
def accesslogs(deets: schemas.AccessGive, db: Session = Depends(get_db)):
    return access.verify_user(db, deets)

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_admin(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid admin credentials")

    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/start_registration")
def start_registration(
    name: str = Body(...),
    mobile_number: str = Body(...),
    admin: dict = Depends(get_current_admin)
):
    pending_user_data.clear()
    pending_user_data["name"] = name
    pending_user_data["mobile_number"] = mobile_number
    pending_user_data["created_time"] = datetime.utcnow()

    # pending_user_data = {
    #     "name": name,
    #     "mobile_number": mobile_number
    # }
    return {"message": " Registration started. Now scan user's RFID card."}


@app.post("/cancel_registration")
def cancel_registration(admin: dict = Depends(get_current_admin)):
    if pending_user_data:
        pending_user_data.clear()
        return {"message": "Registration Canceled by the user"}

    else:
        raise HTTPException(status_code=404, detail="User registration cancelled")


@app.get("/users")
def get_user(db: Session = Depends(get_db)):
    query = db.query(models.User).all()
    return query

@app.get("/logs")
def get_all_logs(db: Session = Depends(get_db)):
    query = db.query(models.AccessLog).all()
    return query


@app.get("/get_current_users_logged_in", response_model=List[schemas.User])
def get_current_logged_in_users(db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    # 1. Subquery: get latest log time per user
    subquery = (
        db.query(
            models.AccessLog.user_id,
            func.max(models.AccessLog.logging_time).label("latest_time")
        )
        .group_by(models.AccessLog.user_id)
        .subquery()
    )

    # 2. Join logs with subquery to get only latest log per user
    latest_logs = (
        db.query(models.AccessLog)
        .join(subquery, and_(
            models.AccessLog.user_id == subquery.c.user_id,
            models.AccessLog.logging_time == subquery.c.latest_time
        ))
        .filter(models.AccessLog.is_active == True)
        .all()
    )

    # 3. Extract unique user_ids who are still logged in
    user_ids = [log.user_id for log in latest_logs]
    users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()


    return users if users else []