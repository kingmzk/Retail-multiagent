"""ChromaDB Policy Retrieval Service."""
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import get_logger
from app.rag.ingestion import get_chroma_client
from app.rag.embeddings import get_embedding_function

logger = get_logger("rag.retrieval")


class PolicyRetriever:
    """Retriever for querying policy documentation stored in ChromaDB."""

    def __init__(self, collection_name: Optional[str] = None):
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.client = get_chroma_client()
        self.embedding_fn = get_embedding_function()

    def _get_collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Queries ChromaDB for policy chunks relevant to the customer's question."""
        logger.info(
            f"Querying ChromaDB for: '{query}'",
            extra={"event": "rag_search", "extra_data": {"query": query, "top_k": top_k}}
        )
        try:
            collection = self._get_collection()
            results = collection.query(
                query_texts=[query],
                n_results=min(top_k, max(1, collection.count()))
            )

            retrieved_chunks = []
            if results and results.get("documents") and results["documents"][0]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
                dists = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

                for doc, meta, dist in zip(docs, metas, dists):
                    retrieved_chunks.append({
                        "content": doc,
                        "metadata": meta,
                        "distance": dist,
                        "document": meta.get("document_name", "policy.md"),
                        "section": meta.get("section", "General")
                    })

            return retrieved_chunks
        except Exception as e:
            logger.error(f"Error during RAG retrieval: {e}", extra={"event": "error"})
            return []


def get_policy_retriever() -> PolicyRetriever:
    """Returns a singleton PolicyRetriever instance."""
    return PolicyRetriever()
