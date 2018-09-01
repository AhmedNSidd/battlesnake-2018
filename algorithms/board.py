from snake import Snake
from constants import *
from utils import get_manhattan_distance

class Board(object):
    def __init__(self, data):
        self.width = data['width'] # set the width of game board
        self.height = data['height'] # set the height of game board
        # create a 2d array which represents the game board
        self.grid = [[EMPTY_SPACE_MAKERS for x in range(0, self.width)] for y in range(0, self.height)]
        self.foods = self._parse_data_list(data['food']['data'])
        self.my_snake = self._parse_snake_object(data['you'])
        # Creates a list of other snakes (enemies)
        self.other_snakes = [self._parse_snake_object(snake) for snake in data['snakes']['data'] if not self.my_snake.id != snake['id']]
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
        return Snake(id, coords, health, length)

    def _mark_grid(self):
        # Marking my own snake.
        for x, y in self.my_snake.coordinates[1:]:
            self.grid[y][x] = SNAKE_BODY_MARKER

        x, y = self.my_snake.coordinates[0]
        self.grid[y][x] = SNAKE_HEAD_MARKER

        # Marking other snakes
        for other_snake in self.other_snakes:
            for x, y in other_snake.coordinates[1:]:
                self.grid[y][x] = SNAKE_BODY_MARKER

            x, y = other_snake.coordinates[0]
            self.grid[y][x] = SNAKE_HEAD_MARKER

        # Marking foods
        for x, y in self.foods:
            self.grid[y][x] = FOOD_MARKER

    def print_grid(self):
        for row in self.grid:
            for point in row:
                print point,
            print

    # this method is gonna get the neighbours of the node in the parameter and put it in a list of tuples, i will
    # make another method that will check whether the coordinate is valid by: a) Making sure the value around it isnt -1
    # and b) making sure it's in the grid e.g. [(2,1), (2,0), (1,0)]
    def get_surrounding_coords(self, node):
        xcoord, ycoord = node
        return [(xcoord + 1, ycoord), (xcoord - 1, ycoord), (xcoord, ycoord + 1), (xcoord, ycoord - 1)]

    def get_neighbours(self, node):
        xcoord, ycoord = node
        neighbours = [(xcoord + 1, ycoord), (xcoord - 1, ycoord), (xcoord, ycoord + 1), (xcoord, ycoord - 1)]
        return [(i, j) for i, j in neighbours if self.is_valid_coordinate(i, j)]

    def is_valid_coordinate(self, xcoord, ycoord):
        return -1 < xcoord < self.width and -1 < ycoord < self.height and self.grid[ycoord][xcoord] != SNAKE_BODY_MARKER and self.grid[ycoord][xcoord] != SNAKE_HEAD_MARKER

        # this method will recieve a node and it will check if there is a snake on that grid, if it does have a snake
        # it will check its length, it will also see if the tail of the snake is there, it will
    def get_cost(self, node):
        #1st check if there's a snake head on the node
        cost = 1
        # xcoord, ycoord = node
        # if self.grid[ycoord][xcoord] == SNAKE_BIG_HEAD_MARKER:
        #     cost = cost + 5
        # elif self.grid[ycoord][xcoord] == SNAKE_SMALL_HEAD_MARKER:
        #     cost = cost + 2
        # # second case: checks if theres a snake head around the node
        # for xcoord_neighbour, ycoord_neighbour in self.get_surrounding_coords(node):
        #     if -1 < xcoord_neighbour < self.width and -1 < ycoord_neighbour < self.height:
        #         if self.grid[ycoord_neighbour][xcoord_neighbour] == SNAKE_BIG_HEAD_MARKER:
        #             cost = cost + 14
        #
        #         elif self.grid[ycoord_neighbour][xcoord_neighbour] == FOOD_MARKER:
        #             #calculate manhattan distance of all snakes on the Board
        #             #find lowest one
        #             smallest_distance = min([get_manhattan_distance(snake.get_head(), (xcoord_neighbour, ycoord_neighbour)) for snake in self.snakes if snake.id != self.self_snake.id])
        #             if get_manhattan_distance(self.self_snake.get_head(), (xcoord_neighbour, ycoord_neighbour)) > smallest_distance:
        #                 cost = cost + 2
        #     else:
        #         cost = cost + 2

        return cost


        '''
        on small snakes head
        on large snakes
        around small snakes head
        around large snakes head


        around food if snake with low health is close
        around walls

        '''
