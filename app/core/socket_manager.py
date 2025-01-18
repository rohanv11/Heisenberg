import socketio
import string
import random

# Initialize Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi")

# Room management logic
rooms = {}

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit("message", {"data": "Welcome to the server!"}, to=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    for code, details in list(rooms.items()):
        if sid in details['members']:
            details['members'].remove(sid)
            if len(details['members']) == 0:
                del rooms[code]
            await sio.emit("room_update", {"room": code, "members": details['members']}, room=code)

@sio.event
async def create_room(sid, public=True):
    room_code = generate_room_code()
    while room_code in rooms:
        room_code = generate_room_code()
    rooms[room_code] = {'members': [sid], 'public': public}
    sio.enter_room(sid, room_code)
    print(f"{sid} created and joined room: {room_code}")
    await sio.emit("room_update", {"room": room_code, "members": rooms[room_code]['members']}, room=room_code)

@sio.event
async def join_room(sid, room_code):
    if room_code in rooms and len(rooms[room_code]['members']) < 5:
        rooms[room_code]['members'].append(sid)
        sio.enter_room(sid, room_code)
        print(f"{sid} joined room: {room_code}")
        await sio.emit("room_update", {"room": room_code, "members": rooms[room_code]['members']}, room=room_code)

@sio.event
async def leave_room(sid, room_code):
    if room_code in rooms and sid in rooms[room_code]['members']:
        rooms[room_code]['members'].remove(sid)
        sio.leave_room(sid, room_code)
        print(f"{sid} left room: {room_code}")
        await sio.emit("room_update", {"room": room_code, "members": rooms[room_code]['members']}, room=room_code)
