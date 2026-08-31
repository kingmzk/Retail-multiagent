"""Response Synthesizer Agent Domain Logic.

Fuses the results of multiple specialist agents into a clean, unified, customer-facing response.
"""
from typing import List, Dict, Any, Optional
from app.agents.schemas import SpecialistResult, FinalSupportResponse, IntentType
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("agents.response")

RESPONSE_SYNTHESIS_PROMPT = """You are the friendly, helpful, and professional Customer Support Response Agent for an omnichannel retail store.
Your job is to synthesize the verified outputs of our specialist agents into a single, cohesive, polite customer response.

Rules:
1. Address all aspects of the customer's query directly and empathetically.
2. Integrate the factual details provided by the specialist agents (e.g. order status, tracking number, ETA, return windows, conditions).
3. Do NOT reveal internal agent architecture, tool names, JSON structures, or chain-of-thought reasoning.
4. Keep the response natural, clear, and well-structured.

Customer Message:
{customer_query}

Specialist Findings:
{specialist_findings}
"""


class ResponseAgent:
    """Agent responsible for assembling and synthesizing specialist outputs."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or settings.GEMINI_API_KEY

    def _fallback_synthesis(self, customer_query: str, specialist_results: List[SpecialistResult]) -> str:
        """Deterministic synthesis if LLM is unavailable."""
        if not specialist_results:
            return "Thank you for reaching out! How can I assist you with your retail orders, products, or store policies today?"

        paragraphs = []
        for res in specialist_results:
            if res.summary:
                paragraphs.append(res.summary)

        return "\n\n".join(paragraphs)

    async def synthesize(
        self,
        customer_query: str,
        specialist_results: List[SpecialistResult],
        intents: Optional[List[str]] = None
    ) -> FinalSupportResponse:
        """Combines specialist results into a customer-ready answer with source citations."""
        logger.info(
            "ResponseAgent synthesizing final response",
            extra={"event": "agent_started", "agent": "ResponseAgent"}
        )

        all_sources: List[Dict[str, Any]] = []
        for res in specialist_results:
            for s in res.sources:
                if s not in all_sources:
                    all_sources.append(s)

        detected_intents = intents or [res.intent.value for res in specialist_results]
        is_escalated = any(res.intent == IntentType.HUMAN_ESCALATION for res in specialist_results)

        if not self.api_key:
            answer = self._fallback_synthesis(customer_query, specialist_results)
            logger.info("Generated fallback response (no LLM key)", extra={"event": "response_generated"})
            return FinalSupportResponse(
                answer=answer,
                intents=detected_intents,
                sources=all_sources,
                escalated_to_human=is_escalated
            )

        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)

            findings_text = "\n\n".join(
                [f"[{res.agent_name} ({res.intent.value})]:\n{res.summary}" for res in specialist_results]
            )

            prompt = RESPONSE_SYNTHESIS_PROMPT.format(
                customer_query=customer_query,
                specialist_findings=findings_text
            )

            response = client.models.generate_content(
                model=settings.DEFAULT_GEMINI_MODEL,
                contents=prompt
            )

            final_text = response.text.strip()
            logger.info("Successfully synthesized final response via Gemini", extra={"event": "response_generated"})
            return FinalSupportResponse(
                answer=final_text,
                intents=detected_intents,
                sources=all_sources,
                escalated_to_human=is_escalated
            )

        except Exception as e:
            logger.error(f"ResponseAgent LLM synthesis failed: {e}", extra={"event": "error"})
            answer = self._fallback_synthesis(customer_query, specialist_results)
            return FinalSupportResponse(
                answer=answer,
                intents=detected_intents,
                sources=all_sources,
                escalated_to_human=is_escalated
            )
