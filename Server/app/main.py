# server/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Face Recognition API",
    description="Real-Time Monitoring System with Face Recognition",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.presentation.controllers import (
    auth_controller,
    user_controller,
    department_controller,
    device_controller,
)

app.include_router(auth_controller.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_controller.router, prefix="/api/users", tags=["Users"])
app.include_router(
    department_controller.router, prefix="/api/departments", tags=["Departments"]
)
app.include_router(device_controller.router, prefix="/api/devices", tags=["Devices"])


@app.get("/")
async def root():
    return {
        "message": "Face Recognition API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }
