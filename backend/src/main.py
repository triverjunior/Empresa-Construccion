from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth
from .api.admin import workers, projects, reports
from .api.worker import reports as worker_reports, projects as worker_projects  
from .db.models import user, project, report
import os

app = FastAPI()

frontend_urls_env = os.getenv("FRONTEND_URLS", "")
frontend_urls = [url.strip() for url in frontend_urls_env.split(",") if url.strip()]

allow_origins = frontend_urls if frontend_urls else ["*"]
allow_credentials = bool(frontend_urls)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workers.router)
app.include_router(projects.router)
app.include_router(reports.router)
app.include_router(worker_reports.router)
app.include_router(worker_projects.router)
