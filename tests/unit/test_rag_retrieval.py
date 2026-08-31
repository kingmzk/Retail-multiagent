"""Unit tests for ChromaDB RAG Retrieval."""
from app.rag.retrieval import get_policy_retriever


def test_footwear_return_policy_retrieval():
    retriever = get_policy_retriever()
    results = retriever.retrieve("Can I return shoes if they don't fit?", top_k=3)
    assert len(results) > 0
    # Must retrieve footwear_return_policy.md or return_policy.md
    docs = [r["document"] for r in results]
    assert any("footwear_return_policy.md" in d or "return_policy.md" in d for d in docs)
    # Check source text contains 30-day window or unworn conditions
    all_text = " ".join([r["content"].lower() for r in results])
    assert "30" in all_text or "unworn" in all_text or "return" in all_text


def test_warranty_policy_retrieval():
    retriever = get_policy_retriever()
    results = retriever.retrieve("What is the warranty coverage for defective shoes?", top_k=2)
    assert len(results) > 0
    docs = [r["document"] for r in results]
    assert any("warranty_policy.md" in d for d in docs)


def test_retrieval_metadata_structure():
    retriever = get_policy_retriever()
    results = retriever.retrieve("How do I contact human support?", top_k=1)
    assert len(results) > 0
    item = results[0]
    assert "content" in item
    assert "document" in item
    assert "section" in item
    assert "metadata" in item
