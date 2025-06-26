import { useState } from "react";
import axios from "axios";
import './Login.css';

function Register({ onRegister }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");             // ← NEW
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");

  const validatePassword = (password) => {
    return (
      password.length >= 8 &&
      /[A-Za-z]/.test(password) &&
      /\d/.test(password)
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validatePassword(password)) {
      setMessage("Password must be at least 8 characters long and include at least one letter and one number.");
      return;
    }
    if (password !== confirmPassword) {
      setMessage("Passwords do not match.");
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
    }
  };

  return (
    <form onSubmit={handleSubmit} className="login-container">
      <h2>Register</h2>
      <input
        value={username}
        onChange={e => setUsername(e.target.value)}
        placeholder="Username"
        required
      />
      <input
        type="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={e => { setPassword(e.target.value); setMessage(""); }}
        placeholder="Password"
        required
      />
      <input
        type="password"
        value={confirmPassword}
        onChange={e => { setConfirmPassword(e.target.value); setMessage(""); }}
        placeholder="Confirm Password"
        required
      />
      <button type="submit">Register</button>
      {message && (
        <div
          style={{
            marginTop: '1rem',
            textAlign: 'center',
            color: message.includes('successful') ? 'green' : 'red'
          }}
        >
          {message}
        </div>
      )}
    </form>
  );
}

export default Register;
