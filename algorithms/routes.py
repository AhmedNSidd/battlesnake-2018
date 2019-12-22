
from .utils import get_manhattan_distance, translate
from heapq import heappush, heappop
from .graph_algorithms import a_star, bfs
from copy import deepcopy
from .board import Board, generate_new_board_with_path
from .constants import EMPTY_SPACE_MAKERS


def find_path_to_my_tail(board):
    """A* algorithm used by my snake to find a path to his tail, but
    makes sure we go near the center first.
    """
    cost_of_tail, path_to_tail = a_star(board, board.my_snake.get_head(),
                                        board.my_snake.get_tail(),
                                        board.my_snake)

    if path_to_tail == None or len(path_to_tail) == 1:
        return (None, None)
    return ("Going To My Tail", translate(board.my_snake.get_head(),
                        path_to_tail[1]))

def path_to_tail_exists(board):
    """Checks to see if our tail is reachable given a board.
    """
    return bfs(board, board.my_snake.get_head(), board.my_snake.get_tail(), 
               board.my_snake)

def can_go_to_tail_after_moves(board, path):
    """
    This function tells us whether a path to our tail exists after certain
    moves have been made.
    """
    return path_to_tail_exists(generate_new_board_with_path(board, path))

def sp_find_path_to_food(board):
    """This function is used for our singleplayer snake to find food.
    """
    result = (999999, "") # result[0] = length, result[1] = move
    for food in board.foods:
        cost, path = a_star(board, board.my_snake.get_head(), food, 
                          board.my_snake)
        move = translate(board.my_snake.get_head(), path[1])
        if (len(path) - 1) < result[0] and can_go_to_tail_after_moves(board,
                                                                     path[1:]):
            result = (len(path) - 1, move)

    if result[0] > board.my_snake.health:
        return (None, None)

    if not result[1]:
        return (None, None)
    return ("Going to Closest Food", result[1])


def is_death_guranteed(board, snake):
    """
    Checks if death is guranteed for our snake in the given board.
    """
    starvation_guranteed = True
    potential_foods = []
    for food in board.foods:
        min_distance = get_manhattan_distance(snake.get_head(), food)
        if min_distance <= snake.health:
            potential_foods.append(food)
    for food in potential_foods:
        cost, path = a_star(board, snake.get_head(), food, snake)
        if len(path) - 1 <= snake.health:
            starvation_guranteed = False
            break
    if starvation_guranteed:
        return True
    
    return False
    