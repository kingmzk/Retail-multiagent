"""Ingestion CLI Script.

Loads retail policy documents from /documents and indexes them into ChromaDB.
Usage: python scripts/ingest_documents.py
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag.ingestion import ingest_documents


def main():
    print("Starting document ingestion into ChromaDB...")
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "documents"))
    total_chunks = ingest_documents(documents_dir=docs_dir)
    print(f"Ingestion complete! Total {total_chunks} policy chunks indexed in ChromaDB.")


if __name__ == "__main__":
    main()
