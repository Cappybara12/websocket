from flask import Flask, request
from flask_sock import Sock
from flask_cors import CORS
import redis
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)
sock = Sock(app)

# Initialize Redis
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

QUEUE_NAME = 'messages'

@sock.route('/ws')
def ws(sock):
    print("WebSocket connection established")
    try:
        # Subscribe to Redis
        pubsub = redis_client.pubsub()
        pubsub.subscribe(QUEUE_NAME)
        
        # Send initial connection message
        sock.send(json.dumps({
            "type": "system",
            "content": "Connected to server",
            "timestamp": str(datetime.now())
        }))

        while True:
            # Check for WebSocket messages
            data = sock.receive()
            if data:
                message = json.loads(data)
                print(f"Received message: {message}")
                
                # Store in Redis and print queue length
                redis_client.rpush(QUEUE_NAME, json.dumps(message))
                queue_length = redis_client.llen(QUEUE_NAME)
                print(f"Messages in queue: {queue_length}")
                
                # Print last 5 messages in queue
                last_messages = redis_client.lrange(QUEUE_NAME, -5, -1)
                print("Last 5 messages in queue:")
                for msg in last_messages:
                    print(f"- {msg}")
                
                # Publish to channel
                redis_client.publish(QUEUE_NAME, json.dumps(message))
                print(f"Published message to channel: {QUEUE_NAME}")

            # Check for Redis messages
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                print(f"Received from Redis channel: {message['data']}")
                sock.send(message['data'])

    except Exception as e:
        print(f"Error in WebSocket: {e}")
    finally:
        print("WebSocket connection closed")
        pubsub.unsubscribe()

# Add a new endpoint to view messages
@app.route('/api/messages', methods=['GET'])
def get_messages():
    try:
        # Get all messages from Redis
        messages = redis_client.lrange(QUEUE_NAME, 0, -1)
        return {
            'messages': [json.loads(msg) for msg in messages],
            'count': len(messages)
        }
    except Exception as e:
        return {'error': str(e)}, 500

# Add endpoint to clear messages
@app.route('/api/messages/clear', methods=['POST'])
def clear_messages():
    try:
        redis_client.delete(QUEUE_NAME)
        return {'status': 'success', 'message': 'All messages cleared'}
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/api/send', methods=['POST'])
def send_message():
    try:
        data = request.json
        message = {
            'type': data.get('type', 'message'),
            'content': data.get('content', ''),
            'timestamp': data.get('timestamp', str(datetime.now()))
        }
        
        # Store and print queue info
        redis_client.rpush(QUEUE_NAME, json.dumps(message))
        queue_length = redis_client.llen(QUEUE_NAME)
        print(f"Messages in queue after REST API send: {queue_length}")
        
        # Publish
        redis_client.publish(QUEUE_NAME, json.dumps(message))
        return {'status': 'success', 'message': 'Message sent successfully'}, 200
    except Exception as e:
        print(f"Error in send_message: {e}")
        return {'error': str(e)}, 500

if __name__ == '__main__':
    # Clear any existing messages on startup
    redis_client.delete(QUEUE_NAME)
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)