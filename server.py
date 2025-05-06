import os
import eventlet
eventlet.monkey_patch()
from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

get_data_clients = set()

# --- HTTP route for health check ---
@app.route('/')
def health_check():
    return "✅ WebSocket server is up and running!", 200

# --- WebSocket: /gun ---
@socketio.on('message', namespace='/gun')
def handle_gun_message(message):
    print(f"[GUN] Received: {message}")
    emit('ack', "ACK: Message received")

    for sid in list(get_data_clients):
        try:
            socketio.emit('gun_data', message, namespace='/get_data', to=sid)
            print(f"[GUN] Relayed to /get_data: {sid}")
        except Exception as e:
            print(f"[GUN] Failed to send to {sid}: {e}")
            get_data_clients.discard(sid)

@socketio.on('connect', namespace='/gun')
def on_gun_connect():
    print(f"[GUN] Connected: {request.sid}")

@socketio.on('disconnect', namespace='/gun')
def on_gun_disconnect():
    print(f"[GUN] Disconnected: {request.sid}")

# --- WebSocket: /get_data ---
@socketio.on('connect', namespace='/get_data')
def on_get_data_connect():
    print(f"[GET_DATA] Connected: {request.sid}")
    get_data_clients.add(request.sid)

@socketio.on('disconnect', namespace='/get_data')
def on_get_data_disconnect():
    print(f"[GET_DATA] Disconnected: {request.sid}")
    get_data_clients.discard(request.sid)

# --- Main Entry ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"[SERVER] WebSocket server running at ws://0.0.0.0:{port} (paths: /gun, /get_data)")
    socketio.run(app, host='0.0.0.0', port=port)
