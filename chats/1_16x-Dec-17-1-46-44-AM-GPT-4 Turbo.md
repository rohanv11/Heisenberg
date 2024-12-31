User:
You are tasked to answer a question:

I have currently made a repo using fast api and socket io for a online game i am making.
This server will handle rooms, and people in rooms.
Its a online turn based game. (you can consider a monopoly like game)
Each user must be able to create a room. Each room will have a 6 digit unique room code.
Room can be private or public.
Public rooms can be listed in a rooms api. So other users can join.
One room size can be from at most 5 players.
Users should be able to join the room and leave the room.

I have done some part already, please refer to it and update accordingly

Use Python 3.10 syntax.

Prefer list comprehensions and f-strings.

Instructions for the output format:
- Output code without descriptions, unless it is important.
- Minimize prose, comments and empty lines.
- Only show the relevant code that needs to be modified. Use comments to represent the parts that are not modified.
- Make it easy to copy and paste.
- Consider other possibilities to achieve the result, do not be limited by the prompt.
- Make sure low level design is taken care of. Use SOLID principles and appropriate design patterns.

main.py
```py
from fastapi import FastAPI
from socketio import ASGIApp
from app.socket_manager import sio
from .routers import room

app = FastAPI()

def include_routers(app):
    app.include_router(room.router)

include_routers(app)

socket_app = ASGIApp(sio, other_asgi_app=app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
```

routers/room.py
```py
from fastapi import APIRouter

router = APIRouter()

@router.get("/rooms")
def get_rooms():
    """Get all available rooms."""
    from ..socket_manager import rooms
    return {"rooms": list(rooms.keys())}
```

socket_manager.py
```py
import socketio

sio = socketio.AsyncServer(async_mode="asgi")

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
```

Assistant:
Here's the updated code with improved functionality and structural adjustments. Key improvements include room code generation, public/private room distinction, and handling join conditions:

### main.py
```py
from fastapi import FastAPI
from socketio import ASGIApp
from app.socket_manager import sio
from .routers import room

app = FastAPI()

def include_routers(app):
    app.include_router(room.router)

include_routers(app)

socket_app = ASGIApp(sio, other_asgi_app=app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
```

### routers/room.py
```py
from fastapi import APIRouter

router = APIRouter()

@router.get("/rooms")
def get_rooms():
    from ..socket_manager import rooms
    public_rooms = {code: details for code, details in rooms.items() if details['public']}
    return {"rooms": list(public_rooms.keys())}
```

### socket_manager.py
```py
import socketio
import string
import random

sio = socketio.AsyncServer(async_mode="asgi")

rooms = {}

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
```

Key enhancements include:
- Unique room code handling through a function that generates 6-digit alphanumeric codes.
- Creation and management of private and public rooms.
- Defined join room event to append members.
- Condition checks to prevent joining a full room or not existing rooms.
- Automatic deletion of rooms with no members.