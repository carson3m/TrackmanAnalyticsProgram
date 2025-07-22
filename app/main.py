from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.api import routes_auth, routes_csv, routes_metrics, routes_admin, routes_debug
from app.api import routes_social
from app.models.database import engine, Base
from fastapi import Request

app = FastAPI(
    title="MoundVision Analytics API",
    description="Backend for MoundVision-based analytics platform.",
    version="1.0.0"
)

# CORS settings - allow only production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://moundvision.com",
        "https://www.moundvision.com",
        "https://api.moundvision.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for AWS health checks
@app.get("/")
async def root():
    return {"status": "healthy", "message": "MoundVision Analytics API is running"}

# Health check endpoint for AWS
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "MoundVision Analytics API is running"}

# Simple test endpoint
@app.get("/test")
async def test():
    return {"status": "success", "message": "Application is running without database"}

# Register API routers
app.include_router(routes_auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(routes_csv.router, prefix="/api/csv", tags=["csv"])
app.include_router(routes_metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(routes_admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(routes_debug.router, prefix="/api", tags=["debug"])
app.include_router(routes_social.router, prefix="/api/social", tags=["social"])

# Fix recursion: use get_openapi instead of app.openapi()
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="MoundVision Analytics API",
        version="1.0.0",
        description="Backend for MoundVision-based analytics platform.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Application starting up...")
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables initialized")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("⚠️  Application will continue without database initialization")
        # Don't raise the exception - let the app start anyway
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str, request: Request):
    return {}