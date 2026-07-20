import { useState } from 'react'
import { ChatInput } from '../chats/ChatInput';
import ChatMessages from '../chats/ChatMessages';
import './AgentChatView.css'

function AgentChatView() {
  const [chatMessages, setChatMessages] = useState([]);

  return (
    <div className="app-container">
      <ChatMessages
        chatMessages={chatMessages}
      />
      <ChatInput
        chatMessages={chatMessages}
        setChatMessages={setChatMessages}
      />
    </div>
  );
}

export default AgentChatView;