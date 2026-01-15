import re

from flask import session
from flask_socketio import leave_room, close_room
from flask import current_app as app

from errors.InvalidRoomError import InvalidRoomError
from game.Action import Action
from game.Room import Room
from game.room_number import generate_room_id

class Game:
    def __init__(self):
        self.players = []
        self.rooms = []

    def add_player(self, player):
        self.players.append(player)

    def get_player(self, client_id):
        for player in self.players:
            if player.client_id == client_id:
                return player
        return None

    def join_room(self, room_id, client_id):
        if room_id == '' or len(room_id) == 0:
            room_id = generate_room_id()
            app.logger.info("Generated room_id '%s' for client_id '%s'", room_id, client_id)

        player = self.get_player(client_id)

        if player is None:
            raise InvalidRoomError('Invalid player!')

        self.validate_room_id(room_id)

        room = self.get_room(room_id)

        if room is None:
            room = Room(room_id)
            self.rooms.append(room)

        room.add_player(player)
        session['room_id'] = room_id
        return room

    def get_room(self, room_id):
        for room in self.rooms:
            if room.room_id == room_id:
                return room
        return None

    def get_room_ids(self):
        return [room.room_id for room in self.rooms]

    def leave_room(self, room_id, client_id):
        for room in self.rooms:
            if room.room_id == room_id:
                player = self.get_player(client_id)
                room.remove_player(player)
                leave_room(room_id)
                if room.is_empty():
                    close_room(room_id)
                self.rooms.remove(room)
                self.players.remove(player)

    def play_action(self, room_id, client_id, action):
        room = self.get_room(room_id)
        player = self.get_player(client_id)

        if room is None:
            raise InvalidRoomError('Invalid room!')

        room.play(Action(player, action))

    def result(self, room_id):
        room = self.get_room(room_id)
        if room is None:
            raise InvalidRoomError('Invalid room!')
        return room.get_result()

    @staticmethod
    def validate_room_id(room_id):
        if room_id == '' or len(room_id) == 0:
            raise InvalidRoomError(room_id)
        if re.search(r'^\d{3}-\d{3}$', room_id) is None:
            raise InvalidRoomError(room_id)