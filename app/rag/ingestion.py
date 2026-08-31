"""Document Ingestion and Vector Store Indexer."""
import os
import re
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from app.core.config import settings
from app.core.logging import get_logger
from app.rag.embeddings import get_embedding_function

logger = get_logger("rag.ingestion")


def get_chroma_client():
    """Returns a persistent ChromaDB client."""
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)


def chunk_markdown_file(file_path: Path) -> List[Dict[str, Any]]:
    """Chunks markdown by header sections preserving context and metadata."""
    content = file_path.read_text(encoding="utf-8")
    doc_name = file_path.name
    doc_type = file_path.stem.replace("_", " ").title()

    # Split by markdown headers (# or ## or ###)
    sections = re.split(r'\n(?=#{1,3}\s)', content)
    chunks = []

    for i, sec in enumerate(sections):
        clean_sec = sec.strip()
        if not clean_sec:
            continue

        # Extract title if present
        header_match = re.match(r'^#{1,3}\s+(.+)$', clean_sec, re.MULTILINE)
        section_title = header_match.group(1) if header_match else f"Section {i+1}"

        chunk_id = f"{file_path.stem}_sec_{i+1}"
        chunks.append({
            "id": chunk_id,
            "text": clean_sec,
            "metadata": {
                "document_name": doc_name,
                "document_type": doc_type,
                "section": section_title,
                "source": str(file_path.name)
            }
        })

    return chunks


def ingest_documents(documents_dir: str = "./documents") -> int:
    """Ingests all markdown documents from directory into ChromaDB collection."""
    doc_path = Path(documents_dir)
    if not doc_path.exists():
        raise FileNotFoundError(f"Documents directory '{documents_dir}' not found.")

    client = get_chroma_client()
    embedding_fn = get_embedding_function()

    # Reset or get collection
    collection = client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"description": "Retail customer support policy knowledge base"}
    )

    all_chunks: List[Dict[str, Any]] = []
    md_files = list(doc_path.glob("*.md"))

    if not md_files:
        logger.warning(f"No markdown documents found in {documents_dir}", extra={"event": "error"})
        return 0

    for md_file in md_files:
        chunks = chunk_markdown_file(md_file)
        all_chunks.extend(chunks)

    if all_chunks:
        # Upsert chunks into ChromaDB
        ids = [c["id"] for c in all_chunks]
        documents = [c["text"] for c in all_chunks]
        metadatas = [c["metadata"] for c in all_chunks]

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(
            f"Successfully ingested {len(all_chunks)} chunks from {len(md_files)} files into ChromaDB.",
            extra={"event": "rag_search", "extra_data": {"count": len(all_chunks)}}
        )

    return len(all_chunks)
