from copy import deepcopy
from .utils import translate, generate_data_dictionary
from .constants import FOOD_MARKER
from .board import Board

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
