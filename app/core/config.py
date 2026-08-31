from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Retail Customer Support Assistant"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # LLM Settings
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    DEFAULT_GEMINI_MODEL: str = "gemini-2.5-flash"

    # Agent Runtime Framework
    AGENT_FRAMEWORK: Literal["langgraph", "langchain", "adk"] = "langgraph"

    # PostgreSQL Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "retail_support"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "ROOT"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @computed_field
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # ChromaDB Settings
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    CHROMA_COLLECTION_NAME: str = "retail_policies"

    # MCP Microservices URLs (Stateless HTTP)
    ORDER_MCP_URL: str = "http://localhost:8101/mcp"
    PRODUCT_MCP_URL: str = "http://localhost:8102/mcp"

    # HTTP client timeouts (in seconds)
    MCP_REQUEST_TIMEOUT: float = 10.0


settings = Settings()
