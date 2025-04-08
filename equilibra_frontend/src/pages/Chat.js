// src/pages/Chat.js
import React, { useState } from 'react';


const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSendMessage = () => {
    if (input.trim() === '') return;

    const newMessage = {
      id: Date.now(),
      text: input,
      sender: 'user',
    };

    setMessages([...messages, newMessage]);
    setInput('');
  };

  return (
    <div className="container">
      <h1>Chat</h1>
      <div className="chat-window">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.sender}`}>
            {message.text}
          </div>
        ))}
      </div>
      <div className="input-group">
        <input
          type="text"
          className="form-control"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />
        <button className="btn btn-primary" onClick={handleSendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}
export default Chat;