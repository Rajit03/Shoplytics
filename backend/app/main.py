"""
Shoplytics: Main FastAPI Application
Entrypoint for the REST API backend serving analytical and operational data.
"""

from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import check_db_connection
from .schemas import MessageResponse, HealthResponse
from .routers import (
    dashboard,
    customers,
    products,
    orders,
    segments,
    recommendations,
    association_rules,
    sales
)

# Initialize FastAPI App
app = FastAPI(
    title="Shoplytics API",
    description="A Distributed Big Data Analytics Platform for E-Commerce REST API Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for React / Vite frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler to protect sensitive internal details
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log exception internally, but return clean message to clients
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )


# Register all API Routers
app.include_router(dashboard.router)
app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(segments.router)
app.include_router(recommendations.router)
app.include_router(association_rules.router)
app.include_router(sales.router)


@app.get(
    "/",
    response_model=MessageResponse,
    summary="Root Status",
    tags=["System"]
)
def root():
    """Root endpoint confirming API status."""
    return {
        "message": "Shoplytics API is running",
        "version": "1.0.0"
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    tags=["System"]
)
def health_check():
    """Verify live PostgreSQL database connectivity."""
    is_connected = check_db_connection()
    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is unavailable."
        )
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow()
    }
