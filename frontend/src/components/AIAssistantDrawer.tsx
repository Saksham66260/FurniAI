import React, { useState, useRef, useEffect } from 'react';
import { chatWithAgent } from '../services/api';
import type { AgentChatResponse } from '../types';

interface Message {
  id: string;
  sender: 'user' | 'agent';
  text: string;
  toolCalls?: Array<{ name: string; args: Record<string, any> }>;
  approvalRequired?: boolean;
  approvalPrompt?: string | null;
  checkoutResult?: any;
}

interface AIAssistantDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onOrderCreated?: (orderId: number) => void;
}

export const AIAssistantDrawer: React.FC<AIAssistantDrawerProps> = ({
  isOpen,
  onClose,
  onOrderCreated,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'agent',
      text: "👋 Hi! I'm your FurniAI shopping assistant. I can help you find furniture with semantic hybrid search, compare specifications, verify warehouse stock, or answer care and assembly questions from grounded documentation.",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState<string>(() => `session-${Math.random().toString(36).substring(2, 9)}`);
  const [awaitingApproval, setAwaitingApproval] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!isOpen) return null;

  const handleSend = async (userText: string = input) => {
    if (!userText.trim() || loading) return;

    const userMessage: Message = {
      id: Math.random().toString(),
      sender: 'user',
      text: userText,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response: AgentChatResponse = await chatWithAgent(userText, threadId);
      setThreadId(response.thread_id);

      const agentMessage: Message = {
        id: Math.random().toString(),
        sender: 'agent',
        text: response.reply,
        toolCalls: response.tool_calls,
        approvalRequired: response.approval_required,
        approvalPrompt: response.approval_prompt,
        checkoutResult: response.checkout_result,
      };

      setMessages((prev) => [...prev, agentMessage]);

      if (response.approval_required) {
        setAwaitingApproval(true);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: Math.random().toString(),
          sender: 'agent',
          text: `⚠️ Error: ${err.message || 'Unable to connect to AI assistant.'}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleApprovalResponse = async (approved: boolean) => {
    setLoading(true);
    setAwaitingApproval(false);

    try {
      const response: AgentChatResponse = await chatWithAgent('', threadId, approved);

      const agentMessage: Message = {
        id: Math.random().toString(),
        sender: 'agent',
        text: response.reply,
        toolCalls: response.tool_calls,
        checkoutResult: response.checkout_result,
      };

      setMessages((prev) => [...prev, agentMessage]);

      if (approved && response.checkout_result?.order_id && onOrderCreated) {
        onOrderCreated(response.checkout_result.order_id);
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: Math.random().toString(),
          sender: 'agent',
          text: `⚠️ Error handling approval: ${err.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    'Find minimalist wooden desks under ₹15,000',
    'How do I care for walnut study desks?',
    'Check inventory for product 12',
    'Ready to checkout my cart',
  ];

  return (
    <div className="agent-drawer">
      {/* Header */}
      <div
        style={{
          padding: '18px 20px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(15, 22, 38, 0.95)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '1.4rem' }}>🤖</span>
          <div>
            <h3 style={{ fontSize: '1.05rem', margin: 0 }}>FurniAI Assistant</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--accent-emerald)' }} />
              LangGraph + Groq Orchestration
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          style={{ fontSize: '1.4rem', color: 'var(--text-muted)' }}
        >
          &times;
        </button>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
        }}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '85%',
            }}
          >
            {/* Tool Calls badge */}
            {msg.toolCalls && msg.toolCalls.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '8px' }}>
                {msg.toolCalls.map((tc, idx) => (
                  <span key={idx} className="badge badge-indigo" style={{ fontSize: '0.68rem' }}>
                    🛠️ Tool: {tc.name}
                  </span>
                ))}
              </div>
            )}

            {/* Bubble */}
            <div
              style={{
                padding: '12px 16px',
                borderRadius: 'var(--radius-md)',
                background:
                  msg.sender === 'user'
                    ? 'linear-gradient(135deg, #6366f1, #4f46e5)'
                    : 'rgba(255, 255, 255, 0.05)',
                border:
                  msg.sender === 'user'
                    ? 'none'
                    : '1px solid rgba(255, 255, 255, 0.08)',
                color: 'var(--text-primary)',
                fontSize: '0.9rem',
                lineHeight: 1.5,
                whiteSpace: 'pre-line',
              }}
            >
              {msg.text}
            </div>

            {/* Human-in-the-loop confirmation card */}
            {msg.approvalRequired && awaitingApproval && (
              <div
                style={{
                  marginTop: '12px',
                  padding: '14px',
                  background: 'rgba(245, 158, 11, 0.1)',
                  border: '1px solid rgba(245, 158, 11, 0.35)',
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px', color: '#fcd34d', fontWeight: 600, fontSize: '0.85rem' }}>
                  <span>🛡️</span>
                  <span>Human-in-the-Loop Safety Approval</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                  {msg.approvalPrompt || 'Do you approve creating the order in PostgreSQL?'}
                </p>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    className="btn-amber"
                    style={{ flex: 1, padding: '8px 12px', fontSize: '0.85rem' }}
                    onClick={() => handleApprovalResponse(true)}
                    disabled={loading}
                  >
                    ✓ Yes, Place Order
                  </button>
                  <button
                    className="btn-secondary"
                    style={{ flex: 1, padding: '8px 12px', fontSize: '0.85rem' }}
                    onClick={() => handleApprovalResponse(false)}
                    disabled={loading}
                  >
                    ✕ Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ alignSelf: 'flex-start', display: 'flex', gap: '8px', alignItems: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            <span style={{ display: 'inline-block', animation: 'spin 1s infinite linear' }}>⏳</span>
            <span>AI agent is reasoning with strict backend tools...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Quick Prompts */}
      <div style={{ padding: '8px 16px', borderTop: '1px solid var(--border-subtle)', background: 'rgba(0,0,0,0.2)' }}>
        <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px' }}>
          {quickPrompts.map((prompt, i) => (
            <button
              key={i}
              className="badge badge-slate"
              style={{ cursor: 'pointer', whiteSpace: 'nowrap', textTransform: 'none' }}
              onClick={() => handleSend(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input bar */}
      <div
        style={{
          padding: '16px 20px',
          borderTop: '1px solid var(--border-subtle)',
          background: 'rgba(15, 22, 38, 0.95)',
          display: 'flex',
          gap: '8px',
        }}
      >
        <input
          type="text"
          className="search-input"
          placeholder="Ask FurniAI anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          disabled={loading || awaitingApproval}
          style={{ padding: '10px 14px', fontSize: '0.9rem' }}
        />
        <button
          className="btn-primary"
          onClick={() => handleSend()}
          disabled={loading || !input.trim() || awaitingApproval}
          style={{ padding: '10px 16px' }}
        >
          Send
        </button>
      </div>
    </div>
  );
};
