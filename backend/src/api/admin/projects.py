from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.models import user, schemas, project
from ...db.database import get_db
from .. import auth

router = APIRouter()

@router.get("/projects")
def get_projects(db: Session = Depends(get_db), current_user: dict = Depends(auth.require_role("admin"))):
    projects = db.query(project.Project).all()
    return {
        "projects": [
            {
                "id": project.id,
                "title": project.title,
                "description": project.description,
                "location": project.location
            }
            for project in projects
        ]
    }

@router.post("/projects")
def create_project(project_data: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: dict = Depends(auth.require_role("admin"))):
    if db.query(project.Project).filter(project.Project.title == project_data.title).first():
        raise HTTPException(status_code=400, detail="Project title already exists")
    
    new_project = project.Project(title=project_data.title, description=project_data.description, location=project_data.location)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {"message": "Project created successfully", "project_id": new_project.id}

@router.put("/projects/{project_id}")
def update_project(project_id: int, project_data: schemas.ProjectUpdate, db: Session = Depends(get_db), current_user: dict = Depends(auth.require_role("admin"))):
    project_to_update = db.query(project.Project).filter(project.Project.id == project_id).first()
    if not project_to_update:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project_data.title != "" and project_data.title != project_to_update.title:
        if db.query(project.Project).filter(project.Project.title == project_data.title).first():
            raise HTTPException(status_code=400, detail="Project title already exists")
        setattr(project_to_update, "title", project_data.title)
    
    if project_data.description != "" and project_data.description != project_to_update.description:
        setattr(project_to_update, "description", project_data.description)
    
    if project_data.location != "" and project_data.location != project_to_update.location:
        setattr(project_to_update, "location", project_data.location)
        
    db.commit()
    db.refresh(project_to_update)
    return {"message": "Project updated successfully"}

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: dict = Depends(auth.require_role("admin"))):
    project_to_delete = db.query(project.Project).filter(project.Project.id == project_id).first()
    if not project_to_delete:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project_to_delete)
    db.commit()
    return {"message": "Project deleted successfully"}