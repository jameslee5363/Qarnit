import { Outlet } from "react-router-dom";
import ConversationsSidebar from "./ConversationsSidebar";
import "./styles/index.css";            // global
import "./styles/Layout.css";           // (optional extra styles for layout)

export default function ConversationsLayout({ token, onLogout }) {
  return (
    <div className="layout">              {/* full-height flex container */}
      <ConversationsSidebar token={token} onLogout={onLogout} />
      <div className="layout-main">
        <Outlet context={{ token, onLogout }} />
      </div>
    </div>
  );
}
