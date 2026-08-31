import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  User, 
  Send, 
  Sparkles, 
  ShoppingBag, 
  Layers, 
  BookOpen, 
  Activity, 
  CheckCircle2, 
  AlertCircle,
  Clock,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

const PRESET_SCENARIOS = [
  {
    tag: "⭐ Primary Multi-Intent",
    query: "Where is my order #45231? Can I return the shoes if they don't fit?"
  },
  {
    tag: "📦 Order Status & Tracking",
    query: "What is the status and tracking number for order #45231?"
  },
  {
    tag: "👟 Footwear Return Policy",
    query: "Can I return shoes if they have been worn outside?"
  },
  {
    tag: "🔍 Product & Inventory",
    query: "Do you have Running Shoes in stock and what is the price?"
  },
  {
    tag: "🛡️ Warranty Inquiry",
    query: "What is the warranty coverage for defective products?"
  },
  {
    tag: "👤 Human Escalation",
    query: "I have an unauthorized card charge and need to speak with a human supervisor."
  }
];

export default function App() {
  const [framework, setFramework] = useState("langgraph");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);
  const [health, setHealth] = useState({
    database: "checking",
    chromadb: "checking",
    order_mcp: "checking",
    product_mcp: "checking"
  });

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Poll system health
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch("/health");
        if (res.ok) {
          const data = await res.json();
          setHealth({
            database: data.database === "connected" ? "online" : "degraded",
            chromadb: data.chromadb === "connected" ? "online" : "degraded",
            order_mcp: data.mcp_servers?.order_mcp === "healthy" ? "online" : "standby",
            product_mcp: data.mcp_servers?.product_mcp === "healthy" ? "online" : "standby"
          });
        }
      } catch (err) {
        setHealth({
          database: "standby",
          chromadb: "standby",
          order_mcp: "standby",
          product_mcp: "standby"
        });
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSend = async (customQuery) => {
    const text = customQuery || input;
    if (!text.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      sender: "user",
      text: text.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!customQuery) setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    setLoading(true);

    try {
      const response = await fetch("/api/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text.trim(),
          framework: framework
        })
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: "assistant",
            text: errData.detail || "An error occurred while communicating with the agent runtime.",
            intents: ["ERROR"],
            sources: [],
            framework: framework,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
        return;
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: "assistant",
          text: data.answer,
          intents: data.intents || [],
          sources: data.sources || [],
          framework: data.framework || framework,
          escalated: data.escalated_to_human,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: "assistant",
          text: "Failed to connect to the backend server. Please verify all microservices are running.",
          intents: ["NETWORK_ERROR"],
          sources: [],
          framework: framework,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaInput = (e) => {
    setInput(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
  };

  return (
    <>
      {/* Top Header */}
      <header className="app-header">
        <div className="logo-group">
          <div className="logo-icon">
            <ShoppingBag size={22} />
          </div>
          <div className="logo-text">
            <h1>RetailAI Nexus</h1>
            <p>Multi-Agent Autonomous Support</p>
          </div>
        </div>

        <div className="header-actions">
          {/* Framework Switcher */}
          <div className="framework-selector-wrap" title="Select Active Agent Runtime">
            <button 
              className={`framework-btn ${framework === 'langgraph' ? 'active' : ''}`}
              onClick={() => setFramework('langgraph')}
            >
              LangGraph
            </button>
            <button 
              className={`framework-btn ${framework === 'langchain' ? 'active' : ''}`}
              onClick={() => setFramework('langchain')}
            >
              LangChain
            </button>
            <button 
              className={`framework-btn ${framework === 'adk' ? 'active' : ''}`}
              onClick={() => setFramework('adk')}
            >
              Google ADK
            </button>
            <button 
              className={`framework-btn ${framework === 'maf' ? 'active' : ''}`}
              onClick={() => setFramework('maf')}
            >
              MS Agent Framework
            </button>
            <button 
              className={`framework-btn ${framework === 'autogen' ? 'active' : ''}`}
              onClick={() => setFramework('autogen')}
            >
              AutoGen
            </button>
          </div>

          {/* Health Pill */}
          <div className="health-pill">
            <span className="pulse-dot"></span>
            <span>Systems Active</span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="app-container">
        
        {/* Left Sidebar */}
        <aside className="app-sidebar">
          {/* Scenarios */}
          <div className="sidebar-section">
            <h3><Sparkles size={14} /> Demo Scenarios</h3>
            <div className="preset-list">
              {PRESET_SCENARIOS.map((scenario, idx) => (
                <button 
                  key={idx} 
                  className="preset-card"
                  onClick={() => handleSend(scenario.query)}
                  disabled={loading}
                >
                  <div className="preset-tag">{scenario.tag}</div>
                  <div className="preset-text">{scenario.query}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Microservices Health */}
          <div className="sidebar-section">
            <h3><Activity size={14} /> Microservices Health</h3>
            <div className="health-grid">
              <div className="health-card">
                <span className="health-card-title">PostgreSQL</span>
                <span className="health-card-val" style={{ color: health.database === 'online' ? 'var(--success)' : 'var(--warning)' }}>
                  <CheckCircle2 size={12} /> {health.database.toUpperCase()}
                </span>
              </div>
              <div className="health-card">
                <span className="health-card-title">ChromaDB RAG</span>
                <span className="health-card-val" style={{ color: health.chromadb === 'online' ? 'var(--success)' : 'var(--warning)' }}>
                  <CheckCircle2 size={12} /> {health.chromadb.toUpperCase()}
                </span>
              </div>
              <div className="health-card">
                <span className="health-card-title">Order MCP (8101)</span>
                <span className="health-card-val" style={{ color: health.order_mcp === 'online' ? 'var(--success)' : 'var(--text-muted)' }}>
                  <CheckCircle2 size={12} /> {health.order_mcp.toUpperCase()}
                </span>
              </div>
              <div className="health-card">
                <span className="health-card-title">Product MCP (8102)</span>
                <span className="health-card-val" style={{ color: health.product_mcp === 'online' ? 'var(--success)' : 'var(--text-muted)' }}>
                  <CheckCircle2 size={12} /> {health.product_mcp.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        </aside>

        {/* Right Chat Area */}
        <section className="chat-container">
          
          {/* Message Stream */}
          <div className="chat-messages">
            
            {/* Welcome Banner */}
            <div className="welcome-hero">
              <h2>Autonomous Retail Customer Support</h2>
              <p>
                Powered by <strong>Gemini</strong>, <strong>LangGraph / LangChain / Google ADK</strong>, <strong>PostgreSQL</strong>, <strong>ChromaDB RAG</strong>, and <strong>stateless HTTP MCP Microservices</strong>.
              </p>

              <div className="agent-flow-diagram">
                <div className="agent-chip">🎯 Router Agent</div>
                <div className="flow-arrow">➔</div>
                <div className="agent-chip">📦 Order MCP (Postgres)</div>
                <div className="flow-arrow">+</div>
                <div className="agent-chip">📚 Policy RAG (ChromaDB)</div>
                <div className="flow-arrow">➔</div>
                <div className="agent-chip">🤖 Response Synthesizer</div>
              </div>
            </div>

            {/* Render Messages */}
            {messages.map((msg) => (
              <div key={msg.id} className={`message-row ${msg.sender}`}>
                <div className={`avatar ${msg.sender}`}>
                  {msg.sender === 'user' ? <User size={18} /> : <Bot size={18} />}
                </div>
                <div className="message-content-wrap">
                  <div className="message-bubble">
                    <div style={{ whiteSpace: "pre-line" }}>{msg.text}</div>

                    {/* Sources Card */}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="sources-card">
                        <div className="sources-header">
                          <BookOpen size={13} />
                          <span>Referenced Policy Sources ({msg.sources.length})</span>
                        </div>
                        <div className="sources-list">
                          {msg.sources.map((s, sIdx) => (
                            <div key={sIdx} className="source-item">
                              <span>📄 <strong>{s.document}</strong> {s.section ? `— ${s.section}` : ""}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Metadata Chips */}
                  {msg.sender === 'assistant' && (
                    <div className="meta-chips">
                      {msg.intents && msg.intents.map((intent, iIdx) => (
                        <span key={iIdx} className="intent-badge">
                          🏷️ {intent}
                        </span>
                      ))}
                      {msg.framework && (
                        <span className="framework-badge">
                          ⚡ {msg.framework}
                        </span>
                      )}
                      <span style={{ fontSize: "10px", color: "var(--text-muted)", alignSelf: "center", marginLeft: "4px" }}>
                        {msg.timestamp}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Typing Animation */}
            {loading && (
              <div className="message-row assistant">
                <div className="avatar assistant">
                  <Bot size={18} />
                </div>
                <div className="message-content-wrap">
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Bar */}
          <div className="chat-input-area">
            <div className="input-box-wrapper">
              <textarea
                ref={textareaRef}
                className="chat-textarea"
                placeholder="Ask about orders, returns, products, or policies (e.g. 'Where is order #45231?')..."
                value={input}
                onChange={handleTextareaInput}
                onKeyDown={handleKeyDown}
                rows={1}
                disabled={loading}
              />
              <button 
                className="send-button"
                onClick={() => handleSend()}
                disabled={loading || !input.trim()}
                title="Send message (Enter)"
              >
                <Send size={16} />
              </button>
            </div>
          </div>

        </section>

      </div>
    </>
  );
}
