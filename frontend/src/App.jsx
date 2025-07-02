import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { useState } from "react";
import Login    from "./Login";
import Register from "./Register";
import ChatPage from "./ChatPage";
import ConversationsLayout from "./ConversationsLayout";

// Protect /chat routes
function RequireAuth({ token, children }) {
  return token ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const navigate = useNavigate();
  const [token, setToken] = useState(localStorage.getItem("token"));

  const handleLogin = (newTok) => {
    localStorage.setItem("token", newTok);
    setToken(newTok);
    navigate("/chat", { replace: true });
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    navigate("/login", { replace: true });
  };

  return (
    <Routes>
      {/* root → chat or login */}
      <Route
        path="/"
        element={token ? <Navigate to="/chat" replace /> : <Navigate to="/login" replace />}
      />

      {/* public */}
      <Route path="/login"    element={<Login onLogin={handleLogin} />} />
      <Route path="/register" element={<Register />} />

      {/* /chat/* keeps the sidebar from ConversationsLayout */}
      <Route
        path="/chat/*"
        element={
          <RequireAuth token={token}>
            <ConversationsLayout token={token} onLogout={handleLogout} />
          </RequireAuth>
        }
      >
      {/* placeholder when no conversation selected */}
      <Route
        index
        element={
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select or start a conversation
          </div>
        }
      />

        {/* conversation — now with its own nested routes */}
        <Route path=":convId/*" element={<ChatPage />} />
      </Route>

      {/* fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
