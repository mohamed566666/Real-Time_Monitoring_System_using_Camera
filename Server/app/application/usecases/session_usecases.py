from datetime import datetime
from typing import List
from uuid import uuid4
from fastapi import HTTPException, status

from app.domain.entities.entities import SessionEntity, SessionEndReason
from app.infrastructure.repositories.implementations.session_repository import (
    SessionRepository,
)
from app.infrastructure.repositories.implementations.employee_repository import (
    EmployeeRepository,
)
from app.infrastructure.repositories.implementations.face_embedding_repository import (
    FaceEmbeddingRepository,
)
from app.infrastructure.aiModels.face_engine import FaceEngine


class SessionUseCases:

    def __init__(
        self,
        session_repo: SessionRepository,
        employee_repo: EmployeeRepository,
        embedding_repo: FaceEmbeddingRepository,
        face_engine: FaceEngine,
    ):
        self.session_repo = session_repo
        self.employee_repo = employee_repo
        self.embedding_repo = embedding_repo
        self.face_engine = face_engine

    async def _set_online(self, employee_id: int, value: bool) -> None:
        emp = await self.employee_repo.get_by_id(employee_id)
        if emp:
            emp.is_online = value
            await self.employee_repo.update(emp)

    async def login_with_embedding(
        self,
        username: str,
        embedding: list[float],
    ) -> SessionEntity:
        emp = await self.employee_repo.get_by_username(username)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")

        stored = await self.embedding_repo.get_by_employee_id(emp.id)
        if not stored:
            raise HTTPException(
                status_code=404, detail="No embedding registered for this employee"
            )

        match, similarity = self.face_engine.verify_face(
            None, stored.embedding, embedding_override=embedding
        )
        if not match:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Face not recognised (similarity={similarity:.4f})",
            )

        return await self.open_session(emp.id)

    async def login_with_image(
        self,
        username: str,
        image_bytes: bytes,
    ) -> SessionEntity:
        import cv2
        import numpy as np

        emp = await self.employee_repo.get_by_username(username)
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")

        stored = await self.embedding_repo.get_by_employee_id(emp.id)
        if not stored:
            raise HTTPException(
                status_code=404, detail="No embedding registered for this employee"
            )

        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=422, detail="Could not decode image")

        face = self.face_engine.detect_face(image)
        if face is None:
            raise HTTPException(status_code=422, detail="No face detected in image")

        match, similarity = self.face_engine.verify_face(face, stored.embedding)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Face not recognised (similarity={similarity:.4f})",
            )

        return await self.open_session(emp.id)

    async def open_session(self, employee_id: int) -> SessionEntity:
        existing = await self.session_repo.get_active_by_employee(employee_id)
        if existing:
            raise HTTPException(
                status_code=409, detail="Employee already has an active session"
            )
        session = await self.session_repo.create(
            SessionEntity(id=uuid4(), employee_id=employee_id)
        )
        await self._set_online(employee_id, True)
        return session

    async def close_session(
        self,
        session_id,
        end_reason: SessionEndReason = SessionEndReason.LOGOUT,
    ) -> SessionEntity:
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.logout_time:
            raise HTTPException(status_code=409, detail="Session already closed")
        session.logout_time = datetime.utcnow()
        session.end_reason = end_reason
        result = await self.session_repo.update(session)
        await self._set_online(session.employee_id, False)
        return result

    async def get_session(self, session_id) -> SessionEntity:
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session

    async def list_sessions_by_employee(self, employee_id: int) -> List[SessionEntity]:
        return await self.session_repo.get_by_employee(employee_id)

    async def list_all_sessions(self) -> List[SessionEntity]:
        return await self.session_repo.get_all()

    async def list_sessions_by_department(
        self, department_id: int
    ) -> List[SessionEntity]:
        return await self.session_repo.get_by_department(department_id)

    async def get_active_session(self, employee_id: int) -> SessionEntity:
        session = await self.session_repo.get_active_by_employee(employee_id)
        if not session:
            raise HTTPException(
                status_code=404, detail="No active session for this employee"
            )
        return session
