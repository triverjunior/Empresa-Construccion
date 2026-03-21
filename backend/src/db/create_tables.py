from .database import Base, engine
from .models.project import Project
from .models.user import User
from .models.report import Report

Base.metadata.create_all(bind=engine)