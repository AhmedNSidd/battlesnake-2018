from heapq import heappush, heappop
from utils import get_manhattan_distance
from collections import deque

def a_star(board, start, target):
    p_q = [(get_heuristic(start, target), [start], get_heuristic(start, target))]
    processed = set()

    while p_q:
        cost_of_path_so_far, path, prev_heuristic = heappop(p_q)
        print "cost_of_path_so_far", cost_of_path_so_far
        curr_node = path[-1]
        processed.add(curr_node)
        if curr_node == target:
            return (cost_of_path_so_far, path)
        neighbours = board.get_neighbours(curr_node)
        for neighbour in neighbours:
            if not neighbour in processed:
                heappush(p_q, (get_heuristic(neighbour, target) + board.get_cost(neighbour) + (cost_of_path_so_far - prev_heuristic),
                                path + [neighbour], get_heuristic(curr_node, target)))
    return (None, None)


def get_heuristic(curr_node, target):
    return get_manhattan_distance(curr_node, target)




'''
class NewPath():
    longest_path = []
    def find_new_path(self, board, start, target):
        if start == target:
            return start
        remaining_paths = board.get_neighbours(start)
        for path in remaining_paths:
            print path
            self.longest_path.append(self.find_new_path(board, path, target))

        print longest_path
'''
