from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.models import project, user
from ...db.database import get_db
from .. import auth

router = APIRouter()

@router.get("/api/active-project")
def get_my_active_project(db: Session = Depends(get_db), current_user: dict = Depends(auth.require_role("worker"))):
    user_sel = db.query(user.User).filter(user.User.id == current_user["id"]).first()
    
    if not user_sel:
        raise HTTPException(status_code=404, detail="User not found")
    
    active_project = db.query(project.Project).filter(project.Project.id == user_sel.assigned_project_id).first()

    if not active_project:
        raise HTTPException(status_code=404, detail="Assigned project not found")

    return active_project