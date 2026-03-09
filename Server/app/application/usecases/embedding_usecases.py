from app.application.services.face_embedding_service import FaceEmbeddingService


class CreateEmbeddingUseCase:
    def __init__(self, service: FaceEmbeddingService):
        self.service = service

    async def execute(self, user_id: int, embedding: list):
        if not embedding:
            raise ValueError("Embedding cannot be empty")

        return await self.service.create_embedding(user_id, embedding)


class DeleteEmbeddingUseCase:
    def __init__(self, service: FaceEmbeddingService):
        self.service = service

    async def execute(self, embedding_id: int):
        return await self.service.delete_embedding(embedding_id)


class GetUserEmbeddingsUseCase:
    def __init__(self, service: FaceEmbeddingService):
        self.service = service

    async def execute(self, user_id: int):
        return await self.service.get_embeddings_by_user(user_id)


class ListAllEmbeddingsUseCase:
    def __init__(self, service: FaceEmbeddingService):
        self.service = service

    async def execute(self):
        return await self.service.list_all_embeddings()


class ListEmbeddingsByUserIdsUseCase:
    def __init__(self, service: FaceEmbeddingService):
        self.service = service

    async def execute(self, user_ids: list):
        if not user_ids:
            raise ValueError("User IDs list cannot be empty")

        return await self.service.list_embeddings_by_user_ids(user_ids)


class UpdateEmbeddingUseCase:
    def __init__(self, service: FaceEmbeddingService):
        self.service = service

    async def execute(self, embedding_id: int, new_embedding: list):
        if not new_embedding:
            raise ValueError("New embedding cannot be empty")

        return await self.service.update_embedding(embedding_id, new_embedding)
