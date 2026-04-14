from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import logging
from ...db.models import schemas, report, project
from ...db.database import get_db
from .. import auth
from ...emails.sender import send_email
import os

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/api/reports")
def create_report(
    report_data: schemas.ReportCreate, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(auth.require_role("worker"))
):
    project_exists = db.query(project.Project).filter(project.Project.id == report_data.project_id).first()
    if not project_exists:
        raise HTTPException(status_code=404, detail="Project not found")

    admin_email = os.getenv('ADMIN_EMAIL', '')
    if not admin_email:
        raise HTTPException(status_code=500, detail="Admin email not configured")
    
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

    email_status = send_email(
        to_email=admin_email,
        subject=f"New Report: {report_data.title}",
        body=f"A new report has been created for project '{project_exists.title}'.\nDescription: {report_data.description}"
    )

    if email_status != 'success':
        logger.warning("Report created but email notification failed: %s", email_status)

    return {
        "message": "Report created successfully",
        "report_id": new_report.id,
        "email_status": email_status or "not_sent"
    }