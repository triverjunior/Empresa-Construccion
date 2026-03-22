from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.models import schemas, report, project
from ...db.database import get_db
from .. import auth

router = APIRouter()

@router.post("/reports")
def create_report(
    report_data: schemas.ReportCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(auth.require_role("worker"))
):
    project_exists = db.query(project.Project).filter(project.Project.id == report_data.project_id).first()
    if not project_exists:
        raise HTTPException(status_code=404, detail="Project not found")

    new_report = report.Report(
        user_id=current_user["id"],
        project_id=report_data.project_id,
        title=report_data.title,
        description=report_data.description,
        type=report_data.type
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return {"message": "Report created successfully", "report_id": new_report.id}