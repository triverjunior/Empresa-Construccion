from ..database import Base
from sqlalchemy import Column, Integer, String

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)