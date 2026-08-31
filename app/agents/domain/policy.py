"""Policy Specialist Agent Domain Logic.

Queries ChromaDB vector knowledge base for policy documentation and produces grounded responses.
"""
from typing import Optional, List, Dict, Any
from app.agents.schemas import SpecialistResult, IntentType
from app.rag.retrieval import PolicyRetriever, get_policy_retriever
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("agents.policy")

POLICY_GROUNDING_PROMPT = """You are the official Policy Specialist Agent for a retail customer support team.
Your task is to answer the customer's question using ONLY the retrieved policy context provided below.

CRITICAL RULES:
1. Base your answer strictly on the provided Context. Do NOT invent, assume, or extrapolate rules.
2. If the policy documentation does not contain enough information to answer the question, explicitly state:
   "The available policy documentation does not provide enough information to answer this confidently."
3. If the question is about footwear fit or returns, explicitly mention key return conditions (e.g. 30-day window, unworn condition, original packaging/tags, sizing exchange option) if present in the context.
4. Keep the answer concise, professional, and clear.

Context:
{context}

Customer Question:
{question}
"""


class PolicyAgent:
    """Specialist agent for RAG policy retrieval and grounded answering."""

    def __init__(self, retriever: Optional[PolicyRetriever] = None, api_key: str = ""):
        self.retriever = retriever or get_policy_retriever()
        self.api_key = api_key or settings.GEMINI_API_KEY

    async def execute(self, query: str) -> SpecialistResult:
        """Retrieves policy chunks from ChromaDB and generates a grounded response."""
        logger.info(
            f"PolicyAgent started for query: '{query}'",
            extra={"event": "agent_started", "agent": "PolicyAgent"}
        )

        chunks = self.retriever.retrieve(query=query, top_k=3)
        sources = []
        for c in chunks:
            sources.append({
                "document": c.get("document", "policy.md"),
                "section": c.get("section", "General")
            })

        if not chunks:
            return SpecialistResult(
                agent_name="PolicyAgent",
                intent=IntentType.RETURN_POLICY,
                success=False,
                summary="The available policy documentation does not provide enough information to answer this confidently.",
                sources=[]
            )

        context_text = "\n\n---\n\n".join([f"Source: {c['document']} ({c['section']})\n{c['content']}" for c in chunks])

        if not self.api_key:
            # Fallback deterministic summary from top retrieved chunk
            top_chunk = chunks[0]["content"].strip()
            # Clean markdown header hash prefixes
            clean_chunk = "\n".join([line.lstrip("#").strip() for line in top_chunk.split("\n") if line.strip()])
            return SpecialistResult(
                agent_name="PolicyAgent",
                intent=IntentType.RETURN_POLICY,
                success=True,
                summary=f"Store Policy Information:\n{clean_chunk}",
                sources=sources,
                raw_data={"chunks": chunks}
            )

        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            prompt = POLICY_GROUNDING_PROMPT.format(context=context_text, question=query)

            response = client.models.generate_content(
                model=settings.DEFAULT_GEMINI_MODEL,
                contents=prompt
            )

            grounded_answer = response.text.strip()
            return SpecialistResult(
                agent_name="PolicyAgent",
                intent=IntentType.RETURN_POLICY,
                success=True,
                summary=grounded_answer,
                sources=sources,
                raw_data={"chunks": chunks}
            )

        except Exception as e:
            logger.error(f"PolicyAgent LLM generation failed: {e}", extra={"event": "error"})
            top_chunk = chunks[0]["content"]
            return SpecialistResult(
                agent_name="PolicyAgent",
                intent=IntentType.RETURN_POLICY,
                success=True,
                summary=f"According to the retrieved policy documentation: {top_chunk}",
                sources=sources,
                raw_data={"chunks": chunks}
            )
