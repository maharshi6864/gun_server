import asyncio
import websockets
import json

# Store clients connected to /get_data
get_data_clients = set()

# Validate incoming WebSocket path
async def process_request(path, request_headers):
    if path not in ["/gun", "/get_data"]:
        return (
            403,
            [("Content-Type", "text/plain")],
            b"Forbidden: Invalid WebSocket path\n"
        )
    return None

# Handle /gun connections
async def gun_handler(websocket):
    print(f"[GUN] Client connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"[GUN] Received message: {message}")

            await websocket.send("ACK: Message received")

            # Broadcast to /get_data
            dead_clients = []
            for client in list(get_data_clients):
                try:
                    await client.send(json.dumps(message))
                    print(f"[GUN] Sent to /get_data: {message}")
                except Exception as e:
                    print(f"[GUN] Failed to send to a /get_data client: {e}")
                    dead_clients.append(client)

            for dc in dead_clients:
                print(f"[GUN] Removing dead /get_data client: {dc.remote_address}")
                get_data_clients.discard(dc)

    except websockets.ConnectionClosed:
        print(f"[GUN] Disconnected: {websocket.remote_address}")


# Handle /get_data connections
async def get_data_handler(websocket):
    print(f"[GET_DATA] Client connected from {websocket.remote_address}")
    get_data_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        print(f"[GET_DATA] Client disconnected: {websocket.remote_address}")
        get_data_clients.discard(websocket)

# Dispatcher
async def handler(websocket, path):
    if path == "/gun":
        await gun_handler(websocket)
    elif path == "/get_data":
        await get_data_handler(websocket)

# Start the server
async def main():
    async with websockets.serve(
        handler,
        "0.0.0.0",
        8080,
        process_request=process_request,
        ping_interval=10,
        ping_timeout=30
    ):
        print("[SERVER] WebSocket server running at ws://0.0.0.0:8080 (paths: /gun, /get_data)")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
