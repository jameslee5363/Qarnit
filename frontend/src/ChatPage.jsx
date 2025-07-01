import { useState, useEffect, useRef } from "react";
import {
  useParams,
  useNavigate,
  useOutletContext,
  Routes,
  Route,
  NavLink,
} from "react-router-dom";
import axios from "axios";
import "./styles/App.css";      // chat-specific styles

/* ---------- MESSAGES TAB ---------- */
function MessagesView({ convId, token }) {
  const [messages, setMessages] = useState([]);
  const [input,    setInput]    = useState("");
  const [loading,  setLoading]  = useState(false);
  const endRef                 = useRef(null);
  const navigate               = useNavigate();

  /* load history whenever convId changes */
  useEffect(() => {
    if (!token || !convId) return;
    axios
      .get(`http://localhost:8000/api/conversations/${convId}/messages`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setMessages(res.data))
      .catch((err) => {
        console.error("History:", err);
        if (err?.response?.status === 404) navigate("/chat");
      });
  }, [convId, token, navigate]);

  useEffect(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), [messages]);

  /* send a message */
  async function send(e) {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    try {
      const res = await axios.post(
        `http://localhost:8000/api/conversations/${convId}/messages`,
        { role: "user", content: input }, // Add role here
        { headers: { Authorization: `Bearer ${token}` } },
      );
      setMessages((prev) => [...prev, res.data]);
    } catch (err) {
      console.error("Send:", err);
    } finally {
      setLoading(false);
      setInput("");
    }
  }

  return (
    <div className="messages-view">
      <div className="messages-list">
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
            <div className="typing-indicator">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={send} className="composer">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message…"
          className="composer-input"
          disabled={loading}
        />
        <button type="submit" className="btn-send" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

/* ---------- MAIN CHAT PAGE ---------- */
export default function ChatPage() {
  const { convId } = useParams();
  const { token, onLogout } = useOutletContext();

  return (
    <div className="chat-container">
      {/* tiny tab-style menu */}

      {/* nested routes render inside <main> */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <Routes>
          <Route index      element={<MessagesView convId={convId} token={token} />} />
        </Routes>
      </main>
    </div>
  );
}

// <button onClick={onLogout} className="logout-btn">Logout</button>