import random

def generate_room_id():
    return str(random.randint(100, 999)) + '-' + str(random.randint(100, 999))