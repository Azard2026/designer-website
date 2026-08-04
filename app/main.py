from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from app.routers import auth, leads, followups, projects, blogs, ai_assistant, analytics, settings
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Luxe Interior Design Business Engine",
    description="Enterprise-grade back-end core supporting CRM, Client Portals, AI features, and blog engines.",
    version="1.0.0"
)

# Set CORS permissions for local Next.js node server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust in production configuration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup DB initialisation
@app.on_event("startup")
def on_startup():
    init_db()

# Mount uploads directory to serve static images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
