from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

# Track connected clients to /get_data
get_data_clients = set()

# /gun WebSocket endpoint
@socketio.on('message', namespace='/gun')
def handle_gun_message(message):
    print(f"[GUN] Received: {message}")
    
    # Send ACK back to /gun sender
    emit('ack', "ACK: Message received")

    # Broadcast to all /get_data clients
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


# /get_data WebSocket endpoint
@socketio.on('connect', namespace='/get_data')
def on_get_data_connect():
    print(f"[GET_DATA] Connected: {request.sid}")
    get_data_clients.add(request.sid)

@socketio.on('disconnect', namespace='/get_data')
def on_get_data_disconnect():
    print(f"[GET_DATA] Disconnected: {request.sid}")
    get_data_clients.discard(request.sid)


if __name__ == '__main__':
    print("[SERVER] WebSocket server running at ws://0.0.0.0:8080 (paths: /gun, /get_data)")
    socketio.run(app, host='0.0.0.0', port=8080)
