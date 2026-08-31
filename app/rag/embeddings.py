"""Embedding function for ChromaDB and RAG."""
from typing import List, Optional
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("rag.embeddings")


class PolicyEmbeddingFunction(EmbeddingFunction):
    """Embedding function utilizing Google GenAI or ChromaDB default embedding model."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._fallback_fn = None

    def _get_fallback_fn(self):
        if self._fallback_fn is None:
            # Use chromadb's default ONNX-based MiniLM embeddings
            from chromadb.utils import embedding_functions
            self._fallback_fn = embedding_functions.DefaultEmbeddingFunction()
        return self._fallback_fn

    def __call__(self, input: Documents) -> Embeddings:
        # If GEMINI_API_KEY is configured and valid, use google.genai embeddings
        if self.api_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                response = client.models.embed_content(
                    model="text-embedding-004",
                    contents=input
                )
                if hasattr(response, "embeddings") and response.embeddings:
                    return [e.values for e in response.embeddings]
            except Exception as e:
                logger.warning(
                    f"Google GenAI embedding failed, falling back to local embeddings: {e}",
                    extra={"event": "error"}
                )

        # Local deterministic ONNX embedding fallback
        fallback = self._get_fallback_fn()
        return fallback(input)


def get_embedding_function() -> EmbeddingFunction:
    """Returns the configured embedding function."""
    return PolicyEmbeddingFunction()
