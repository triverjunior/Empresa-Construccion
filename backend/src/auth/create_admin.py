from ..db.database import SessionLocal
from ..db.models import user, project
from . import utils
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env')))

def create_admin():
    db: Session = SessionLocal()
    try:
        admin_password = os.getenv("ADMIN_PASSWORD")
        if not admin_password:
            raise ValueError("ADMIN_PASSWORD is not set")
        admin = user.User(
            username=os.getenv("ADMIN_USERNAME"),
            email=os.getenv("ADMIN_EMAIL"),
            hashed_password=utils.hash_password(admin_password),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()