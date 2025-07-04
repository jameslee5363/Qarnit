import { useState } from "react";
import axios from "axios";
import "./styles/Login.css";
import { Link } from "react-router-dom";

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    
    try {
      const res = await axios.post("http://localhost:8000/login", new URLSearchParams({
        username,
        password
      }));
      onLogin(res.data.access_token);
    } catch (err) {
      setError("Invalid username or password. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-card">
      <h2>Welcome Back</h2>
      
      <div className="form-group">
        <input 
          value={username} 
          onChange={e => setUsername(e.target.value)} 
          placeholder="Username" 
          required
          disabled={isLoading}
        />
      </div>
      
      <div className="form-group">
        <input 
          type="password" 
          value={password} 
          onChange={e => setPassword(e.target.value)} 
          placeholder="Password" 
          required
          disabled={isLoading}
        />
      </div>
      
      {error && (
        <div className="message error">
          {error}
        </div>
      )}
      
      <button type="submit" disabled={isLoading}>
        {isLoading ? "Signing In..." : "Sign In"}
      </button>
      
      <div className="link-container">
        <p>
          Need an account? <Link to="/register">Create one here</Link>
        </p>
      </div>
    </form>
  );
}
    
export default Login;
