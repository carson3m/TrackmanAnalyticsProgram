from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.api import routes_auth, routes_csv, routes_metrics
from app.models.database import engine, Base
from fastapi import Request

app = FastAPI(
    title="Trackman Analytics API",
    description="Backend for Trackman-based analytics platform.",
    version="1.0.0"
)

# CORS settings (allow frontend dev server to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for AWS health checks
@app.get("/")
async def root():
    return {"status": "healthy", "message": "Trackman Analytics API is running"}

# Health check endpoint for AWS
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Trackman Analytics API is running"}

# Register API routers
app.include_router(routes_auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(routes_csv.router, prefix="/api/csv", tags=["csv"])
app.include_router(routes_metrics.router, prefix="/api/metrics", tags=["metrics"])

# Fix recursion: use get_openapi instead of app.openapi()
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Trackman Analytics API",
        version="1.0.0",
        description="Backend for Trackman-based analytics platform.",
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
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables initialized")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str, request: Request):
    return {}