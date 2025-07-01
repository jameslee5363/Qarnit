import { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";            // (optional) extract chat-only styles

function ChatPage({ token, onLogout }) {
  // --- Chat state (exactly what you had) ---
  const [messages, setMessages]   = useState([]);
  const [input, setInput]         = useState("");
  const [loading, setLoading]     = useState(false);
  const endRef                    = useRef(null);

  // Scroll on new msg
  useEffect(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), [messages]);

  // Pull history on mount
  useEffect(() => {
    if (!token) return;
    axios
      .get("http://localhost:8000/api/chat/history", {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => setMessages(res.data))
      .catch(err => console.error("History:", err));
  }, [token]);

  const send = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = { role: "user", content: input };
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/api/chat", userMsg, {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        }
      });
      setMessages((prev) => [...prev, userMsg, res.data]);
    } catch (err) {
      console.error("Send:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <header className="chat-header">
        <h1>AI Chat Assistant</h1>
        <button className="logout-button" onClick={onLogout}>Logout</button>
      </header>

      <div className="chat-messages">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`message ${m.role} ${
              m.role === "assistant" && i === messages.length - 1 ? "fade-in-down" : ""
            }`}
          >
            <strong>{m.role === "user" ? "You" : "Assistant"}</strong>
            <span>{m.content}</span>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <strong>Assistant</strong>
            <div className="typing-indicator"><span/><span/><span/></div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={send} className="chat-input-form">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="chat-input"
          disabled={loading}
        />
        <button
          type="submit"
          className="send-button"
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatPage;
