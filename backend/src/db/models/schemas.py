from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = 'worker'
    disponibility: bool = True
    assigned_project_id: int = None

class UserLogin(BaseModel):
    username: str
    password: str

class WorkerUpdate(BaseModel):
    username: str
    email: EmailStr

class WorkerDisponibilityUpdate(BaseModel):
    disponibility: bool
    assigned_project_id: int

class ProjectCreate(BaseModel):
    title: str
    description: str
    location: str

class ProjectUpdate(BaseModel):
    title: str
    description: str
    location: str

class ReportCreate(BaseModel):
    user_id: int
    project_id: int
    type: str
    title: str
    description: str