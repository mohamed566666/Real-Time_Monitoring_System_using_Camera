# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Face Recognition API",
    description="Real-Time Monitoring System with Face Recognition",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.presentation.controllers import (
    auth_controller,
    user_controller,
    department_controller,
    device_controller,
    session_controller,
)

# Include routers
API_PREFIX = "/api"
app.include_router(auth_controller.router, prefix=API_PREFIX)
app.include_router(user_controller.router, prefix=API_PREFIX)
app.include_router(department_controller.router, prefix=API_PREFIX)
app.include_router(device_controller.router, prefix=API_PREFIX)
app.include_router(session_controller.router, prefix=API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Face Recognition API",
        "version": "1.0.0",
        "status": "operational",
        "note": "WebSocket available at separate service",
        "websocket_service": "wss://your-websocket-service.onrender.com",
        "endpoints": {
            "rest_api": "/api",
            "documentation": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# هذا السطر مهم جداً لـ Vercel
# Vercel يحتاج هذا المتغير
handler = app
