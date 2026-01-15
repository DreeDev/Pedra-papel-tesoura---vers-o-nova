import eventlet
eventlet.monkey_patch()

from threading import Lock
from flask import Flask, session, request, render_template
from flask_socketio import SocketIO, emit
from game.Game import Game
from game.Player import Player
from errors.InvalidRoomError import InvalidRoomError
from errors.FullRoomError import FullRoomError
from game.usernames import generate_random_username
from config.logger import setup_logging

thread = None
thread_lock = Lock()

setup_logging()

app = Flask(__name__)
logger = app.logger
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

app_game = Game()

def background_thread():
    while True:
        socketio.sleep(3)
        for room_id in app_game.get_room_ids():
            room = app_game.get_room(room_id)
            result = app_game.result(room_id)
            is_ready = room.is_playable()

            player_1, player_2 = '', ''

            if len(room.players) == 2:
                player_1, player_2 = room.players[0].username, room.players[1].username
            elif len(room.players) == 1:
                player_1 = room.players[0].username

            socketio.emit('game_ready',
                          {'roomId': room_id, 'ready': is_ready, 'match': result, 'player1': player_1, 'player2': player_2},
                        to=room_id)

            logger.info(f"Updating ... client room '{room_id}'")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.event
def connect():
    player = Player(generate_random_username(), request.sid)
    app_game.add_player(player)
    logger.info(f"Client connecting with username '{player.username}' for sid '{player.client_id}'")

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

    emit('connect_response', {'username': player.username})
@socketio.event
def connected():
    logger.info(f"Client connected with username '{session['username']}' for client_id '{request.sid}'")

@socketio.event
def start_game(message):
    room_id = message['roomId']
    client_id = request.sid

    try:
        room = app_game.join_room(room_id, client_id)
        logger.info(f"Client starting game '{room.room_id}' with username '{session['username']}' for client_id '{client_id}'")
        emit('start_game_response', {'roomId': room.room_id})
    except InvalidRoomError as e:
        logger.error('Room %s is invalid', e.room_id)
        emit('start_game_response', {'error':'invalid'})
    except FullRoomError as e:
        logger.error("Room '%s' is full", e.room_id)
        emit('start_game_response', {'error': 'full'})

@socketio.event
def play_action(message):
    username = session['username']
    room_id = session['room_id']
    action = message['action']
    app_game.play_action(room_id=room_id, client_id=request.sid, action=action)

    emit('play_action_response',
         {'action': action, 'username': username},
         to=room_id,
         broadcast=True)

@socketio.on('disconnect')
def do_disconnect(reason):
    app_game.leave_room(session['room_id'], request.sid)
    session['username'] = None
    session['room_id'] = None
    logger.info('Client disconnected %s %s', request.sid, reason)

if __name__ == '__main__':
    socketio.run(app)
