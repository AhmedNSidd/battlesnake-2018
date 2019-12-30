from heapq import heappush, heappop
from .utils import get_manhattan_distance, translate
from collections import deque
from .generators import generate_new_board_with_move

def battlestar(board, start, target):
    """
    This is an algorithm that calculates all viable paths from a start to a
    target and returns the one with the least cost.
    """
    if get_heuristic(start, target) > board.my_snake.health:
        return (None, None)
    p_q = [(get_heuristic(start, target), [start],
            get_heuristic(start, target), board)]
    processed = set()
    while p_q:
        cost, path, prev_heuristic, curr_board = heappop(p_q)
        curr_node = path[-1]
        if curr_node == target:
            return (cost, path)
        if curr_board.my_snake.health == 0:
            continue
        neighbours = curr_board.get_valid_neighbours(curr_node,
                                                     curr_board.my_snake)
        processed.add((curr_node, len(path) - 1))
        for neighbour in neighbours:
            if not (neighbour, len(path)) in processed:
                curr_heuristic = get_heuristic(neighbour, target)
                new_cost = (curr_heuristic + (cost - prev_heuristic) +
                            curr_board.get_cost(
                                neighbour, curr_board.my_snake))
                new_path = path + [neighbour]
                new_board = generate_new_board_with_move(
                    curr_board, translate(curr_node, neighbour))
                if curr_heuristic <= new_board.my_snake.health:
                    heappush(p_q, (new_cost, new_path, curr_heuristic,
                                   new_board))
    return (None, None)

def a_star(board, start, target, snake, cost_limit=99999):
    """
    A pathfinding algorithm similar to djiskta's algorithm that find's the
    shortest path from start to target with the lowest cost (least dangerous)

    It's different to A* in that it takes into account food on the path to the
    destination and it also takes into account the dynamic nature of the game.
    """
    p_q = [(get_heuristic(start, target), [start],
            get_heuristic(start, target), (1 if start in board.foods else 0))]
    processed = set()
    while p_q:
        path_cost, path, prev_heuristic, foods_in_path = heappop(p_q)
        if path_cost > cost_limit:
            continue
        curr_node = path[-1]
        processed.add(curr_node)
        if curr_node == target:
            return (path_cost, path)
        neighbours = board.get_valid_neighbours(curr_node, snake, len(path),
                                          foods_in_path)
        for neighbour in neighbours:
            if not neighbour in processed:
                new_cost = (get_heuristic(neighbour, target) + board.get_cost(
                                neighbour, snake, len(path), foods_in_path) +
                                (path_cost - prev_heuristic))
                new_path = path + [neighbour]
                curr_heuristic = get_heuristic(neighbour, target)
                foods = (1 + foods_in_path if neighbour in board.foods
                         else foods_in_path)
                heappush(p_q, (new_cost, new_path, curr_heuristic, foods))
    return (None, None)

def get_heuristic(curr_node, target):
    """Returns the heuristic cost for A*
    """
    return get_manhattan_distance(curr_node, target)

"""Bottom 2 functions are not currently being used however they may be helpful
in the future"""

# def floodfill(board, snake):
#     processed = set()
#     start = snake.get_head()
#     to_be_processed = [(snake.get_head(), 0)]
#     while to_be_processed:
#         curr_node, length_of_path = to_be_processed.pop()
#         processed.add(curr_node)
#         neighbours = board.get_simplest_neighbours(curr_node)
#         for neighbour in neighbours:
#             if neighbour not in processed:
#                 to_be_processed.append((neighbour, length_of_path+1))
#     return len(processed) - 1

def advanced_floodfill(board, node, snake, distance_to_node=0, foods=0):
    """Advanced version accounts for moving snakes
    """
    processed = set()
    start = snake.get_head()
    to_be_processed = [(snake.get_head(), 0)]
    while to_be_processed:
        curr_node, length_of_path = to_be_processed.pop()
        processed.add(curr_node)
        neighbours = board.get_valid_neighbours(curr_node, snake,
                                                length_of_path+1)
        for neighbour in neighbours:
            if neighbour not in processed:
                to_be_processed.append((neighbour, length_of_path+1))
    return len(processed) - 1


def bfs(board, start, target, snake):
    """
    Uses bfs to see if target is accessible from start.
    """
    queue = deque([(0, start, (1 if start in board.foods else 0))])
    processed = set([start])
    while queue:
        length_of_path, curr_node, foods_in_path = queue.popleft()
        if (curr_node == target
            or target in board.get_simplest_neighbours(curr_node)):
            return True
        neighbours = board.get_valid_neighbours(curr_node, snake,
                                                length_of_path+1,
                                                foods_in_path)
        for neighbour in neighbours:
            if not neighbour in processed:
                processed.add(neighbour)
                queue.append((length_of_path+1, neighbour,
                             (1 + foods_in_path if neighbour in board.foods
                                                else foods_in_path)))
    return False
