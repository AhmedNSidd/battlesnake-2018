from pathfinding import a_star, bfs
from board import *
from heapq import heappush, heappop

class SelfSnake():
    def get_action(self, board):
        '''
        If health (< 30) or length is low:
        1st priority: Food (A*)
        2nd priority: Tail (A*)
        3rd priority: Enemy's tail (A*)
        4th priority: At this point, i'm probably trapped, so stall until an exit opens. (DFS + Reverse-floodfill)

        If health and length is fine:
        1st priority: Tail (A*)
        2nd priority: Enemy's tail (A*)
        3rd priority: At this point, i'm probably trapped, so stall until an exit opens. (DFS + Reverse-floodfill)

        How to stall:
        1 - Keep using BFS to find a path to snakes tail starting from the end until algorithm returns true
        2 - Use that node as the destination for reverse-floodfill algorithm
            a) Create a grid of WxH with -1 everywhere
            b) set i = 0
            c) add the destination to the grid as i++
            d) get_neighbours to mark the neighbours with i++
            * How to get neighbours: make sure a neighbour is within the height and width, is not a tail or a head of snake and is -1
            e) mark the neighbours of neighbours with i++ (check that the neighbours of neighbours are -1, if not, don't mark them.)
            f) keep marking until all valid neighbours are marked.
        3- from the start (snake's head), get valid neighbours of start, compare neighbour's values, whichever one is bigger, that's your destination
        '''

        foods = board.foods
        cost_and_path_to_all_foods = []
        for food in foods:
            print "Calculating cost to a food..."
            if (bfs(board, board.my_snake.get_head(), food)):
                heappush(cost_and_path_to_all_foods, a_star(board, board.my_snake.get_head(), food))
        if board.my_snake.health > 75 and board.my_snake.length > 5:
            print "Calculating cost to my tail..."
            if (bfs(board, board.my_snake.get_head(), board.my_snake.coordinates[-1])):
                cost_of_tail, path_to_tail = a_star(board, board.my_snake.get_head(), board.my_snake.coordinates[-1])
                return self.translate(board.my_snake.get_head(), path_to_tail[1])
            else:
                cost_of_food, path_to_food = heappop(cost_and_path_to_all_foods)
                return self.translate(board.my_snake.get_head(), path_to_food[1])
        else:
            try:
                cost_of_food, path_to_food = heappop(cost_and_path_to_all_foods)
                return self.translate(board.my_snake.get_head(), path_to_food[1])
            except IndexError:
                cost_of_tail, path_to_tail = a_star(board, board.my_snake.get_head(), board.my_snake.coordinates[-1])
                return self.translate(board.my_snake.get_head(), path_to_tail[1])


    def translate(self, self_coords, target_coords):
        self_x, self_y = self_coords
        target_x, target_y = target_coords
        if self_x == target_x:
            if self_y > target_y:
                return "up"
            elif self_y < target_y:
                return "down"
        elif self_y == target_y:
            if self_x > target_x:
                return "left"
            elif self_x < target_x:
                return "right"
