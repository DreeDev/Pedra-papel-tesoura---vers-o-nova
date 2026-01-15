import random

def generate_random_username():
    adjectives = ["rapido", "veloz", "mistico", "silencioso", "forte", "antigo", "novo", "queimado", "solitario", "quente", "frio"]
    nouns = ["passaro", "tamandua", "cavalo", "dragao", "escorpiao", "mostiquito", "leao", "peixe", "tubarao", "pastel", "cachorro", "gato"]

    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    number = random.randint(10, 99)

    return f"{noun}{adjective}{number}"