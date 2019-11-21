
from .utils import get_manhattan_distance, translate, max_cost_to_food
from heapq import heappush, heappop
from .graph_algorithms import a_star, bfs
from copy import deepcopy
from .board import Board
from .constants import EMPTY_SPACE_MAKERS

def find_path_to_food(board, risk):
    """Used by my snake to find food.
    """
    cost_and_path_to_all_foods = []
    for food in board.foods:
        max = -99999
        for snake in board.other_snakes:
            distance = get_manhattan_distance(board.my_snake.get_head(),
                                                food) - get_manhattan_distance(
                                                snake.get_head(), food)
            if distance > max:
                max = distance
        heappush(cost_and_path_to_all_foods, (max, food))

    while cost_and_path_to_all_foods:
        distance_to_food, food = heappop(cost_and_path_to_all_foods)
        spaces_of_enemy_to_food = []
        food_cost, food_path = a_star(board, board.my_snake.get_head(),
                                            food, board.my_snake,
                                            max_cost_to_food(board.height, 
                                                                board.width, 
                                                                risk))
        if food_cost == None:
            continue
        actual_distance_to_food = len(food_path) - 1
        unsafe = False
        if risk == "Safe":
            for snake in board.other_snakes:
                distance, path = bfs(board, snake.get_head(), food, snake)
                if distance == None:
                    continue
                if (snake.length > board.my_snake.length
                    and distance < actual_distance_to_food):
                    unsafe = True
        if unsafe:
            continue
        food_coordinates = board.foods[:]
        other_snakes = deepcopy(board.other_snakes)
        my_snake = deepcopy(board.my_snake)
        foods = 0
        for node_x, node_y in food_path[1:]:
            if board.grid[node_y][node_x] != EMPTY_SPACE_MAKERS:
                if (node_x, node_y) in food_coordinates:
                    food_coordinates.remove((node_x, node_y))
                    foods += 1
                else:
                    if (node_x, node_y) not in my_snake.coordinates:
                        for snake in other_snakes:
                            if (node_x, node_y) in snake.coordinates:
                                x = snake.coordinates.index((node_x,
                                                                node_y))
                                if x == 0:
                                    break
                                snake.coordinates = snake.coordinates[:x]
        my_snake.health = 100
        new_snake_coords = []
        my_snake.length += foods
        if my_snake.length-1 <= actual_distance_to_food:
            for x in range(my_snake.length-1):
                xcoord, ycoord = food_path[-1-x]
                new_snake_coords.append((xcoord, ycoord))
            my_snake.coordinates = new_snake_coords
        else:
            for x in range(actual_distance_to_food-(foods-1)):
                my_snake.coordinates.pop()
            for xcoord, ycoord in food_path[1:]:
                my_snake.coordinates.insert(0, (xcoord, ycoord))
        my_snake.coordinates.append(my_snake.coordinates[-1])
        new_board = Board(board.generate_data_dictionary(food_coordinates,
                                                other_snakes, my_snake))
        distance_to_tail, path_to_tail = bfs(new_board,
                                            new_board.my_snake.get_head(),
                                            new_board.my_snake.get_tail(),
                                            new_board.my_snake)
        if distance_to_tail == None:
            continue

        return ("{} food".format(risk), translate(
                                board.my_snake.get_head(), food_path[1]))

    return (None, None)

def find_path_to_my_tail(board):
    """A* algorithm used by my snake to find a path to his tail, but
    makes sure we go near the center first.
    """
    # print "Checking path to tail"
    halfway_x = int((board.width-1)/2)
    halfway_y = int((board.height-1)/2)
    center = (halfway_x, halfway_y)
    if (get_manhattan_distance(board.my_snake.get_head(), center) > int(halfway_x/2)):
        cost, path_to_center = a_star(board, board.my_snake.get_head(),
                                            center, board.my_snake)
        if cost != None:
            actual_distance_to_center = len(path_to_center) - 1
            food_coordinates = board.foods[:]
            other_snakes = deepcopy(board.other_snakes)
            my_snake = deepcopy(board.my_snake)
            foods = 0
            for node_x, node_y in path_to_center[1:]:
                if board.grid[node_y][node_x] != EMPTY_SPACE_MAKERS:
                    if (node_x, node_y) in food_coordinates:
                        food_coordinates.remove((node_x, node_y))
                        foods += 1
                    else:
                        if (node_x, node_y) not in my_snake.coordinates:
                            for snake in other_snakes:
                                if (node_x, node_y) in snake.coordinates:
                                    x = snake.coordinates.index((node_x,
                                                                    node_y))
                                    if x == 0:
                                        break
                                    snake.coordinates = snake.coordinates[:x]
            new_snake_coords = []
            my_snake.length += foods
            if my_snake.length-1 <= actual_distance_to_center:
                for x in range(my_snake.length-1):
                    xcoord, ycoord = path_to_center[-1-x]
                    new_snake_coords.append((xcoord, ycoord))
                my_snake.coordinates = new_snake_coords
            else:
                for x in range(actual_distance_to_center-(foods-1)): 
                    my_snake.coordinates.pop()
                for xcoord, ycoord in path_to_center[1:]:
                    my_snake.coordinates.insert(0, (xcoord, ycoord))
            my_snake.coordinates.append(my_snake.coordinates[-1])
            new_board = Board(board.generate_data_dictionary(food_coordinates,
                                                    other_snakes, my_snake))
            distance_to_tail, path_to_tail = bfs(new_board,
                                                new_board.my_snake.get_head(),
                                                new_board.my_snake.get_tail(),
                                                new_board.my_snake)
            if distance_to_tail != None:
                return ("Going to center", translate(
                            board.my_snake.get_head(),path_to_center[1]))

    cost_of_tail, path_to_tail = a_star(board,
                                        board.my_snake.get_head(),
                                        board.my_snake.get_tail(),
                                        board.my_snake)
    # print "path found: ", path_to_tail
    if path_to_tail == None or len(path_to_tail) == 1:
        return (None, None)
    return ("Going To My Tail", translate(board.my_snake.get_head(),
                        path_to_tail[1]))

