import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';

const App = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [socket, setSocket] = useState(null);
  const [status, setStatus] = useState('Connecting...');

  useEffect(() => {
    // Create WebSocket connection
    const ws = new WebSocket('ws://localhost:5000/ws');
    
    ws.onopen = () => {
      console.log('Connected to WebSocket');
      setStatus('Connected');
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      console.log('Message received:', event.data);
      const message = JSON.parse(event.data);
      setMessages(prev => [...prev, message]);
    };

    ws.onclose = () => {
      console.log('Disconnected from WebSocket');
      setStatus('Disconnected');
      setSocket(null);
    };

    ws.onerror = (error) => {
      console.log('WebSocket error:', error);
      setStatus('Error');
    };

    // Cleanup on unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const sendMessage = () => {
    if (socket && inputMessage) {
      const message = {
        type: 'message',
        content: inputMessage,
        timestamp: new Date().toISOString()
      };
      socket.send(JSON.stringify(message));
      setInputMessage('');
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <Card>
        <CardHeader>
          <h1 className="text-2xl font-bold">Real-time Message Queue</h1>
          <p className={`text-sm ${status === 'Connected' ? 'text-green-500' : 'text-red-500'}`}>
            Status: {status}
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type a message..."
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            />
            <Button onClick={sendMessage}>Send</Button>
          </div>
          <div className="border rounded-lg p-4 h-96 overflow-y-auto">
            {messages.map((msg, index) => (
              <div key={index} className="mb-2 p-2 bg-gray-50 rounded">
                <p className="text-sm text-gray-600">{msg.content}</p>
                <span className="text-xs text-gray-400">
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default App;