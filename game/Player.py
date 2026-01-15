from flask import session


class Player:
    def __init__(self, username, client_id):
        self.username = username
        self.client_id = client_id
        self.to_session()

    def __str__(self):
        return f"Player(username='{self.username}', client_id='{self.client_id}')"

    def to_session(self):
        session['username'] = self.username
