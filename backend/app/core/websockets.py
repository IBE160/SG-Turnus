import socketio
from starlette.websockets import WebSocket
from fastapi import Depends, HTTPException, status
from urllib.parse import parse_qs
from backend.app.dependencies import get_current_user_websocket
from backend.app.database import get_db
from sqlalchemy.orm import Session

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    query_string = environ.get('QUERY_STRING', '')
    query_params = parse_qs(query_string)
    token = query_params.get('token')

    if not token:
        print(f"Authentication failed for sid {sid}: No token provided.")
        raise ConnectionRefusedError('Authentication token not provided')

    try:
        # Use a generator for get_db and pass it to get_current_user_websocket
        db_generator = get_db()
        db: Session = next(db_generator) # Get the session from the generator

        # get_current_user_websocket expects a token directly, not a header string
        user = await get_current_user_websocket(token[0], db) # token is a list, get the first element
        sio.save_session(sid, {'user_id': str(user.id)}) # Store user_id in session
        sio.enter_room(sid, str(user.id)) # Join a room named after the user ID
        print(f"connect {sid} with user ID {user.id}")
    except HTTPException as e:
        print(f"Authentication failed for sid {sid}: {e.detail}")
        raise ConnectionRefusedError(e.detail)
    except Exception as e:
        print(f"Unexpected error during connection for sid {sid}: {e}")
        raise ConnectionRefusedError('Authentication failed due to unexpected error')
    finally:
        # Ensure the database session is closed
        try:
            db.close()
        except UnboundLocalError:
            pass # db was not assigned if an exception occurred early

@sio.event
async def disconnect(sid):
    print("disconnect ", sid)
    session = await sio.get_session(sid)
    if session and 'user_id' in session:
        user_id = session['user_id']
        sio.leave_room(sid, user_id)
        print(f"User {user_id} left room with sid {sid}")

async def emit_to_user(user_id: str, event: str, data: dict):
    """Emits an event to all sockets in a specific user's room."""
    await sio.emit(event, data, room=str(user_id))
    print(f"Emitted event '{event}' to user {user_id} with data {data}")