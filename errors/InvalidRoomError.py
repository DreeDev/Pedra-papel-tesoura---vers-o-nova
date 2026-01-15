class InvalidRoomError(BaseException):
    def __init__(self, room_id, message="Room_id not valid"):
        self.room_id = room_id
        super().__init__(f"{message}: {self.room_id}")