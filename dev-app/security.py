from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

# Auth config
SECRET_KEY = "your_super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Token and password tools
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Fake hardcoded admin (or fetch from env later)
admin_user = {
    "username": "admin",
    "hashed_password": pwd_context.hash("admin123")
}

def verify_password(raw, hashed):
    return pwd_context.verify(raw, hashed)

def authenticate_admin(username: str, password: str):
    if username != admin_user["username"]:
        return None
    if not verify_password(password, admin_user["hashed_password"]):
        return None
    return {"username": username}

def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != admin_user["username"]:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": payload["sub"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
