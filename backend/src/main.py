from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth
from .api.admin import workers, projects, reports
from .api.worker import reports as worker_reports, projects as worker_projects  
from .db.models import user, project, report

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workers.router)
app.include_router(projects.router)
app.include_router(reports.router)
app.include_router(worker_reports.router)
app.include_router(worker_projects.router)
