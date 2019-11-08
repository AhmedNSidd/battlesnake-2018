from heapq import heappush, heappop
from .utils import get_manhattan_distance, translate
from collections import deque

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
        # if target == board.other_snakes[-1].get_tail():
        #     print path_cost, path, foods_in_path
        if path_cost > cost_limit:
            continue
        curr_node = path[-1]
        processed.add(curr_node)
        if curr_node == target:
            return (path_cost, path)
        neighbours = board.get_neighbours(curr_node, snake, len(path),
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

def stall(board):
    """An algorithm that is used as a last resort by Samaritan when it's trapped
    Sometimes it's also used when A* can't find a way out, but there is, infact,
    a way out.
    """
    possible_routes = []
    neighbours_of_samaritan = board.get_neighbours(board.samaritan.get_head(),
                                                   board.samaritan)
    for neighbour in neighbours_of_samaritan:
        heappush(possible_routes, (1, [neighbour], set([neighbour])))
    if not possible_routes:
        return (None, None)
    while possible_routes:
        length_of_path, path, visited_nodes = heappop(possible_routes)
        neighbours_of_node = board.get_neighbours(path[-1], board.samaritan,
                                                  length_of_path)
        for neighbour in neighbours_of_node:
            if neighbour not in visited_nodes:
                visited_nodes.add(neighbour)
                heappush(possible_routes, (length_of_path+1, path + [neighbour],
                                           visited_nodes))
    return ("Stalling", translate(board.samaritan.get_head(), path[0]))

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
#         neighbours = board.get_simple_neighbours(curr_node)
#         for neighbour in neighbours:
#             if neighbour not in processed:
#                 to_be_processed.append((neighbour, length_of_path+1))
#     return len(processed) - 1
#
def advanced_floodfill(board, node, snake, distance_to_node=0, foods=0):
    """Advanced version accounts for moving snakes
    """
    processed = set()
    start = snake.get_head()
    to_be_processed = [(snake.get_head(), 0)]
    while to_be_processed:
        curr_node, length_of_path = to_be_processed.pop()
        processed.add(curr_node)
        neighbours = board.get_neighbours(curr_node, snake, length_of_path+1)
        for neighbour in neighbours:
            if neighbour not in processed:
                to_be_processed.append((neighbour, length_of_path+1))
    return len(processed) - 1

def bfs(board, start, target, snake):
    """
    Uses bfs to see if a path is available from start to target. Returns
    true if a path exists, else false.
    """
    queue = deque([(0, [start], (1 if start in board.foods else 0))])
    processed = set([start])
    while queue:
        length_of_path, path, foods_in_path = queue.popleft()
        curr_node = path[-1]
        if curr_node == target:
            return (length_of_path, path)
        neighbours = board.get_neighbours(curr_node, snake, length_of_path+1,
                                          foods_in_path)
        for neighbour in neighbours:
            if not neighbour in processed:
                processed.add(neighbour)
                queue.append((length_of_path+1, path + [neighbour],
                             (1 + foods_in_path if neighbour in board.foods
                                                else foods_in_path)))
    return (None, None)
