"""Domain data schemas and enums for agents."""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    ORDER_STATUS = "ORDER_STATUS"
    PRODUCT_INFORMATION = "PRODUCT_INFORMATION"
    RETURN_POLICY = "RETURN_POLICY"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"
    GENERAL_QUERY = "GENERAL_QUERY"


class ExtractedEntities(BaseModel):
    order_id: Optional[str] = None
    product_name: Optional[str] = None
    sku: Optional[str] = None
    policy_topic: Optional[str] = None


class RouterDecision(BaseModel):
    intents: List[IntentType] = Field(default_factory=list)
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    reasoning: Optional[str] = None


class SpecialistResult(BaseModel):
    agent_name: str
    intent: IntentType
    success: bool
    summary: str
    raw_data: Optional[Dict[str, Any]] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)


class FinalSupportResponse(BaseModel):
    answer: str
    intents: List[str] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    escalated_to_human: bool = False
