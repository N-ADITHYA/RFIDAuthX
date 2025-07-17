from fastapi import FastAPI, Depends, Body, HTTPException
from sqlalchemy.orm import Session
import access, models, schemas
from database import session_local, engine
from security import authenticate_admin, create_access_token, get_current_admin
from fastapi.security import OAuth2PasswordRequestForm
from state import pending_user_data
from datetime import datetime

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
    return {"message": "✅ Registration started. Now scan user's RFID card."}
