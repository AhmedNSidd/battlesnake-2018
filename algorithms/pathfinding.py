from heapq import heappush, heappop
from utils import get_manhattan_distance
from collections import deque


def a_star(board, start, target, snake, attacking=False):
    '''
    A pathfinding algorithm similar to djiskta's algorithm that find's the
    shortest path from start to target with the lowest cost (least dangerous)
    '''
    p_q = [(get_heuristic(start, target), [start],
            get_heuristic(start, target))]
    processed = set()

    while p_q:
        # print p_q # For Debugging Purposes.
        cost_of_path_so_far, path, prev_heuristic = heappop(p_q)
        curr_node = path[-1]
        processed.add(curr_node)
        if curr_node == target:
            return (cost_of_path_so_far, path)
        neighbours = board.get_neighbours(curr_node, snake, len(path)-1,
                                          attacking)
        for neighbour in neighbours:
            if not neighbour in processed:
                heappush(p_q, (get_heuristic(neighbour, target)
                               + board.get_cost(neighbour)
                               + (cost_of_path_so_far - prev_heuristic),
                                path + [neighbour],
                                get_heuristic(neighbour, target)))
    return (None, None)


def bfs(board, start, target, snake, attacking=False):
    '''
    Uses bfs to see if a path is available from start to target. Returns
    true if a path exists, else false.
    '''
    queue = deque([start])
    processed = set()
    while queue:
        curr_node = queue.popleft()
        processed.add(curr_node)
        if curr_node == target:
            return True
        neighbours = board.get_neighbours(curr_node, snake, attacking=attacking)
        for neighbour in neighbours:
            if not neighbour in processed:
                processed.add(neighbour)
                queue.append(neighbour)
    return False


def get_heuristic(curr_node, target):
    '''Returns the heuristic cost for A*
    '''
    return get_manhattan_distance(curr_node, target)
