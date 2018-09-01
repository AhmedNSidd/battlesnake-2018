from pathfinding import a_star

class Snake(object):
    def __init__(self, s_id, list_of_coords, health, length): # e.g list_of_coords = [(2,3), (3,4), etc.]
        self.id = s_id
        self.coordinates = list_of_coords
        self.health = health
        self.length = length

    def get_head(self):
        return self.coordinates[0]
