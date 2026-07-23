import { useState } from 'react'
import axios from "axios";
import Stack from '@mui/material/Stack';
import SendIcon from '@mui/icons-material/Send';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export function ChatInput({ chatMessages, setChatMessages }) {
  const [inputText, setInputText] = useState('');

  function saveInputText(event) {
    setInputText(event.target.value);
  }

  async function sendMessage() {
    const newChatMessagesWithThink = [
      ...chatMessages,
      {
        message: inputText,
        sender: 'user',
        id: crypto.randomUUID()
      },
      {
        message: <CircularProgress size={20} />,
        sender: 'robot',
        id: crypto.randomUUID()
      }
    ];

    const newChatMessages = [
      ...chatMessages,
      {
        message: inputText,
        sender: 'user',
        id: crypto.randomUUID()
      }
    ];

    setChatMessages(newChatMessagesWithThink);
    setInputText('');
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
          }).catch((err) => {
              //setChartOpen(false);
              console.error(err);
              throw new Error("Failed to load mach data");
          });
    
  }

  return (
    <Stack direction="row"
           spacing={3}
           sx={{
              justifyContent: "center",
              alignItems: "center",
            }}
    >
      <TextField
        placeholder="Send a message to AI"
        onChange={saveInputText}
        value={inputText}
        sx={{
          '& .MuiInputBase-input': {
            padding: 1,
          },
        }}
        fullWidth
      />
      <Button
        onClick={sendMessage}
        variant="contained"
        endIcon={<SendIcon />}
        sx={{ height: '30px',
          backgroundColor: "primary.light"
        }}
      >
        Send
      </Button>
    </Stack>
  );
}
