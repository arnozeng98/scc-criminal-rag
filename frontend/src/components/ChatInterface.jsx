import React, { useState, useEffect, useRef } from 'react';
import './ChatInterface.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ChatMessage = ({ message, isUser }) => (
  <div className={`chat-message ${isUser ? 'user-message' : 'assistant-message'}`}>
    <div className="message-avatar">
      {isUser ? '👤' : '🤖'}
    </div>
    <div className="message-content">
      {message.text}
      {message.citations && message.citations.length > 0 && (
        <div className="citations">
          <h4>Sources:</h4>
          <ul>
            {message.citations.map((citation, index) => (
              <li key={index}>{citation.citation_text}</li>
            ))}
          </ul>
        </div>
      )}
      {message.error && (
        <div className="error-message">Error: {message.error}</div>
      )}
    </div>
  </div>
);

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { text: "Welcome to the SCC Criminal Cases Assistant. How can I help you with information about Canadian Supreme Court criminal cases?", isUser: false }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message
    setMessages(prev => [...prev, { text: input, isUser: true }]);
    
    // Clear input and show loading state
    setInput('');
    setIsLoading(true);
    
    try {
      // Send query to API
      const response = await fetch(`${API_URL}/rag/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: input,
          top_k: 5
        }),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Add assistant response
      setMessages(prev => [...prev, {
        text: data.answer,
        citations: data.citations,
        error: data.error,
        isUser: false
      }]);
      
    } catch (error) {
      console.error('Error querying RAG system:', error);
      
      // Add error message
      setMessages(prev => [...prev, {
        text: "I'm sorry, I encountered an error processing your request. Please try again later.",
        error: error.message,
        isUser: false
      }]);
      
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>SCC Criminal Cases Assistant</h2>
      </div>
      
      <div className="chat-messages">
        {messages.map((message, index) => (
          <ChatMessage key={index} message={message} isUser={message.isUser} />
        ))}
        
        {isLoading && (
          <div className="chat-message assistant-message">
            <div className="message-avatar">🤖</div>
            <div className="message-content loading">
              <div className="dot-flashing"></div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={handleInputChange}
          placeholder="Ask about Canadian Supreme Court criminal cases..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          {isLoading ? '...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default ChatInterface; 