from heapq import heappush, heappop
from utils import get_manhattan_distance, translate
from collections import deque
from copy import deepcopy

def a_star(board, start, target, snake, cost_limit=99999):
    '''
    A pathfinding algorithm similar to djiskta's algorithm that find's the
    shortest path from start to target with the lowest cost (least dangerous)
    '''
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
        neighbours = board.get_neighbours(curr_node, snake, len(path),
                                          foods_in_path)
        for neighbour in neighbours:
            if not neighbour in processed:
                if neighbour == target:
                    heappush(p_q, (get_heuristic(neighbour, target)
                                   + 1 + (path_cost - prev_heuristic),
                                    path + [neighbour],
                                    get_heuristic(neighbour, target),
                                    (1 + foods_in_path if neighbour in board.foods
                                    else foods_in_path)))
                else:
                    heappush(p_q, (get_heuristic(neighbour, target)
                                   + board.get_cost(neighbour, len(path),
                                                    foods_in_path)
                                   + (path_cost - prev_heuristic),
                                    path + [neighbour],
                                    get_heuristic(neighbour, target),
                                    (1 + foods_in_path if neighbour in board.foods
                                    else foods_in_path)))
    return (None, None)


def bfs(board, start, target, snake):
    '''
    Uses bfs to see if a path is available from start to target. Returns
    true if a path exists, else false.
    '''
    queue = deque([(0, [start], (1 if start in board.foods else 0))])
    processed = set()
    while queue:
        length_of_path, path, foods_in_path = queue.popleft()
        curr_node = path[-1]
        processed.add(curr_node)
        if curr_node == target:
            return True
        neighbours = board.get_neighbours(curr_node, snake, length_of_path+1,
                                          foods_in_path)
        for neighbour in neighbours:
            if not neighbour in processed:
                queue.append((length_of_path+1, path + [neighbour],
                             (1 + foods_in_path if neighbour in board.foods
                                                else foods_in_path)))
    return False

def stall(board):
    '''An algorithm that is used as a last resort by Samaritan when it's trapped
    '''
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
    return ('Stalling', translate(board.samaritan.get_head(), path[0]))

def floodfill(board, snake):
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

def get_heuristic(curr_node, target):
    '''Returns the heuristic cost for A*
    '''
    return get_manhattan_distance(curr_node, target)
