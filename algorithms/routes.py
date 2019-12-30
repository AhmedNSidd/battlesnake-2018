
from .utils import get_manhattan_distance, translate
from heapq import heappush, heappop
from .graph_algorithms import a_star, bfs, battlestar
from copy import deepcopy
from .board import Board
from .generators import generate_new_board_with_path
from .constants import EMPTY_SPACE_MAKERS
from collections import deque


#### SINGLEPLAYER ALGORITHMS #####

def sp_find_path_to_food(board):
    """This function is used for our singleplayer snake to find food.
    """
    result = (999999, "") # result[0] = length, result[1] = move
    for food in board.foods:
        cost, path = a_star(board, board.my_snake.get_head(), food, board.my_snake)
        if cost != None:
            move = translate(board.my_snake.get_head(), path[1])
            if (len(path) - 1) < result[0] and can_go_to_tail_after_moves(
                                                            board, path[1:]):
                result = (len(path) - 1, move)

    if result[0] > board.my_snake.health or not result[1]:
        return (None, None)

    return ("Going to Closest Food", result[1])

def sp_path_to_tail(board):
    """
    A single player method to go to tail.
    """
    cost, path = battlestar(board, board.my_snake.get_head(),
                            board.my_snake.get_tail())
    if cost is None:
        return (None, None)
    return ("Going To My Tail", translate(board.my_snake.get_head(), path[1]))


#### MULTIPLAYER ALGORITHMS #####

def find_path_to_my_tail(board):
    """A* algorithm used by my snake to find a path to his tail, but
    makes sure we go near the center first.
    """
    cost_of_tail, path_to_tail = a_star(board, board.my_snake.get_head(),
                                        board.my_snake.get_tail(), board.my_snake)

    if path_to_tail == None or len(path_to_tail) == 1:
        return (None, None)
    return ("Going To My Tail", translate(board.my_snake.get_head(),
                        path_to_tail[1]))

def go_to_least_dense_region(board):
    """
    This is used by our snake to find a path to the least dense region on the
    board.
    """
    grid = [[0] + ([0] * (board.width - 2)) + [0]]
    for x in range((board.height-2)):
        grid.append([0] + ([0] * (board.width - 2)) + [0])
    grid.append([0] + ([0] * (board.width - 2)) + [0])
    safest_nodes = [(-9999, (0,0))]
    for row in grid:
        for point in row:
            print(point, end=" ")
        print()
    print()
    for snake in board.other_snakes:
        x = 1
        queue = deque([(0, snake.get_head())])
        processed = set([snake.get_head()])
        while queue:
            length_of_path, curr_node = queue.popleft()
            x_node, y_node = curr_node
            val = length_of_path * x
            grid[y_node][x_node] += val
            if grid[y_node][x_node] > safest_nodes[0][0]:
                safest_nodes = [(grid[y_node][x_node], curr_node)]
            elif grid[y_node][x_node] == safest_nodes[0]:
                safest_nodes.append((grid[y_node][x_node], curr_node))
            neighbours = board.get_simple_neighbours(curr_node)
            for neighbour in neighbours:
                if not neighbour in processed:
                    processed.add(neighbour)
                    queue.append((length_of_path+1, neighbour))
    for row in grid:
        for point in row:
            print(point, end=" ")
        print()
    print()

    print(safest_nodes)
    for safety, node in safest_nodes:
        print(node)
        cost, path = a_star(board, board.my_snake.get_head(), node,
                            board.my_snake)
        if cost and can_go_to_tail_after_moves(board, path[1:]):
            return ("Going to least dense region", translate(
                                        board.my_snake.get_head(), path[1]))

    return (None, None)

def get_safest_move(board):
    neighbours = board.get_valid_neighbours(board.my_snake.get_head(),
                                            board.my_snake)
    min_node = (99999999, None)
    for neighbour in neighbours:
        food = 1 if neighbour in board.foods else 0
        cost = board.get_cost(neighbour, board.my_snake, 1, food)
        if cost < min_node[0]:
            min_node = (cost, neighbour)
    if min_node[1] is None:
        return (None, None)
    return ("Going to safest node", translate(board.my_snake.get_head(),
                                              min_node[1]))



def find_path_to_food(board):
    """Go to food that's furthest away from everyone but also make sure that
    no one can get to it before me.
    """
    cost_and_path_to_all_foods = []
    for food in board.foods:
        maximum = -99999
        for snake in board.other_snakes:
            diff = (get_manhattan_distance(board.my_snake.get_head(), food) -
                    get_manhattan_distance(snake.get_head(), food))
            if diff > maximum:
                maximum = diff
        heappush(cost_and_path_to_all_foods, (maximum, food))
    while cost_and_path_to_all_foods:
        distance_to_food, food = heappop(cost_and_path_to_all_foods)
        food_cost, food_path = a_star(board, board.my_snake.get_head(),
                                      food, board.my_snake)
        if food_cost == None:
            continue
        actual_distance_to_food = len(food_path) - 1
        unsafe = False
        for snake in board.other_snakes:
            distance, path = a_star(board, snake.get_head(), food, snake)
            if distance == None:
                continue
            if (snake.length > board.my_snake.length and
                distance < actual_distance_to_food):
                unsafe = True
        if unsafe or not can_go_to_tail_after_moves(board, food_path[1:]):
            continue
        return ("Going to food", translate(board.my_snake.get_head(),
                                           food_path[1]))
    return (None, None)


#### MISC ALGORITHMS #####

def path_to_tail_exists(board):
    """Checks to see if our tail is reachable given a board.
    """
    return a_star(board, board.my_snake.get_head(), board.my_snake.get_tail(),
               board.my_snake) != (None, None)

def can_go_to_tail_after_moves(board, path):
    """
    This function tells us whether a path to our tail exists after certain
    moves have been made.
    """
    return path_to_tail_exists(generate_new_board_with_path(board, path))

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
