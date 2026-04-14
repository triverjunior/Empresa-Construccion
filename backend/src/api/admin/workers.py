from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.models import user, schemas
from ...db.database import get_db
from .. import auth
from ...emails.sender import send_email

router = APIRouter()

@router.get("/api/workers")
def get_workers(db: Session = Depends(get_db), current_user: dict = Depends(auth.require_role("admin"))):
    workers = db.query(user.User).filter(user.User.role == "worker").all()
    return {
        "workers": [
            {
                "id": worker.id,
                "username": worker.username,
                "email": worker.email,
                "disponibility": worker.disponibility,
                "assigned_project_id": worker.assigned_project_id
            }
            for worker in workers
        ]
    }

@router.put("/api/workers/{worker_id}/data")
def update_worker_data(
    worker_id: int, 
    worker_data: schemas.WorkerUpdate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(auth.require_role("admin"))
):
    worker = db.query(user.User).filter(user.User.id == worker_id, user.User.role == "worker").first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    if worker_data.username != "" and worker_data.username != worker.username:
        if db.query(user.User).filter(user.User.username == worker_data.username).first():
            raise HTTPException(status_code=400, detail="Username already registered")
        setattr(worker, "username", worker_data.username)
    
    if worker_data.email != "" and worker_data.email != worker.email:
        if db.query(user.User).filter(user.User.email == worker_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        setattr(worker, "email", worker_data.email)
        
    db.commit()
    db.refresh(worker)
    return {"message": "Worker data updated successfully"}

@router.put("/api/workers/{worker_id}/disponibility")
def update_worker_disponibility(
    worker_id: int, 
    worker_data: schemas.WorkerDisponibilityUpdate,
    db: Session = Depends(get_db), 
    current_user: dict = Depends(auth.require_role("admin"))
):
    worker = db.query(user.User).filter(user.User.id == worker_id, user.User.role == "worker").first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    setattr(worker, "disponibility", worker_data.disponibility)
    setattr(worker, "assigned_project_id", None if worker_data.disponibility else worker_data.assigned_project_id)
    
    db.commit()
    db.refresh(worker)
    email_status = send_email(
        to_email=worker.email,
        subject="Disponibility Updated",
        body=f"Hi {worker.username}, your disponibility has been updated, you have a new project assigned."
    )
    if email_status != 'success':
        print(f"Worker availability updated but email failed for worker_id={worker.id}: {email_status}")
    return {
        "message": "Worker disponibility updated successfully",
        "email_status": email_status or "not_sent"
    }

@router.delete("/api/workers/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.require_role("admin"))):
    worker = db.query(user.User).filter(user.User.id == worker_id, user.User.role == "worker").first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    db.delete(worker)
    db.commit()
    return {"message": "Worker deleted successfully"}