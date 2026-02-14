import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './ChatPanel.css';

// Configure axios defaults
axios.defaults.headers.common['Content-Type'] = 'application/json';
axios.defaults.headers.common['Accept'] = 'application/json';

const ChatPanel = ({ onNewLayer, onLoading, onNotification }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'RAZORBILL AI READY\n\nTry:\n• Population in Brazil\n• Earthquakes in Japan\n• Weather in London\n• Roads in Paris'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    const userInput = input;
    setInput('');
    setLoading(true);
    onLoading && onLoading(true);

    try {
      console.log('Sending message:', userInput);

      const response = await axios.post('/api/chat', {
        message: userInput
      }, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        timeout: 30000 // 30 second timeout
      });

      console.log('Response received:', response.data);

      const assistantMessage = {
        role: 'assistant',
        content: response.data.message || 'Response received'
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (response.data.layer_data) {
        const metadata = response.data.layer_data.metadata;
        onNewLayer(
          response.data.layer_data,
          metadata?.center || response.data.view_position
        );

        const featureCount = metadata?.feature_count || 0;

        onNotification && onNotification({
          message: `✓ Loaded ${featureCount} features from ${metadata?.source}`,
          type: 'success'
        });
      }
    } catch (error) {
      console.error('Chat error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        headers: error.response?.headers
      });

      let errorMsg = 'Connection error';

      if (error.response) {
        // Server responded with error
        errorMsg = error.response.data?.message || `Server error (${error.response.status})`;
      } else if (error.request) {
        // Request made but no response
        errorMsg = 'No response from server. Is the backend running?';
      } else {
        errorMsg = error.message;
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '❌ ERROR: ' + errorMsg
      }]);

      onNotification && onNotification({
        message: `✗ Error: ${errorMsg}`,
        type: 'error'
      });
    }

    setLoading(false);
    onLoading && onLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-header">
              <span className="message-sender">{msg.role === 'user' ? 'USER' : 'AI'}</span>
              <span className="message-time">{new Date().toLocaleTimeString()}</span>
            </div>
            <div className="message-content">
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-header">
              <span className="message-sender">AI</span>
            </div>
            <div className="message-content">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about any location..."
          disabled={loading}
          className="chat-input"
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          className="send-btn"
        >
          {loading ? 'SENDING...' : 'SEND'}
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;
