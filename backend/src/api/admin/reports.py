from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.models import schemas, report, project
from ...db.database import get_db
from .. import auth

router = APIRouter()

@router.get("/reports")
def get_reports(db: Session = Depends(get_db), current_user: dict = Depends(auth.require_role("admin"))):
    reports = db.query(report.Report).all()
    return {
        "reports": [
            {
                "id": rep.id,
                "user_id": rep.user_id,
                "project_id": rep.project_id,
                "title": rep.title,
                "description": rep.description,
                "type": rep.type
            }
            for rep in reports
        ]
    }