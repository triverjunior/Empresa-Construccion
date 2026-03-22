from fastapi import FastAPI
from .api import auth
from .api.admin import workers, projects, reports
from .api.worker import reports as worker_reports, projects as worker_projects
from .db.models import user, project, report

app = FastAPI()
app.include_router(auth.router)
app.include_router(workers.router)
app.include_router(projects.router)
app.include_router(reports.router)
app.include_router(worker_reports.router)
app.include_router(worker_projects.router)
