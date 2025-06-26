import { useEffect, useState, useRef } from 'react';
import Login from "./Login";
import Register from "./Register";
import axios from "axios";

import './App.css';

function App() {
  // --- Authentication ---
  const [token, setToken] = useState(localStorage.getItem("token"));
  const isAuthenticated = Boolean(token);
  const [showRegister, setShowRegister] = useState(false);

  const handleLogin = (newToken) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setMessages([]); // clear chat on logout
  };

  // --- Chat state ---
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom on new messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load history after authentication
  useEffect(() => {
    if (!token) return; // run only when logged in

    axios
      .get("http://localhost:8000/api/chat/history", {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setMessages(res.data))
      .catch((err) => console.error("Failed to load chat history:", err));
  }, [token]);

  // Send a message
  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const newMessage = { role: "user", content: inputMessage };
    setInputMessage('');
    setIsLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/api/chat", newMessage, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      setMessages((prev) => [...prev, newMessage, res.data]);
    } catch (err) {
      console.error("Failed to send message:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // --- Render ---
  if (!isAuthenticated) {
    return (
      <div className="chat-container">
        {showRegister ? (
          <>
            <Register onRegister={() => setShowRegister(false)} />
            <div style={{ textAlign: 'center', marginTop: '1rem' }}>
              <button onClick={() => setShowRegister(false)} style={{ background: 'none', color: '#38BDF8', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}>Back to Login</button>
            </div>
          </>
        ) : (
          <>
            <Login onLogin={handleLogin} />
            <div style={{ textAlign: 'center', marginTop: '1rem' }}>
              <button onClick={() => setShowRegister(true)} style={{ background: 'none', color: '#38BDF8', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}>Register</button>
            </div>
          </>
        )}
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>AI Chat Assistant</h1>
        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => {
          const isLastAssistant =
            message.role === 'assistant' && index === messages.length - 1;

          return (
            <div
              key={index}
              className={`message ${message.role} ${isLastAssistant ? 'fade-in-down' : ''}`}
            >
              <strong>{message.role === 'user' ? 'You' : 'Assistant'}</strong>
              <span>{message.content}</span>
            </div>
          );
        })}

        {isLoading && (
          <div className="message assistant">
            <strong>Assistant</strong>
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={sendMessage} className="chat-input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Type your message..."
          className="chat-input"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={isLoading || !inputMessage.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default App;
