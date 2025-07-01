import { useState } from "react";
import axios from "axios";
import './Login.css';
import { Link } from "react-router-dom";

function Register({ onRegister }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const validatePassword = (password) => {
    return (
      password.length >= 8 &&
      /[A-Za-z]/.test(password) &&
      /\d/.test(password)
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage("");
    
    if (!validatePassword(password)) {
      setMessage("Password must be at least 8 characters long and include at least one letter and one number.");
      setIsLoading(false);
      return;
    }
    if (password !== confirmPassword) {
      setMessage("Passwords do not match.");
      setIsLoading(false);
      return;
    }
    
    try {
      await axios.post("http://localhost:8000/register", {
        username,
        email,
        password,
        confirm_password: confirmPassword
      });
      setMessage("Registration successful! You can now log in.");
      if (onRegister) onRegister();
    } catch (err) {
      const detail = err?.response?.data?.detail || "Registration failed";
      setMessage(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessage = () => {
    setMessage("");
  };

  return (
    <form onSubmit={handleSubmit} className="login-container">
      <h2>Create Account</h2>
      
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
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="Email"
          required
          disabled={isLoading}
        />
      </div>
      
      <div className="form-group">
        <input
          type="password"
          value={password}
          onChange={e => { setPassword(e.target.value); clearMessage(); }}
          placeholder="Password"
          required
          disabled={isLoading}
        />
      </div>
      
      <div className="form-group">
        <input
          type="password"
          value={confirmPassword}
          onChange={e => { setConfirmPassword(e.target.value); clearMessage(); }}
          placeholder="Confirm Password"
          required
          disabled={isLoading}
        />
      </div>
      
      {message && (
        <div className={`message ${message.includes('successful') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}
      
      <button type="submit" disabled={isLoading}>
        {isLoading ? "Creating Account..." : "Create Account"}
      </button>
      
      <div className="link-container">
        <p>
          Already have an account? <Link to="/login">Sign in here</Link>
        </p>
      </div>
    </form>
  );
}

export default Register;
