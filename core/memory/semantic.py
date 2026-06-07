"""ChromaDB semantic memory index."""

from typing import Any

import chromadb

from core.ai.router import AIRouter
from core.config import config


class SemanticMemory:
    """Stores and searches vector embeddings for memories."""

    def __init__(self, ai_router: AIRouter) -> None:
        """Create Chroma collection."""
        self.ai_router = ai_router
        self.client = chromadb.PersistentClient(path=str(config.chroma_path))
        self.collection = self.client.get_or_create_collection("sanaya_memories")

    async def store(self, memory_id: str, content: str, metadata: dict[str, Any]) -> None:
        """Embed and store a memory in Chroma."""
        provider = self.ai_router.select_provider("embedding", True, {"content": content})
        embedding = await provider.embed(content)
        self.collection.upsert(ids=[memory_id], documents=[content], metadatas=[metadata], embeddings=[embedding])

    async def search(self, query: str, n_results: int = 5) -> list[dict[str, Any]]:
        """Search semantic memory."""
        provider = self.ai_router.select_provider("embedding", True, {"content": query})
        embedding = await provider.embed(query)
        result = self.collection.query(query_embeddings=[embedding], n_results=n_results)
        return [{"id": item, "document": doc} for item, doc in zip(result["ids"][0], result["documents"][0], strict=False)]

    async def delete(self, memory_id: str) -> None:
        """Delete semantic memory."""
        self.collection.delete(ids=[memory_id])
