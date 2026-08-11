import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from app.routers import auth, leads, followups, projects, blogs, ai_assistant, analytics, settings
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Luxe Interior Design Business Engine",
    description="Enterprise-grade back-end core supporting CRM, Client Portals, AI features, and blog engines.",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# The production site and API share one domain through the reverse proxy.
cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://43.204.238.189").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup DB initialisation
@app.on_event("startup")
def on_startup():
    init_db()

# Mount persistent uploads to serve site and portfolio images.
upload_dir = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Register Routers
app.include_router(auth.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(followups.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(blogs.router, prefix="/api")
app.include_router(ai_assistant.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(settings.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Luxe Interior Design API Engine",
        "version": "1.0.0"
    }

@app.get("/api/health")
def health_check():
    return {"status": "online"}
