from flask_socketio import join_room
from errors.FullRoomError import FullRoomError

class Room:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = []
        self.actions = []

    def __str__(self):
        return f"Player(Room='{self.room_id}', players='{len(self.players)}')"

    def add_player(self, player):
        if player.username in self.players:
            print(f"Player '{player.username}' is already playing.")
            return

        if self.is_full():
            raise FullRoomError(self.room_id)

        self.players.append(player)
        join_room(self.room_id)

    def remove_player(self, player):
        self.players.remove(player)
        self.clean_actions(player)

    def clean_actions(self, player):
        self.actions = [action for action in self.actions if action.player.username != player.username]

    def is_full(self):
        return len(self.players) == 2

    def is_empty(self):
        return len(self.players) == 0

    def is_playable(self):
        return len(self.players) == 2

    def play(self, action):
        self.actions.append(action)

    def get_result(self):
        if len(self.actions) < 2:
            return {}

        if len(self.actions) > 2:
            raise RuntimeError("Too many actions!")

        action1, action2 = self.actions

        if action1.action == action2.action:
            return {'result': 'tie'}
        elif action1.action == 'rock' and action2.action == 'scissor':
            return {'result': 'won', 'username': action1.player.username}
        elif action1.action == 'scissor' and action2.action == 'paper':
            return {'result': 'won', 'username': action1.player.username}
        elif action1.action == 'paper' and action2.action == 'rock':
            return {'result': 'won', 'username': action1.player.username}
        elif action2.action == 'rock' and action1.action == 'scissor':
            return {'result': 'won', 'username': action2.player.username}
        elif action2.action == 'scissor' and action1.action == 'paper':
            return {'result': 'won', 'username': action2.player.username}
        elif action2.action == 'paper' and action1.action == 'rock':
            return {'result': 'won', 'username': action2.player.username}
        return {}