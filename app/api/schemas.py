"""API Request and Response Pydantic Schemas."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        description="The customer's message or question.",
        examples=["Where is my order #45231? Can I return the shoes if they don't fit?"]
    )
    framework: Optional[str] = Field(
        default=None,
        description="Optional override for AGENT_FRAMEWORK ('langgraph', 'langchain', or 'adk')."
    )


class SourceMetadata(BaseModel):
    document: str
    section: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str = Field(..., description="The synthesized customer-facing support answer.")
    intents: List[str] = Field(default_factory=list, description="Detected customer intents.")
    sources: List[SourceMetadata] = Field(default_factory=list, description="Referenced policy documents.")
    escalated_to_human: bool = Field(default=False, description="Whether inquiry was escalated.")
    framework: str = Field(..., description="The agent framework runtime used.")


class HealthResponse(BaseModel):
    status: str
    app_name: str
    framework: str
    database: str
    chromadb: str
    mcp_servers: Dict[str, str]
