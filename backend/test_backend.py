import websocket
import json
import time
import requests
import threading

def on_message(ws, message):
    print(f"Received message: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connection opened")

def test_websocket():
    # WebSocket connection
    ws = websocket.WebSocketApp(
        "ws://localhost:5000/ws",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    
    # Start WebSocket connection in a separate thread
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.daemon = True
    ws_thread.start()
    
    # Wait for connection to establish
    time.sleep(2)
    
    try:
        # Test sending messages via WebSocket
        test_message = {
            "type": "message",
            "content": "Test message via WebSocket",
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        ws.send(json.dumps(test_message))
        print("Sent WebSocket message")
        
        # Test sending messages via REST API
        response = requests.post(
            'http://localhost:5000/api/send',  # Updated endpoint
            json={
                "type": "message",
                "content": "Test message via REST API",
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        print(f"REST API status code: {response.status_code}")
        if response.status_code == 200:
            print(f"REST API response: {response.json()}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    
    # Keep the script running to receive messages
    time.sleep(5)
    ws.close()

if __name__ == "__main__":
    test_websocket()