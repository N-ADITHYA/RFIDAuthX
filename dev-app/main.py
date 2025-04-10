from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import access, models, schemas
from database import session_local, engine
app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

@app.post("/access", response_model=schemas.AccessGive)
def accesslogs(deets: schemas.AccessGive, db: Session = Depends(get_db)):
    return access.verify_user(db, deets)

@app.post("/create_user", response_model=schemas.User)
def create_user(deet: schemas.UserShow, db: Session = Depends(get_db)):
    return access.create_user(db, deet)