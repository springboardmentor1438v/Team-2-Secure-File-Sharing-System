from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine, Base

from app.models.user import User
from app.models.file import File
from app.models.folder import Folder
from app.models.share import Share

from app.routes.user_routes import router
from app.routes.file_routes import router as file_router
from app.routes.folder_routes import router as folder_router
from app.routes.share_routes import router as share_router
from app.models.activity_log import ActivityLog
from app.routes.activity_routes import router as activity_router
from app.routes.dashboard_routes import router as dashboard_router
from app.routes import password_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(file_router)
app.include_router(folder_router)
app.include_router(share_router)
app.include_router(activity_router)
app.include_router(dashboard_router)
app.include_router(password_routes.router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {
        "message": "Welcome to Secure File Sharing System"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

