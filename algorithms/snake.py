
class Snake(object):
    """This snake class is used to create snake objects to store basic info on
    them. For Samaritan, we can also get an action based on a given board.
    """

    def __init__(self, s_name, s_id, list_of_coords, health, length):
        """Initializes snake object with important instance variables.
        """
        self.name = s_name
        self.id = s_id
        self.coordinates = list_of_coords
        self.health = health
        self.length = length

    def __lt__(self, other):
        return self.length < other.length

    def __str__(self):
        s = "{} health is {}\nSize is {}\nCoordinates are {}".format(self.name,
                                    self.health, self.length, self.coordinates)
        return s

    def get_head(self):
        """Returns head coords of Snake object
        """
        return self.coordinates[0]

    def get_tail(self):
        """Returns tail coords of Snake object
        """
        return self.coordinates[-1]

    def how_long_to_grow(self):
        """
        If the coordinates of the last indices of the snake are the same,
        that means that the snake is still growing out of his tail. This
        function calculates how long it will it take for the tail node to
        disappear
        """
        time_to_disappear = 0
        snake_tail = self.get_tail()
        for snake_node in reversed(self.coordinates[:-1]):
            if snake_node == snake_tail:
                time_to_disappear += 1
        return time_to_disappear

    def coordinates_with_no_repeats(self):
        """Returns a list of coordinates with no repeat nodes e.g. when a snake
        is still growing out of it's tail.
        """
        snake_coordinates = [self.get_head()]
        for node in self.coordinates:
            if node != snake_coordinates[-1]:
                snake_coordinates.append(node)
        return snake_coordinates
