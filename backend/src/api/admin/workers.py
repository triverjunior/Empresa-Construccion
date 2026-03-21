from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.models import user, schemas
from ...db.database import get_db
from .. import auth

router = APIRouter()

@router.get("/workers")
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

@router.put("/workers/{worker_id}/data")
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

@router.put("/workers/{worker_id}/disponibility")
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
    setattr(worker, "assigned_project_id", None if worker_data.disponibility else worker.assigned_project_id)
    
    db.commit()
    db.refresh(worker)
    return {"message": "Worker disponibility updated successfully"}

@router.delete("/workers/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.require_role("admin"))):
    worker = db.query(user.User).filter(user.User.id == worker_id, user.User.role == "worker").first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    db.delete(worker)
    db.commit()
    return {"message": "Worker deleted successfully"}