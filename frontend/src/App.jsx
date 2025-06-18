import { useEffect, useState, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Load chat history when component mounts
    fetch("http://localhost:8000/api/chat/history")
      .then((res) => res.json())
      .then((data) => setMessages(data))
      .catch((error) => console.error("Failed to load chat history:", error));
  }, []);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const newMessage = {
      role: "user",
      content: inputMessage
    };

    setIsLoading(true);
    setInputMessage("");

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newMessage),
      });

      const data = await response.json();
      setMessages(prev => [...prev, newMessage, data]);
    } catch (error) {
      console.error("Failed to send message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <h1>AI Chat Assistant</h1>
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <strong>{message.role === 'user' ? 'You' : 'http://localhost:5173/'}</strong>
            {message.content}
          </div>
        ))}
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
<<<<<<< Updated upstream
=======

<<<<<<< Updated upstream
<<<<<<< Updated upstream
// some sort
>>>>>>> Stashed changes
=======
// some sort
>>>>>>> Stashed changes
=======
// some sort
>>>>>>> Stashed changes
