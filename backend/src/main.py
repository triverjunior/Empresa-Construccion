from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_
from .api import auth
from .api.admin import workers, projects, reports
from .api.worker import reports as worker_reports, projects as worker_projects  
from .db.models import user, project, report
from .db.database import Base, engine, SessionLocal
from .db.models.user import User
from .auth.utils import hash_password
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


def init_database_and_admin() -> None:
    # Ensure required tables exist in the configured database.
    Base.metadata.create_all(bind=engine)

    admin_username = os.getenv("ADMIN_USERNAME")
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_username or not admin_email or not admin_password:
        return

    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(
            or_(User.username == admin_username, User.email == admin_email)
        ).first()

        if existing_admin:
            return

        db.add(
            User(
                username=admin_username,
                email=admin_email,
                hashed_password=hash_password(admin_password),
                role="admin",
            )
        )
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def startup_init() -> None:
    init_database_and_admin()

app.include_router(auth.router)
app.include_router(workers.router)
app.include_router(projects.router)
app.include_router(reports.router)
app.include_router(worker_reports.router)
app.include_router(worker_projects.router)
