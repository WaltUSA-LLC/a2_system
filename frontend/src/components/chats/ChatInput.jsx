import { useState } from 'react'
import axios from "axios";
import './ChatInput.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export function ChatInput({ chatMessages, setChatMessages }) {
  const [inputText, setInputText] = useState('');

  function saveInputText(event) {
    setInputText(event.target.value);
  }

  async function sendMessage() {
    const newChatMessages = [
      ...chatMessages,
      {
        message: inputText,
        sender: 'user',
        id: crypto.randomUUID()
      }
    ];

    setChatMessages(newChatMessages);

    await axios.get(`${API_BASE_URL}/agent/chat`, {
                params: {
                    msg:inputText
                },
          }).then((resp) => {
              const response = resp.data.feedback ?? [];
              //console.log("chat resp: ", response);
              setChatMessages([
                ...newChatMessages,
                {
                  message: response,
                  sender: 'robot',
                  id: crypto.randomUUID()
                }
              ]);
          setInputText('');
          }).catch((err) => {
              //setChartOpen(false);
              console.error(err);
              throw new Error("Failed to load mach data");
          });
    
  }

  return (
    <div className="chat-input-container">
      <input
        placeholder="Send a message to Chatbot"
        size="30"
        onChange={saveInputText}
        value={inputText}
        className="chat-input"
      />
      <button
        onClick={sendMessage}
        className="send-button"
      >Send</button>
    </div>
  );
}