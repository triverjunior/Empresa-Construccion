from fastapi import FastAPI
from .api import auth
from .api.admin import workers
from .db.models import user, project, report

app = FastAPI()
app.include_router(auth.router)
app.include_router(workers.router)