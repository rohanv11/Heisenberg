import socketio

# Initialize Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi")

# Room management logic
rooms = {}

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit("message", {"data": "Welcome to the server!"}, to=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    for room, members in rooms.items():
        if sid in members:
            members.remove(sid)
            await sio.emit("room_update", {"room": room, "members": members}, room=room)

@sio.event
async def create_room(sid, room_name):
    if room_name not in rooms:
        rooms[room_name] = []
    rooms[room_name].append(sid)
    sio.enter_room(sid, room_name)
    print(f"{sid} joined room: {room_name}")
    await sio.emit("room_update", {"room": room_name, "members": rooms[room_name]}, room=room_name)

@sio.event
async def leave_room(sid, room_name):
    if room_name in rooms and sid in rooms[room_name]:
        rooms[room_name].remove(sid)
        sio.leave_room(sid, room_name)
        print(f"{sid} left room: {room_name}")
        await sio.emit("room_update", {"room": room_name, "members": rooms[room_name]}, room=room_name)
