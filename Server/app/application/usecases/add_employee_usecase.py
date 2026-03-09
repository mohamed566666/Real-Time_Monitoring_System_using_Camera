from app.application.services.user_service import UserService
from app.application.services.face_embedding_service import FaceEmbeddingService
from app.application.services.face_ai_service import FaceAIService


class AddEmployeeUseCase:

    def __init__(
        self,
        user_service: UserService,
        embedding_service: FaceEmbeddingService,
        ai_service: FaceAIService,
    ):
        self.user_service = user_service
        self.embedding_service = embedding_service
        self.ai_service = ai_service

    async def execute(
        self, name: str, role: str, department_id: int, image_bytes: bytes
    ):

        embedding = await self.ai_service.extract_embedding_from_bytes(image_bytes)

        user = await self.user_service.create_user(
            name=name,
            role=role,
            department_id=department_id,
        )

        await self.embedding_service.create_embedding(
            user_id=user.id,
            embedding=embedding,
        )

        return user
