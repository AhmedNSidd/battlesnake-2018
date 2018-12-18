from pathfinding import a_star, bfs
import board as NewBoard
from heapq import heappush, heappop

class Snake(object):
    def __init__(self, s_id, list_of_coords, health, length): # e.g list_of_coords = [(2,3), (3,4), etc.]
        self.id = s_id
        self.coordinates = list_of_coords
        self.health = health
        self.length = length

    def get_head(self):
        return self.coordinates[0]

    def get_tail(self):
        return self.coordinates[-1]

    def get_action(self, board):
        if self.health > 70 and self.length > 3:
            #enemy_snake_in_corner = check_for_corners(board)
            existing_path_to_tail = self.find_path_to_my_tail(board)

            if existing_path_to_tail:
                return existing_path_to_tail
            else:
                existing_path_to_food = self.find_path_to_food(board)
                if existing_path_to_food:
                    return existing_path_to_food
                else:
                    return ('Death', 'left')
        else:
            existing_path_to_food = self.find_path_to_food(board)
            if existing_path_to_food:
                return existing_path_to_food
            else:
                existing_path_to_tail = self.find_path_to_my_tail(board)
                if existing_path_to_tail:
                    return existing_path_to_tail
                else:
                    return ('Death', 'left')

    def find_path_to_food(self, board):
        foods = board.foods
        cost_and_path_to_all_foods = []

        for food in foods:
            heappush(cost_and_path_to_all_foods, a_star(board, self.get_head(), food))

        if not cost_and_path_to_all_foods:
            return False
        else:
            while cost_and_path_to_all_foods:
                cost, path_to_food  = heappop(cost_and_path_to_all_foods)
                if not cost == None:
                    data_for_new_board = board.data #remove food from new board and change my snake coords
                    for food in data_for_new_board['food']['data'][:]:
                        if (food['x'], food['y']) == path_to_food[-1]:
                            data_for_new_board['food']['data'].remove(food)
                            break
                    steps_to_food = len(path_to_food) - 1
                    data_for_new_board['you']['health'] = 100
                    data_for_new_board['you']['length'] = self.length + 1
                    my_snake_coords = data_for_new_board['you']['body']['data']
                    new_snake_coords = []
                    if self.length <= steps_to_food: # the snake is smaller than the steps to get to the food. hence use the path to food.
                        for x in range(0, self.length):
                            xcoord, ycoord = path_to_food[-1-x]
                            new_snake_coords.append({
                              "object": "point",
                              "x": xcoord,
                              "y": ycoord
                            })
                    else:
                        for x in range(0, steps_to_food):
                            my_snake_coords.pop()
                        for xcoord, ycoord in path_to_food[1:]:
                            my_snake_coords.insert(0, {
                              "object": "point",
                              "x": xcoord,
                              "y": ycoord
                            })
                        new_snake_coords = my_snake_coords
                    data_for_new_board['you']['body']['data'] = new_snake_coords
                    board_after_samaritan_eats = NewBoard.Board(data_for_new_board)
                    objective, action = board_after_samaritan_eats.my_snake.get_action(board_after_samaritan_eats)
                    if objective == 'Death':
                        return False
                    else:
                        return ('Food', translate(self.get_head(), path_to_food[1]))

    def find_path_to_my_tail(self, board):
        if (bfs(board, self.get_head(), self.get_tail())):
            cost_of_tail, path_to_tail = a_star(board, self.get_head(), self.get_tail())
            return ('My Tail', translate(self.get_head(), path_to_tail[1]))
        else:
            return False

def translate(self_coords, target_coords):
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





        '''
        If health (< 60) or length is low:
        1st priority: Food (A* + BFS) (If you're going to die when getting a food then go to another food)
        2nd priority: If no food, My Tail (A*)
        3rd priority: If not my tail, then Enemy's tail (A*)
        4th priority: At this point, i'm probably trapped, so stall until an exit opens. (???)

        If health and length is fine:
        1st priority: Tail (A*)
        2nd priority: Enemy's tail (A*)
        3rd priority: At this point, i'm probably trapped, so stall until an exit opens. (DFS + Floodfill)

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
