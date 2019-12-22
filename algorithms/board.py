from .snake import EnemySnake, MySnake
from .constants import *
from .utils import translate, generate_data_dictionary
from copy import deepcopy

DEBUG = True

class Board(object):
    """
    This board class is used to display the game state when the game server is
    requesting a move.
    """
    def __init__(self, data):
        """
        This function receives board information such as width and height and
        creates an empty grid to fill out once we recieve more information.
        """
        self.data = data
        self.width = data["board"]["width"]
        self.height = data["board"]["height"]
        self.grid = []
        self.foods = self._parse_data_list(data["board"]["food"])
        self.my_snake = self._parse_snake_object(data["you"], 0)
        self.other_snakes = [self._parse_snake_object(snake, 1)
                             for snake in data["board"]["snakes"]
                             if self.my_snake.id != snake["id"]]
        if DEBUG:
            for snake in self.other_snakes:
                print(snake)
        self._mark_grid()
        if DEBUG:
            self.print_grid()


    def _parse_data_list(self, data_list):
        """
        Recieves a list of JSON objects and returns a list of tuples of x,y
        coordinates
        """
        return [(point["x"], point["y"]) for point in data_list]


    def _parse_snake_object(self, snake_object, type):
        """
        Returns a snake object given the JSON object from the API
        Type is 0 if it's my snake or 1 if it's enemy snake
        """
        name = snake_object["name"]
        id = snake_object["id"]
        coords = self._parse_data_list(snake_object["body"])
        length = len(coords)
        health = snake_object["health"]
        if type:
            return EnemySnake(name, id, coords, health, length)
        else:
            return MySnake(name, id, coords, health, length)

    def _mark_grid(self):
        """
        This method marks the entire grid with my snake, enemy snakes, foods,
        and empty spaces
        """
        for row in range(self.height):
            self.grid.append([EMPTY_SPACE_MAKERS for col in range(self.width)])

        for x, y in self.my_snake.coordinates[1:-1]:
            self.grid[y][x] = MY_SNAKE_BODY_MARKER

        x, y = self.my_snake.coordinates[0]
        self.grid[y][x] = MY_SNAKE_HEAD_MARKER

        x, y = self.my_snake.coordinates[-1]
        self.grid[y][x] = SNAKE_TAIL_MARKER

        for other_snake in self.other_snakes:
            for x, y in other_snake.coordinates[1:-1]:
                self.grid[y][x] = ENEMY_SNAKE_BODY_MARKER

            x, y = other_snake.coordinates[0]
            self.grid[y][x] = ENEMY_SNAKE_HEAD_MARKER

            x, y = other_snake.coordinates[-1]
            self.grid[y][x] = SNAKE_TAIL_MARKER

        for x, y in self.foods:
            self.grid[y][x] = FOOD_MARKER

    def print_grid(self):
        """A method that prints the grid.
        """
        for row in self.grid:
            for point in row:
                print(point, end=" ")
            print()
        print()

    def get_all_snakes(self):
        """A method that returns all snake objects on the board.
        """
        return self.other_snakes + [self.my_snake]

    def is_my_snake_biggest(self):
        """
        Returns a boolean telling us whether my snake is the biggest snake
        on the board.
        """
        for snake in self.other_snakes:
            if snake.length >= self.my_snake.length:
                return False
        return True

    def get_simple_neighbours(self, node):
        """
        Return a list of neighbours of a node regardless of whether they are
        valid or not.
        """
        xcoord, ycoord = node
        return [
            (xcoord + 1, ycoord), (xcoord - 1, ycoord),
            (xcoord, ycoord + 1), (xcoord, ycoord - 1)
            ]


    def get_valid_neighbours(self, node, snake, distance_to_neighbour_nodes=1,
                       foods_in_path=0):
        """
        Return a list of neighbours of a node if they are valid coordinates
        that my snake can go to.
        Parameters:
        node: necessary to get the neighbours around a node.
        snake: Necessary to get the distance from the snake's head to the
        neighbouring node. If the distance is greater than the time it'll take
        to get to the node from the snake's head, then it's a valid neighbour.
        distance_to_neighbour_nodes: Helps with calculating the distance to the
        neighboring nodes since calculating the manhattan distance doesn't
        always give us a true distance.
        foods_in_path: If there is > 0 food in our path, this will increase the
        time to disappear for non-empty nodes that are in my snake's path
        """
        xcoord, ycoord = node
        neighbours = [
            (xcoord + 1, ycoord), (xcoord - 1, ycoord),
            (xcoord, ycoord + 1), (xcoord, ycoord - 1)
            ]
        return [(i, j)
                for i, j in neighbours
                if self.is_valid_coordinate(i, j, snake,
                                            distance_to_neighbour_nodes,
                                            foods_in_path)]

    def is_valid_coordinate(self, xcoord, ycoord, snake, distance_to_node,
                            foods_in_path=0):
        """
        Check if a node is a valid node that my snake can go to without
        dying i.e., it's not out of the board, and if it's a wall, it won't be
        a wall by the time I get to it.
        """
        node = (xcoord, ycoord)
        if not (-1 < xcoord < self.width and -1 < ycoord < self.height):
            return False
        node_empty = (self.grid[ycoord][xcoord] == FOOD_MARKER or
                      self.grid[ycoord][xcoord] == EMPTY_SPACE_MAKERS)
        if node_empty:
            return True
        for snake in self.get_all_snakes():
            if node in snake.coordinates:
                time_to_disappear = snake.how_long_to_grow()
                time_to_disappear += foods_in_path
                snake_coordinates = snake.coordinates_with_no_repeats()
                for snakes_node in reversed(snake_coordinates):
                    time_to_disappear += 1
                    if snakes_node == node:
                        break
                if time_to_disappear <= distance_to_node:
                    node_empty = True

        return node_empty

    def get_cost(self, node, my_snake, distance_to_node, foods_in_path):
        """
        Calculates the cost to travel to the node in the parameter depending on
        from which snake's perspective we are looking at it from.

        Costs are rated from a scale of 1-10 with the only exception being if
        we have predetermined that it's a bad move through paranoid algorithms
        """
        xcoord, ycoord = node
        cost = 1
        # for snake in self.get_all_snakes():
        #     if snake != my_snake:
        #         if snake.length >= my_snake.length:
        #             enemy_neighbours = self.get_valid_neighbours(snake.get_head(),
        #                                                    snake)
        #             for x, y in enemy_neighbours:
        #                 trajectory = translate(snake.get_head(), (x, y))
        #                 if (trajectory == "down" and (node == (x-1, y+1) or
        #                     node == (x+1, y+1))):
        #                     if snake.length > my_snake.length:
        #                         cost += 3
        #                     else:
        #                         cost += 1
        #                 elif (trajectory == "up" and (node == (x-1, y-1) or
        #                     node == (x+1, y-1))):
        #                     if snake.length > my_snake.length:
        #                         cost += 3
        #                     else:
        #                         cost += 1
        #                 elif (trajectory == "left" and (node == (x-1, y-1) or
        #                     node == (x-1, y+1))):
        #                     if snake.length > my_snake.length:
        #                         cost += 3
        #                     else:
        #                         cost += 1
        #                 elif (trajectory == "right" and (node == (x+1, y-1) or
        #                     node == (x+1, y+1))):
        #                     if snake.length > my_snake.length:
        #                         cost += 3
        #                     else:
        #                         cost += 1
        # valid_neighbours = self.get_valid_neighbours(node, my_snake, distance_to_node,
        #                                        foods_in_path)
        # for snake in self.other_snakes:
        #     if (snake.get_head() in valid_neighbours
        #         and snake.length > my_snake.length):
        #         cost += 6
        # if (xcoord == (self.width-1) or ycoord == (self.height-1) or xcoord == 0
        #     or ycoord == 0): # node is on the edges
        #     cost += 1
        return cost


def generate_new_board_with_move(board, move):
    """This function generates a new board for our snake given a move.
    """
    food_coordinates = board.foods[:]
    other_snakes = deepcopy(board.other_snakes)
    my_snake = deepcopy(board.my_snake)
    next_node_x, next_node_y = my_snake.get_head()[0], my_snake.get_head()[1]
    if move == "left":
        next_node_x -= 1
    elif move == "right":
        next_node_x += 1
    elif move == "up":
        next_node_y -= 1
    elif move == "down":
        next_node_y += 1
    my_snake.coordinates.pop()
    my_snake.coordinates.insert(0, (next_node_x, next_node_y))
    my_snake.health -= 1
    if board.grid[next_node_y][next_node_x] == FOOD_MARKER:
        food_coordinates.remove((next_node_x, next_node_y))
        my_snake.length += 1
        my_snake.health = 100
        my_snake.coordinates.append(my_snake.coordinates[-1])
    return Board(generate_data_dictionary(board, food_coordinates,
                                          other_snakes, my_snake))

def generate_new_board_with_path(board, path):
    """This function generates a new board given a path.
    """
    curr_board = board
    for node in path:
        move = translate(curr_board.my_snake.get_head(), node)
        curr_board = generate_new_board_with_move(curr_board, move)
    return curr_board
