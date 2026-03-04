# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.presentation.controllers.user_controller import router as user_router
from app.presentation.controllers.department_controller import (
    router as department_router,
)
from app.presentation.controllers.device_controller import router as device_router
from app.presentation.controllers.auth_controller import router as auth_router

app = FastAPI(title="Face Recognition API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)
app.include_router(department_router)
app.include_router(device_router)
app.include_router(auth_router)


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
