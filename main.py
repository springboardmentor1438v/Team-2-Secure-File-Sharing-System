import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import text

from app.database.database import engine
from app.routes.user_routes import router as user_router
from app.routes.file_routes import router as file_router
from app.routes.admin_routes import router as admin_router
from app.routes.dashboard_routes import router as dashboard_router

app = FastAPI(
    title="CipherVault - Zero-Trust Ephemeral Document Exchange",
    description="Next-generation zero-trust document security platform featuring authenticated AES-256 encryption at rest, ephemeral 12-hour delegated access, role-based access governance, and real-time security audit trails.",
    version="1.0.0",
    debug=True
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(user_router)
app.include_router(file_router)
app.include_router(admin_router)
app.include_router(dashboard_router)

# Mount Static Assets Directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def serve_frontend():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "CipherVault API is running. Access /docs for interactive Swagger UI."}


@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }