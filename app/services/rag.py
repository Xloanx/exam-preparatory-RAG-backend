from app.services.embedder import Embedder


class RAGService:
    def __init__(self, embedder: Embedder):
        self.embedder = embedder

    async def retrieve(self, query: str, top_k: int = 5):
        # Retrieval placeholder — embeddings + vector search land in later phases.
        return []
