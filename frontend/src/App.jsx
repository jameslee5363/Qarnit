import { Routes, Route, Navigate, useNavigate } from "react-router-dom";
import { useState } from "react";
import Login    from "./Login";
import Register from "./Register";
import ChatPage from "./ChatPage";

// Small wrapper to protect /chat
function RequireAuth({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" replace />;
}

function App() {
  const navigate = useNavigate();
  const [token, setToken] = useState(localStorage.getItem("token"));

  // ---- Auth helpers ----
  const handleLogin = (newTok) => {
    localStorage.setItem("token", newTok);
    setToken(newTok);
    navigate("/chat");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    navigate("/login", { replace: true });
  };

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/chat" />} />

      <Route path="/login"
        element={<Login  onLogin={handleLogin} />}
      />

      <Route path="/register"
        element={<Register />}
      />

      <Route
        path="/chat"
        element={
          <RequireAuth>
            <ChatPage token={token} onLogout={handleLogout} />
          </RequireAuth>
        }
      />

      {/* catch-all for bad URLs */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
