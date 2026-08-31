# Multi-Agent Customer Support Assistant for Retail

A standalone Proof of Concept (POC) demonstrating an enterprise multi-agent retail customer-support architecture built with **Gemini**, **PostgreSQL**, **ChromaDB**, **MCP (Model Context Protocol)**, **RAG**, **LangGraph**, **LangChain**, **Google ADK (Antigravity SDK)**, and **FastAPI**.

---

## 1. High-Level Architecture

```text
                         Customer
                            │
                            ▼
                     FastAPI API (/api/v1/chat)
                            │
                            ▼
               Selected Agent Runtime (AGENT_FRAMEWORK)
                  [LangGraph / LangChain / Google ADK]
                            │
                            ▼
                    Router / Orchestrator
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        Order Agent    Product Agent   Policy Agent
             │              │              │
             ▼              ▼              ▼
         MCP Client     MCP Client     ChromaDB RAG
             │              │              │
             ▼              ▼              ▼
      Order MCP Server Product MCP      ChromaDB
       (Port 8101)      (Port 8102)     (Vector Store)
             │              │              │
             ▼              ▼              │
        PostgreSQL     PostgreSQL          │
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    Response Agent (Synthesizer)
                            │
                            ▼
                         Customer
```

---

## 2. Core Architectural Principles

* **Gemini**: LLM reasoning and response grounding.
* **LangGraph / LangChain / Google ADK / Microsoft AutoGen**: Native multi-agent orchestrations selectable via `AGENT_FRAMEWORK` (`langgraph`, `langchain`, `adk`, `autogen`).
* **MCP (Model Context Protocol)**: Stateless JSON-RPC 2.0 microservices over HTTP (`Order MCP` on port 8101, `Product MCP` on port 8102).
* **RAG & ChromaDB**: Unstructured store policy knowledge with source citations (`footwear_return_policy.md`, `return_policy.md`, `shipping_policy.md`, `warranty_policy.md`, `faq.md`).
* **PostgreSQL**: Structured operational retail data (`customers`, `orders`, `order_items`, `products`).
* **FastAPI**: REST API layer (`GET /health`, `POST /api/v1/chat`).

---

## 3. Primary Demonstration Scenario

Customer asks a **multi-intent query**:
> *"Where is my order #45231? Can I return the shoes if they don't fit?"*

1. **Router Agent** analyzes the request and detects two distinct intents:
   - `ORDER_STATUS`
   - `RETURN_POLICY`
2. **Order Agent** calls the `get_order` tool on the Order MCP microservice, returning:
   - Order `#45231`: Status `SHIPPED`, ETA `2026-09-03`, Tracking `TRK123456`, Item `Running Shoes`.
3. **Policy Agent** retrieves relevant policy chunks from ChromaDB, finding the footwear 30-day unworn return condition and sizing exchange policy.
4. **Response Agent** synthesizes both factual findings into a single natural answer:

> *"Your order #45231 has shipped and is expected to arrive by September 3, 2026. The tracking number is TRK123456.*
>
> *According to our footwear return policy, the shoes can be returned or exchanged within 30 days of delivery as long as they are unworn, in original condition, and in their original packaging."*

---

## 4. Quickstart Guide (Local Development)

### 4.1 Prerequisites
- Python 3.11+
- PostgreSQL (running locally on port 5432)

### 4.2 Configuration
Create your `.env` file:
```bash
cp .env.example .env
```
Edit `.env` and set your `GEMINI_API_KEY`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
AGENT_FRAMEWORK=langgraph
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=retail_support
POSTGRES_USER=postgres
POSTGRES_PASSWORD=ROOT
```

### 4.3 Database Setup & Document Ingestion
```bash
# Seed PostgreSQL tables and demo data (including Order #45231)
python scripts/seed_database.py

# Ingest policy markdown documents into ChromaDB
python scripts/ingest_documents.py
```

### 4.4 Start All Microservices
Run the all-in-one startup script:
```bash
python scripts/start_all.py
```
This launches:
- **Web UI & Chat Dashboard**: `http://localhost:8000/`
- **FastAPI OpenAPI Docs**: `http://localhost:8000/docs`
- **Order MCP Server**: `http://localhost:8101`
- **Product MCP Server**: `http://localhost:8102`

Open **http://localhost:8000** in any browser to interact with the visual chat dashboard.

---

## 5. API Reference & Examples

### Health Check
```bash
curl -X GET http://localhost:8000/health
```

### Chat Endpoint (Multi-Intent Demo)
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Where is my order #45231? Can I return the shoes if they don'\''t fit?"
  }'
```

Response format:
```json
{
  "answer": "Your order #45231 has shipped and is expected to arrive by September 3, 2026. The tracking number is TRK123456. According to the footwear return policy, shoes may be returned within 30 days if they are unworn...",
  "intents": ["ORDER_STATUS", "RETURN_POLICY"],
  "sources": [
    {
      "document": "footwear_return_policy.md",
      "section": "1. 30-Day Return Window"
    }
  ],
  "escalated_to_human": false,
  "framework": "langgraph"
}
```

### Framework Switching
You can switch the runtime at request time or via `.env`:
```bash
# Switch to LangChain
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Where is my order #45231? Can I return the shoes if they don'\''t fit?",
    "framework": "langchain"
  }'

# Switch to Google ADK
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Where is my order #45231? Can I return the shoes if they don'\''t fit?",
    "framework": "adk"
  }'

# Switch to Microsoft AutoGen
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Where is my order #45231? Can I return the shoes if they don'\''t fit?",
    "framework": "autogen"
  }'
```

---

## 6. Running Tests

Run the full automated test suite (unit, integration, and E2E parity):
```bash
pytest
```

---

## 7. Docker Deployment

To run all components via Docker Compose:
```bash
docker compose up --build
```
