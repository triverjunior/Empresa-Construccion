from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import cast
from jose import jwt, JWTError
from dotenv import load_dotenv
from ..db.models import user, schemas
from ..db.database import get_db, engine
from ..auth import utils
import os

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env')))
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")

    if not secret_key or not algorithm:
        raise ValueError("SECRET_KEY and ALGORITHM must be set in environment variables")

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username = payload.get("sub")
        role = payload.get("role")

        if username is None or role is None:
            raise credential_exception
    
    except JWTError:
        raise credential_exception
    
    return {"username": username, "role": role}

def require_role(required_role: str):
    
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != required_role:
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient permissions")
        return current_user
    
    return role_checker

@router.post("/register")
def register_user(user_reg: schemas.UserCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_role("admin"))):
    existing_user = db.query(user.User).filter(user.User.email == user_reg.email).first()
    
    if existing_user:
        return {"error": "Email already registered"}
    
    hashed_password = utils.hash_password(user_reg.password)

    new_user = user.User(
        username=user_reg.username,
        email=user_reg.email,
        hashed_password=hashed_password,
        role=user_reg.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }

@router.post("/login")
def login (form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_sel = db.query(user.User).filter(user.User.username == form_data.username).first()
    
    if not user_sel:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    hashed_password = cast(str, user_sel.hashed_password)

    if not utils.verify_password(form_data.password, hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token_data = {
        "sub": user_sel.username,
        "role": user_sel.role
    }

    token = utils.create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}