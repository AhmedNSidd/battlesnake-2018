from pathfinding import a_star, node_counting
from board import *

class SelfSnake():
    def get_action(self, board):
        # get a random food
        # get a path to that food
        # get an action to follow that path

        '''
        your own tail
        enemy's tail
        smaller snakes head
        '''
        health = board.my_snake.health
        length = board.my_snake.length

        distance_to_each_food = []

        for food in board.foods:
            node = (get_manhattan_distance(board.my_snake.get_head(), food), food)
            distance_to_each_food.append(node)

        distance_to_each_food.sort()
        for my_distance, to_food in distance_to_each_food:
            cost_of_food, path_to_food = a_star(board, board.my_snake.get_head(), to_food)
            distances = []

            for snake in board.other_snakes:
                distances.append(get_manhattan_distance(snake.get_head(), to_food))

            for distance in distances:

                if health >= 99:
                    if path_to_food == None:
                        possible_surroundings = board.get_surrounding_coords()
                        possible_routes = []
                        for possible_coord in possible_surroundings:
                            possible_routes.append((node_counting(possible_coord), possible_coords))

                        possible_routes.sort()
                        i, best_possible_coord = possible_routes[-1]
                        return self.translate(board.my_snake.get_head(), best_possible_coord)

                    else:
                        return self.translate(board.my_snake.get_head(), path_to_food[1])

                elif length <= 3 or health <= 75:
                    if path_to_food == None:
                        possible_surroundings = board.get_surrounding_coords()
                        possible_routes = []
                        for possible_coord in possible_surroundings:
                            possible_routes.append((node_counting(possible_coord), possible_coords))

                        possible_routes.sort()
                        i, best_possible_coord = possible_routes[-1]
                        return self.translate(board.my_snake.get_head(), best_possible_coord)

                    else:
                        return self.translate(board.my_snake.get_head(), path_to_food[1])

                elif distance >= my_distance:
                    return self.translate(board.my_snake.get_head(), path_to_food[1])

                else:
                    if path_to_food == None:
                        possible_surroundings = board.get_surrounding_coords()
                        possible_routes = []
                        for possible_coord in possible_surroundings:
                            possible_routes.append((node_counting(possible_coord), possible_coords))

                        possible_routes.sort()
                        i, best_possible_coord = possible_routes[-1]
                        return self.translate(board.my_snake.get_head(), best_possible_coord)
                    else:
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




'''
if path == None:
    i = -1
    while path == None:
        i = i - 1
        cost, path = a_star(board, board.self_snake.get_head(), board.self_snake.coordinates[i])


    return self.translate(board.get_head(), path[1])
    '''
