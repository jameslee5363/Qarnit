import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "./styles/Sidebar.css";

export default function ConversationsSidebar({ token, onLogout }) {
  const [convs, setConvs] = useState([]);
  const { convId } = useParams();
  const navigate  = useNavigate();

  /* --- fetch & sort conversations --- */
  useEffect(() => {
    if (!token) return;
    fetch("http://localhost:8000/api/conversations", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) =>
        setConvs(
          [...data].sort((a, b) =>
            a.updated_at && b.updated_at
              ? new Date(b.updated_at) - new Date(a.updated_at)
              : b.id - a.id,
          ),
        ),
      )
      .catch((err) => console.error("Fetch conversations failed:", err));
  }, [token]);

  /* --- if no chat selected, jump to the newest --- */
  useEffect(() => {
    if (convId || !convs.length) return;
    navigate(`/chat/${convs[0].id}`, { replace: true });
  }, [convId, convs, navigate]);

  async function startNew() {
    const res  = await fetch("http://localhost:8000/api/conversations", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    const conv = await res.json();
    setConvs((prev) => [conv, ...prev]);
    navigate(`/chat/${conv.id}`);
  }

  /* --- UI --- */
  return (
    <aside className="sidebar">
      <button onClick={startNew} className="new-chat-btn">+ New Chat</button>

      <ul className="conversation-list">
        {convs.map((c) => {
          const active = String(convId) === String(c.id);
          return (
            <li
              key={c.id}
              onClick={() => navigate(`/chat/${c.id}`)}
              className={`conversation-item${active ? " active" : ""}`}
            >
              {c.title || `Chat ${c.id}`}
            </li>
          );
        })}
      </ul>
      
      <button onClick={onLogout} className="logout-btn">Logout</button>
      
    </aside>
  );
}
