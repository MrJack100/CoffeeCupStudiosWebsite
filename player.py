class Player:
    def __init__(self, name):
        self.name = name
        self.coordinates = {
            "x": None,
            "y": None,
            "z": None
        }
        self.tags = []
        self.last_seen_timestamp = 0
        self.fail_counter = 0
        self.last_logged_fail_counter = 0