# Elaira — MVP Use Case 1: Retail Customer Support

You are working on the **Elaira** project, an AI-powered customer/IT support automation platform.

For this task, implement **ONLY the first small vertical slice** of the system.

Do not implement the entire Elaira platform yet.

The first use case is:

> **"Where is my order #45231? Can I return the shoes if they don't fit?"**

This use case must demonstrate:

* Multi-intent understanding
* Multi-agent orchestration
* RAG
* ChromaDB
* MCP
* Stateless HTTP MCP communication
* PostgreSQL
* Gemini
* Guardrails at the tool execution boundary
* Framework-selectable agent runtime

---

# 1. TECHNOLOGY STACK

Use:

* Python 3.12+
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Gemini API
* ChromaDB
* LangGraph
* LangChain
* Google ADK
* MCP SDK using the current supported stateless HTTP/JSON-RPC architecture
* Pydantic
* Docker where useful

Gemini API key comes from:

```env
GEMINI_API_KEY=
```

The user will paste the actual key into `.env`.

Never hardcode the API key.

Never print or log it.

---

# 2. POSTGRESQL

Use PostgreSQL as the source of structured operational data.

Connection configuration:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=elaira
POSTGRES_USER=postgres
POSTGRES_PASSWORD=ROOT
```

Do NOT use:

* SQLite
* JSON files
* CSV files
* in-memory dictionaries as the database

Create the database schema using SQLAlchemy + Alembic.

For this first use case, create only the tables we actually need.

At minimum:

```text
customers
orders
order_items
products
```

Keep the schema simple.

---

# 3. DEMO DATA

Seed PostgreSQL with realistic retail data.

The important demonstration order is:

```text
Order ID: 45231
Customer: demo customer
Product: Running Shoes
Status: SHIPPED
ETA: 2026-09-03
Tracking Number: TRK123456
```

Create enough additional orders/products to demonstrate that the system is actually querying PostgreSQL rather than returning hardcoded information.

Do NOT hardcode order #45231 inside the agent.

The agent must retrieve it through the MCP tool.

---

# 4. RAG DATA

Create a small set of realistic retail policy documents.

For example:

```text
documents/
    return_policy.md
    footwear_return_policy.md
    warranty_policy.md
    shipping_policy.md
    faq.md
```

The important policy should state something equivalent to:

* Shoes can be returned within 30 days.
* Shoes must be unworn.
* The product must satisfy the applicable return conditions.

Do not hardcode this policy into the agent prompt.

The Policy Agent must retrieve it from ChromaDB.

---

# 5. CHROMADB

Implement a proper RAG ingestion pipeline.

Flow:

```text
Policy Documents
      ↓
Document Loader
      ↓
Chunking
      ↓
Gemini Embeddings
      ↓
ChromaDB
      ↓
Retriever
      ↓
Policy Agent
```

Store useful metadata such as:

```text
document_name
document_type
section
source
```

The Policy Agent response must include the source documents used.

Do not fabricate citations.

---

# 6. AGENTS

For MVP-1, implement exactly these agents:

```text
Orchestrator Agent
Order Agent
Policy Agent
Response Agent
```

Do NOT implement Product Agent yet.

Product support will be a later use case.

---

# 7. ORCHESTRATOR AGENT

The Orchestrator is the hub.

Its job is to:

1. Understand the user's request.
2. Detect multiple intents.
3. Determine which specialist agents are required.
4. Execute them.
5. Collect their results.
6. Pass the results to the Response Agent.
7. Return the final response.

For:

> Where is my order #45231? Can I return the shoes if they don't fit?

It should identify:

```text
Intent 1:
ORDER_STATUS

Intent 2:
RETURN_POLICY
```

and route them independently:

```text
ORDER_STATUS
    ↓
Order Agent

RETURN_POLICY
    ↓
Policy Agent
```

Do not allow specialist agents to directly call each other.

The Orchestrator owns the workflow.

---

# 8. ORDER AGENT

The Order Agent is responsible only for structured order information.

It should be able to obtain:

```text
order status
ETA
tracking number
order items
```

The Order Agent must access order information through MCP.

It must NOT directly access PostgreSQL.

Correct architecture:

```text
Order Agent
     ↓
MCP Client
     ↓
Stateless HTTP MCP
     ↓
Order/ITSM MCP Server
     ↓
Repository
     ↓
PostgreSQL
```

Create an MCP tool such as:

```text
get_order
```

with a strongly typed input:

```text
order_id
```

and structured output.

Example:

```json
{
  "order_id": "45231",
  "status": "SHIPPED",
  "eta": "2026-09-03",
  "tracking_number": "TRK123456",
  "items": [
    {
      "product_name": "Running Shoes",
      "quantity": 1
    }
  ]
}
```

The exact schema may be improved if needed.

---

# 9. POLICY AGENT

The Policy Agent is responsible for unstructured policy knowledge.

It must use:

```text
User Query
    ↓
Retriever
    ↓
ChromaDB
    ↓
Relevant Policy Chunks
    ↓
Gemini
```

It should answer:

> Can I return the shoes if they don't fit?

based on retrieved policy content.

It must NOT query PostgreSQL for policy information.

It must not invent policy rules.

If the retrieved information is insufficient, clearly state that the available policy information is insufficient.

---

# 10. RESPONSE AGENT

The Response Agent receives the outputs of the other agents.

For example:

```text
Order Agent:
SHIPPED
ETA: 2026-09-03
Tracking: TRK123456

Policy Agent:
Shoes can be returned within 30 days if unworn.
```

The Response Agent synthesizes these into a concise customer-facing answer.

Example style:

> Your order #45231 has shipped and is expected to arrive by September 3, 2026. The tracking number is TRK123456.
>
> According to the return policy, the shoes can be returned within 30 days as long as they are unworn and meet the return conditions.

Do not expose internal agent reasoning.

Do not expose chain-of-thought.

---

# 11. MCP

This project must use MCP properly.

Use the current MCP implementation supported by the selected SDK.

Use:

```text
Stateless HTTP
JSON-RPC
MCP Client
MCP Server
```

Do NOT implement the old session-dependent HTTP/SSE architecture.

Do NOT make MCP depend on persistent server-side protocol sessions.

---

# 12. MCP SERVER

For this MVP, create an Order MCP Server.

Suggested structure:

```text
mcp_servers/
    order/
        server.py
        tools.py
```

Expose:

```text
get_order
```

The MCP server should call an application/service/repository layer.

Architecture:

```text
MCP Tool
   ↓
Order Service
   ↓
Order Repository
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

Do not put SQL directly inside the MCP tool implementation.

---

# 13. GUARDRAIL

Even though `get_order` is a read-only, low-risk operation, implement the guardrail boundary now so the architecture is established correctly.

The execution path should be:

```text
Order Agent
    ↓
Tool Selection
    ↓
Guardrail
    ↓
MCP Client
    ↓
MCP Server
    ↓
PostgreSQL
```

For `get_order`:

```text
Risk: LOW
Approval: NOT_REQUIRED
```

The guardrail must be deterministic Python logic.

Do not ask Gemini to determine whether the user is authorized.

---

# 14. AGENT FRAMEWORK SWITCHING

The project must support:

```env
AGENT_FRAMEWORK=langgraph
```

and:

```env
AGENT_FRAMEWORK=langchain
```

and:

```env
AGENT_FRAMEWORK=adk
```

The default is:

```env
AGENT_FRAMEWORK=langgraph
```

Each implementation must be genuine and native to that framework.

Do NOT create a fake framework abstraction.

Do NOT implement:

```python
if framework == "langgraph":
    # manually emulate everything
```

inside every agent.

Instead, keep framework-specific implementations separated.

Suggested structure:

```text
app/
    agents/
        runtimes/
            langgraph/
                runtime.py
                workflow.py
            langchain/
                runtime.py
                agents.py
            adk/
                runtime.py
                agents.py
```

The common application/domain logic should remain outside the framework-specific runtime code.

The MCP layer must remain identical regardless of which framework is selected.

The RAG knowledge source must remain identical.

The PostgreSQL database must remain identical.

The public FastAPI API must remain identical.

---

# 15. LANGGRAPH IMPLEMENTATION

This is the primary implementation.

Use an actual LangGraph workflow.

Conceptually:

```text
START
  ↓
Orchestrator / Router
  ↓
Intent Routing
  ├───────────────┐
  ▼               ▼
Order Agent    Policy Agent
  │               │
  │               │
  └───────┬───────┘
          ▼
   Response Agent
          ▼
         END
```

Because the query contains two independent intents, the implementation should support executing both branches and collecting their results before synthesis.

Use proper graph state.

Do not just use LangGraph as a wrapper around a normal Python function.

---

# 16. LANGCHAIN IMPLEMENTATION

Implement the equivalent business flow using native LangChain capabilities.

Use LangChain's actual:

* Gemini integration
* prompts
* retriever
* tools
* agent functionality where appropriate

Do not copy the LangGraph implementation and rename classes.

The resulting workflow should behave the same from the user's perspective.

---

# 17. ADK IMPLEMENTATION

Implement the equivalent business flow using Google's Agent Development Kit.

Use native ADK concepts for:

* agents
* tools
* orchestration
* execution

Do not implement ADK by wrapping LangGraph.

Do not implement ADK by wrapping LangChain.

---

# 18. IMPORTANT SEPARATION

Maintain these boundaries:

```text
             ┌─────────────────────┐
             │ Agent Runtime       │
             │ LangGraph/LangChain │
             │ /ADK                │
             └──────────┬──────────┘
                        │
                        ▼
                    Agent Logic
                    /        \
                   /          \
                  ▼            ▼
               RAG             MCP
                │               │
                ▼               ▼
            ChromaDB        MCP Server
                                │
                                ▼
                           PostgreSQL
```

RAG and MCP are separate capabilities.

Do not make ChromaDB part of MCP.

Do not make PostgreSQL part of RAG.

Do not make MCP responsible for agent orchestration.

---

# 19. FASTAPI

Create:

```text
POST /api/v1/chat
GET /health
```

Example request:

```json
{
  "message": "Where is my order #45231? Can I return the shoes if they don't fit?"
}
```

Example response:

```json
{
  "answer": "...",
  "intents": [
    "ORDER_STATUS",
    "RETURN_POLICY"
  ],
  "sources": [
    {
      "type": "policy",
      "document": "footwear_return_policy.md"
    }
  ],
  "actions": []
}
```

Do not expose internal chain-of-thought.

It is acceptable to expose high-level execution metadata for debugging, but never hidden reasoning.

---

# 20. LOGGING

Use structured Python logging.

For a request, log useful events such as:

```text
request_received
intent_detected
agent_started
agent_completed
rag_search
mcp_tool_requested
guardrail_checked
mcp_tool_completed
response_generated
```

Include:

```text
request_id
```

where appropriate.

Never log:

```text
GEMINI_API_KEY
```

or other secrets.

---

# 21. PROJECT STRUCTURE

Use a clean structure similar to:

```text
elaira/
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   └── routes/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   │
│   ├── agents/
│   │   ├── domain/
│   │   │   ├── orchestrator.py
│   │   │   ├── order.py
│   │   │   ├── policy.py
│   │   │   └── response.py
│   │   │
│   │   └── runtimes/
│   │       ├── langgraph/
│   │       ├── langchain/
│   │       └── adk/
│   │
│   ├── rag/
│   │   ├── ingestion.py
│   │   ├── retrieval.py
│   │   └── embeddings.py
│   │
│   ├── guardrails/
│   │   ├── policy.py
│   │   └── risk.py
│   │
│   ├── mcp/
│   │   └── client/
│   │
│   └── database/
│       ├── models/
│       ├── repositories/
│       └── session.py
│
├── mcp_servers/
│   └── order/
│       ├── server.py
│       └── tools.py
│
├── documents/
│
├── migrations/
│
├── scripts/
│
├── tests/
│
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

Adjust the structure if the current framework versions have a better recommended organization.

---

# 22. TESTS

Implement tests for the vertical slice.

## Database

Test:

```text
get order #45231
```

## MCP

Test:

```text
get_order
```

including:

* valid order
* unknown order
* invalid order ID
* MCP error handling

## RAG

Test:

```text
shoe return policy
```

Ensure the correct policy document is retrieved.

## Agent

Test:

```text
ORDER_STATUS
RETURN_POLICY
```

## End-to-end

Test:

```text
Where is my order #45231?
```

and:

```text
Can I return the shoes if they don't fit?
```

and especially:

```text
Where is my order #45231? Can I return the shoes if they don't fit?
```

The last test must demonstrate multi-intent orchestration.

---

# 23. SUCCESS CRITERIA

The MVP is successful when this request works:

```text
Where is my order #45231? Can I return the shoes if they don't fit?
```

Expected execution:

```text
User
 ↓
FastAPI
 ↓
Selected Agent Runtime
 ↓
Orchestrator
 ├───────────────┐
 ▼               ▼
Order Agent    Policy Agent
 │               │
 ▼               ▼
MCP             RAG
 │               │
 ▼               ▼
PostgreSQL    ChromaDB
 │               │
 └───────┬───────┘
         ▼
 Response Agent
         │
         ▼
      FastAPI
         │
         ▼
        User
```

The response must correctly combine:

```text
Structured operational data
+
Unstructured policy knowledge
```

---

# 24. WHAT NOT TO BUILD YET

Do NOT implement:

* Product Agent
* Product MCP Server
* human escalation workflow
* ticket creation
* complex authentication
* Azure services
* ServiceNow
* Azure SQL
* Azure AI Search
* Teams/Bot integration
* Kubernetes
* Redis
* Kafka
* Prometheus/Grafana
* complex frontend

Those belong to later phases.

For now, build one **complete, clean, working vertical slice**.

---

# 25. IMPLEMENTATION ORDER

Implement in this order:

```text
1. Project setup
2. Configuration
3. PostgreSQL
4. Database models
5. Demo data
6. ChromaDB
7. Policy documents
8. RAG ingestion/retrieval
9. Order MCP Server
10. MCP Client
11. Guardrail boundary
12. LangGraph implementation
13. LangChain implementation
14. ADK implementation
15. FastAPI
16. Tests
17. README
18. Local execution verification
```

After each major stage, verify that it works before moving forward.

---

# 26. DEVELOPMENT BEHAVIOR

Do not blindly generate code.

Before implementation:

1. Inspect the repository.
2. Inspect the existing environment.
3. Check installed Python version.
4. Check PostgreSQL connectivity.
5. Check current compatible package versions.
6. Verify the MCP SDK's current stateless HTTP implementation.
7. Verify compatibility between LangGraph, LangChain, ADK, Gemini and MCP.
8. Use current APIs rather than outdated tutorials.

If an API has changed, use the current supported API.

Do not downgrade libraries merely to make old sample code work unless there is a strong compatibility reason.

Keep the implementation simple and laptop-friendly.

Do not over-engineer.

The primary goal is a **working, demonstrable, architecturally correct MVP vertical slice**.

At the end, provide:

1. What was implemented
2. Project structure
3. How to configure `.env`
4. How to start PostgreSQL/ChromaDB
5. How to seed the database
6. How to ingest RAG documents
7. How to start the MCP server
8. How to start Elaira
9. How to switch `AGENT_FRAMEWORK`
10. Example API request
11. Example expected response
12. Tests executed and their results
13. Any limitations or compatibility issues discovered
