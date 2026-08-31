"""Router Agent Domain Logic.

Classifies customer queries into single or multiple intents and extracts key entities.
"""
import re
import json
from typing import Dict, Any
from app.agents.schemas import RouterDecision, IntentType, ExtractedEntities
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("agents.router")

ROUTER_SYSTEM_PROMPT = """You are the central Router Agent for a Retail Customer Support AI assistant.
Your job is to analyze the customer's message, identify ALL intents present (supporting single or multi-intent), and extract key entities.

Supported Intents:
- ORDER_STATUS: Tracking an order, finding ETA, carrier status, order details, order line items.
- PRODUCT_INFORMATION: Product specs, price, sizing, description, inventory availability.
- RETURN_POLICY: Questions about returns, return window, refunds, footwear fit exchange conditions, warranty, shipping policies, FAQs.
- HUMAN_ESCALATION: Unsupported requests, billing fraud, complex disputes, explicit request to talk to a human.
- GENERAL_QUERY: General greetings or polite inquiries.

Extract Entities:
- order_id: e.g. "45231" or "#45231"
- product_name: e.g. "Running Shoes", "shoes", "jacket"
- sku: e.g. "SHOE-RN-001"
- policy_topic: e.g. "shoes return if not fitting", "warranty"

Respond ONLY with a JSON object adhering to this schema:
{
  "intents": ["ORDER_STATUS", "RETURN_POLICY"],
  "entities": {
    "order_id": "45231",
    "product_name": "shoes",
    "sku": null,
    "policy_topic": "return footwear fit"
  },
  "reasoning": "User asks where order #45231 is and whether they can return shoes if they do not fit."
}
"""


class RouterAgent:
    """Router Agent for intent identification and entity extraction."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or settings.GEMINI_API_KEY

    def _rule_based_fallback(self, query: str) -> RouterDecision:
        """Deterministic regex-based fallback if LLM is unavailable."""
        intents = []
        entities = ExtractedEntities()

        order_match = re.search(r'#?(\d{4,6})\b', query)
        has_order_keywords = any(w in query.lower() for w in ["order", "where is", "track", "eta", "status", "ship", "delivery"])
        if order_match or has_order_keywords:
            intents.append(IntentType.ORDER_STATUS)
            if order_match:
                entities.order_id = order_match.group(1)

        has_policy_keywords = any(w in query.lower() for w in ["return", "refund", "exchange", "warranty", "policy", "not fit", "fit", "broken", "guarantee", "defect", "coverage"])
        if has_policy_keywords:
            intents.append(IntentType.RETURN_POLICY)
            if "warranty" in query.lower() or "defect" in query.lower():
                entities.policy_topic = "warranty coverage for defective items"
            else:
                entities.policy_topic = "return and exchange policy"

        has_product_keywords = any(w in query.lower() for w in ["spec", "specs", "price", "stock", "inventory", "available", "material", "how much is", "in stock"])
        # Only trigger product info on generic 'product' keyword if not a policy query
        if not has_policy_keywords and any(w in query.lower() for w in ["product", "products", "item", "items", "catalog"]):
            has_product_keywords = True

        if has_product_keywords:
            intents.append(IntentType.PRODUCT_INFORMATION)

        if any(w in query.lower() for w in ["human", "agent", "supervisor", "representative", "escalate", "fraud", "lawyer"]):
            intents.append(IntentType.HUMAN_ESCALATION)

        if not intents:
            intents.append(IntentType.GENERAL_QUERY)

        # Detect product name if mentioned
        for p in ["shoe", "shoes", "boots", "jacket", "backpack", "watch"]:
            if p in query.lower():
                entities.product_name = p
                break

        return RouterDecision(
            intents=intents,
            entities=entities,
            reasoning="Rule-based heuristic parsing"
        )

    async def route(self, customer_query: str) -> RouterDecision:
        """Determines customer intents and extracts entities."""
        logger.info(
            f"Routing customer query: '{customer_query}'",
            extra={"event": "agent_started", "agent": "RouterAgent"}
        )

        if not self.api_key:
            logger.info("Using rule-based router (no GEMINI_API_KEY provided)")
            return self._rule_based_fallback(customer_query)

        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            prompt = f"Customer Message: \"{customer_query}\"\nAnalyze and return JSON:"

            response = client.models.generate_content(
                model=settings.DEFAULT_GEMINI_MODEL,
                contents=prompt,
                config={
                    "system_instruction": ROUTER_SYSTEM_PROMPT,
                    "response_mime_type": "application/json"
                }
            )

            text = response.text.strip()
            # Clean possible markdown block
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]

            data = json.loads(text.strip())
            intents = [IntentType(i) for i in data.get("intents", []) if i in IntentType.__members__]
            if not intents:
                intents = [IntentType.GENERAL_QUERY]

            ent_data = data.get("entities", {})
            entities = ExtractedEntities(
                order_id=ent_data.get("order_id"),
                product_name=ent_data.get("product_name"),
                sku=ent_data.get("sku"),
                policy_topic=ent_data.get("policy_topic")
            )

            decision = RouterDecision(
                intents=intents,
                entities=entities,
                reasoning=data.get("reasoning")
            )
            logger.info(
                f"Router identified intents: {[i.value for i in decision.intents]}",
                extra={"event": "intent_detected", "intents": [i.value for i in decision.intents]}
            )
            return decision

        except Exception as e:
            logger.warning(
                f"LLM routing failed, falling back to heuristic router: {e}",
                extra={"event": "error"}
            )
            return self._rule_based_fallback(customer_query)
