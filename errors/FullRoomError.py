class FullRoomError(BaseException):
    def __init__(self, room_id, message="Room_id is full"):
        self.room_id = room_id
        super().__init__(f"{message}: {self.room_id}")