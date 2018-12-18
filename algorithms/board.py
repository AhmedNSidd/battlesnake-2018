import snake
from constants import *
from utils import get_manhattan_distance

class Board(object):
    def __init__(self, data):
        self.data = data
        self.width = data['width'] # set the width of game board
        self.height = data['height'] # set the height of game board
        # create a 2d array which represents the game board
        self.grid = [[EMPTY_SPACE_MAKERS for x in range(0, self.width)] for y in range(0, self.height)]
        self.foods = self._parse_data_list(data['food']['data']) # a list of tuple coordinates of all foods.
        self.my_snake = self._parse_snake_object(data['you'])
        # Creates a list of other snakes (enemies)
        self.other_snakes = [self._parse_snake_object(snake) for snake in data['snakes']['data'] if self.my_snake.id != snake['id']]
        self._mark_grid()
        self.print_grid()

    # Recieves a list of JSON objects and returns a list of tuples with points
    def _parse_data_list(self, data_list):
        return [(point['x'], point['y']) for point in data_list]

    # Returns a snake object given the JSON object from the API
    def _parse_snake_object(self, snake_object):
        id = snake_object['id']
        coords = self._parse_data_list(snake_object['body']['data'])
        length = snake_object['length']
        health = snake_object['health']
        return snake.Snake(id, coords, health, length)

    def _mark_grid(self):
        # Marking my own snake.
        for x, y in self.my_snake.coordinates[1:-1]:
            self.grid[y][x] = SAMARITAN_BODY_MARKER

        x, y = self.my_snake.coordinates[0]
        self.grid[y][x] = SAMARITAN_HEAD_MARKER

        x, y = self.my_snake.coordinates[-1]
        if self.my_snake.health == 100 or self.my_snake.length <=3:
            self.grid[y][x] = SAMARITAN_BODY_MARKER
        else:
            self.grid[y][x] = SNAKE_TAIL_MARKER


        # Marking other snakes
        for other_snake in self.other_snakes:
            #currently registers enemy tails as a wall.
            for x, y in other_snake.coordinates[1:-1]:
                self.grid[y][x] = ENEMY_SNAKE_BODY_MARKER

            x, y = other_snake.coordinates[0]
            self.grid[y][x] = ENEMY_SNAKE_HEAD_MARKER

            x, y = other_snake.coordinates[-1]
            if other_snake.health == 100 or other_snake.length <= 3:
                self.grid[y][x] = SAMARITAN_BODY_MARKER
            else:
                self.grid[y][x] = SNAKE_TAIL_MARKER

        # Marking foods
        for x, y in self.foods:
            self.grid[y][x] = FOOD_MARKER

    def print_grid(self):
        for row in self.grid:
            for point in row:
                print point,
            print
        print
        print

    def get_neighbours(self, node):
        xcoord, ycoord = node
        neighbours = [(xcoord + 1, ycoord), (xcoord - 1, ycoord), (xcoord, ycoord + 1), (xcoord, ycoord - 1)]
        return [(i, j) for i, j in neighbours if self.is_valid_coordinate(i, j)]

    # If the x and y coords are in the board, and the coords don't contain any snake's body or head, return true. else, false
    def is_valid_coordinate(self, xcoord, ycoord):
        node_in_board = -1 < xcoord < self.width and -1 < ycoord < self.height # a boolean telling us whether our node is in the board.
        if not node_in_board:
            return False
        node_emptiness = (self.grid[ycoord][xcoord] != SAMARITAN_BODY_MARKER and self.grid[ycoord][xcoord] != ENEMY_SNAKE_BODY_MARKER) and (self.grid[ycoord][xcoord] != SAMARITAN_HEAD_MARKER and self.grid[ycoord][xcoord] != ENEMY_SNAKE_HEAD_MARKER) # boolean telling us if the node is empty
        distance_to_node = get_manhattan_distance(self.my_snake.get_head(), (xcoord, ycoord))
        if not node_emptiness: # if the node isn't empty, check if it's going to be empty.
            if (xcoord, ycoord) in self.my_snake.coordinates:
                time_to_disapper = 1 if self.my_snake.health == 100 else 0
                for my_snakes_node in reversed(self.my_snake.coordinates[1:]):
                    time_to_disapper = time_to_disapper + 1
                    if my_snakes_node == (xcoord, ycoord):
                        break
                if time_to_disapper <= distance_to_node:
                    node_emptiness = True

        return node_in_board and node_emptiness

    def get_cost(self, node):
        cost = 1
        xcoord, ycoord = node
        if xcoord == 19 or ycoord == 19 or xcoord == 0 or ycoord == 0:
            cost+=3
            if (xcoord == 19 and ycoord == 19) or (xcoord == 19 and ycoord == 0) or (xcoord == 0 and ycoord == 19) or (xcoord == 0 and ycoord == 0):
                cost+=5
            else:
                # not a diagonal node
                if xcoord == 19 and (self.grid[ycoord][xcoord-1] == ENEMY_SNAKE_HEAD_MARKER or self.grid[ycoord][xcoord-1] == ENEMY_SNAKE_BODY_MARKER):
                    cost += 10 # maybe change this and others to 999?
                elif ycoord == 19 and (self.grid[ycoord-1][xcoord] == ENEMY_SNAKE_HEAD_MARKER or self.grid[ycoord-1][xcoord] == ENEMY_SNAKE_BODY_MARKER):
                    cost += 10
                elif xcoord == 0 and (self.grid[ycoord][xcoord+1] == ENEMY_SNAKE_HEAD_MARKER or self.grid[ycoord][xcoord+1] == ENEMY_SNAKE_BODY_MARKER):
                    cost += 10
                elif ycoord == 0 and (self.grid[ycoord+1][xcoord] == ENEMY_SNAKE_HEAD_MARKER or self.grid[ycoord+1][xcoord] == ENEMY_SNAKE_BODY_MARKER):
                    cost += 10
        # steps_to_food = get_manhattan_distance(self.my_snake.get_head(), node)
        return cost
