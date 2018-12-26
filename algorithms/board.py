import snake
from constants import *
from utils import get_manhattan_distance, translate
from heapq import heappush, heappop
from graph_algorithms import a_star, bfs, stall
from copy import deepcopy

class Board(object):
    '''
    This board class is used to display the game state when the game server is
    requesting a move.
    '''

    def __init__(self, data):
        '''
        This function receives board information such as width and height and
        creates an empty grid to fill out once we recieve more information.
        '''
        self.data = data
        self.width = data['width']
        self.height = data['height']
        self.grid = []
        self.foods = self._parse_data_list(data['food']['data'])
        self.samaritan = self._parse_snake_object(data['you'])
        self.other_snakes = [self._parse_snake_object(snake)
                             for snake in data['snakes']['data']
                             if self.samaritan.id != snake['id']]
        self._mark_grid()
        self.print_grid()


    def _parse_data_list(self, data_list):
        '''
        Recieves a list of JSON objects and returns a list of tuples of x,y
        coordinates
        '''
        return [(point['x'], point['y']) for point in data_list]

    def _parse_snake_object(self, snake_object):
        '''Returns a snake object given the JSON object from the API
        '''
        id = snake_object['id']
        coords = self._parse_data_list(snake_object['body']['data'])
        length = snake_object['length']
        health = snake_object['health']
        return snake.Snake(id, coords, health, length)

    def _mark_grid(self):
        '''
        This method marks the entire grid with my snake, enemy snakes, foods,
        and empty spaces
        '''
        for x in range(self.height):
            self.grid.append([EMPTY_SPACE_MAKERS for y in range(self.width)])

        for x, y in self.samaritan.coordinates[1:-1]:
            self.grid[y][x] = SAMARITAN_BODY_MARKER

        x, y = self.samaritan.coordinates[0]
        self.grid[y][x] = SAMARITAN_HEAD_MARKER

        x, y = self.samaritan.coordinates[-1]
        self.grid[y][x] = SNAKE_TAIL_MARKER

        for other_snake in self.other_snakes:
            for x, y in other_snake.coordinates[1:-1]:
                self.grid[y][x] = ENEMY_SNAKE_BODY_MARKER

            x, y = other_snake.coordinates[0]
            self.grid[y][x] = ENEMY_SNAKE_HEAD_MARKER

            x, y = other_snake.coordinates[-1]
            self.grid[y][x] = SNAKE_TAIL_MARKER

        for x, y in self.foods:
            self.grid[y][x] = FOOD_MARKER

    def print_grid(self):
        '''A method that prints the grid.
        '''
        for row in self.grid:
            for point in row:
                print point,
            print
        print

    def all_snake_objects(self):
        '''A method that returns all snake objects on the board.
        '''
        return self.other_snakes + [self.samaritan]

    def is_samaritan_biggest(self):
        '''Returns a boolean telling us whether samaritan is the biggest snake
        on the board.'''
        for snake in self.other_snakes:
            if snake.length >= self.samaritan.length:
                return False
        return True

    def get_neighbours(self, node, snake, distance_to_neighbour_nodes=1,
                       ignoring_node=(None, None), foods_in_path=0):
        '''
        Return a list of neighbours of a node if they are valid coordinates that
        Samaritan can go to.

        Parameters:
        node: necessary to get the neighbours around a node.
        snake: Necessary to get the distance from the snake's head to the
        neighbouring node. If the distance is greater than the time it'll take
        to get to the node from the snake's head, then it's a valid neighbour.
        distance_to_neighbour_node: Helps with calculating the distance to the
        neighboring nodes since calculating the manhattan distance doesn't
        always give us a true distance.
        ignoring_node: if we're attacking then we automatically want this method
        to tell us that a snake's head is a valid coordinate even though it's
        not.
        foods_in_path: If there is > 0 food in our path, this will increase the
        time to disappear for non-empty nodes that are samaritan's snake.
        '''
        xcoord, ycoord = node
        neighbours = [
            (xcoord + 1, ycoord), (xcoord - 1, ycoord),
            (xcoord, ycoord + 1), (xcoord, ycoord - 1)
            ]

        return [(i, j)
                for i, j in neighbours
                if self.is_valid_coordinate(i, j, snake,
                                            distance_to_neighbour_nodes,
                                            ignoring_node, foods_in_path)]

    def is_valid_coordinate(self, xcoord, ycoord, snake, distance_to_node,
                            ignoring_node=(None, None), foods_in_path=0):
        '''
        Check if a node is a valid node that Samaritan can go to without dying
        i.e., it's not out of the board, and if it's a wall, it won't be a
        wall by the time I get to it.
        '''
        node = (xcoord, ycoord)
        if node == ignoring_node:
            return True
        if not (-1 < xcoord < self.width and -1 < ycoord < self.height):
            return False
        node_empty = (self.grid[ycoord][xcoord] != SAMARITAN_BODY_MARKER
                      and self.grid[ycoord][xcoord] != ENEMY_SNAKE_BODY_MARKER
                      and self.grid[ycoord][xcoord] != SAMARITAN_HEAD_MARKER
                      and self.grid[ycoord][xcoord] != ENEMY_SNAKE_HEAD_MARKER
                      and self.grid[ycoord][xcoord] != SNAKE_TAIL_MARKER)
        if node_empty:
            return True
        for snake in self.all_snake_objects():
            if node in snake.coordinates:
                time_to_disappear = snake.how_long_to_grow()
                if snake == self.samaritan:
                    time_to_disappear += foods_in_path
                snake_coordinates = snake.coordinates_with_no_repeats()
                # print snake_coordinates
                for snakes_node in reversed(snake_coordinates):
                    if snakes_node == node:
                        break
                    time_to_disappear += 1

                # print "neighbour: ", node
                # print "time_to_disappear", time_to_disappear
                # print "distance_to_node", distance_to_node
                if time_to_disappear <= distance_to_node:
                    node_empty = True

        return node_empty

    def get_cost(self, node):
        '''
        Helps calculate cost for the A* algorithm. If the node is in a dangerous
        spot, the cost is increased.
        '''
        cost = 1
        xcoord, ycoord = node
        if (xcoord == (self.width-1)
            or ycoord == (self.height-1)
            or xcoord == 0
            or ycoord == 0):
            cost += 1
            for snake in self.other_snakes:
                if (get_manhattan_distance(snake.get_head(), node) <=
                   get_manhattan_distance(self.samaritan.get_head(), node) + 2):
                    cost += 10
            if ((xcoord == (self.width-1) and ycoord == (self.height-1))
                or (xcoord == (self.width-1) and ycoord == 0)
                or (xcoord == 0 and ycoord == (self.height-1))
                or (xcoord == 0 and ycoord == 0)):
                cost += 1
            else:
                if xcoord == self.width-1:
                    if self.grid[ycoord][xcoord-1] == ENEMY_SNAKE_BODY_MARKER:
                        cost += 6
                    elif self.grid[ycoord][xcoord-1] == SAMARITAN_BODY_MARKER:
                        cost += 1
                elif ycoord == self.height-1:
                    if self.grid[ycoord-1][xcoord] == ENEMY_SNAKE_BODY_MARKER:
                        cost += 6
                    elif self.grid[ycoord-1][xcoord] == SAMARITAN_BODY_MARKER:
                        cost += 1
                elif xcoord == 0:
                      if self.grid[ycoord][xcoord+1] == ENEMY_SNAKE_BODY_MARKER:
                          cost += 6
                      elif self.grid[ycoord][xcoord+1] == SAMARITAN_BODY_MARKER:
                          cost += 1
                elif ycoord == 0:
                      if self.grid[ycoord+1][xcoord] == ENEMY_SNAKE_BODY_MARKER:
                          cost += 6
                      elif self.grid[ycoord+1][xcoord] == SAMARITAN_BODY_MARKER:
                          cost += 1
        neighbours = [
                (xcoord+1, ycoord), (xcoord-1, ycoord),
                (xcoord, ycoord+1), (xcoord, ycoord-1)
                ]
        horizontal_neighbours = neighbours[:2]
        vertical_neighbours = neighbours[2:]
        diagonal_neighbours = [
                (xcoord+1, ycoord+1), (xcoord-1, ycoord-1),
                (xcoord+1, ycoord-1), (xcoord-1, ycoord+1)
                ]
        valid_neighbours = self.get_neighbours(node, self.samaritan)
        if len(valid_neighbours) == 1:
            for diagonal_neighbour in diagonal_neighbours:
                x_diag, y_diag = diagonal_neighbour
                if (-1 < x_diag < self.width and -1 < y_diag < self.height):
                    if self.grid[y_diag][x_diag] == ENEMY_SNAKE_HEAD_MARKER:
                        cost += 999
        if (self.grid[ycoord][xcoord] == EMPTY_SPACE_MAKERS
            and len(valid_neighbours) == 0):
            cost += 999
        for snake in self.other_snakes:
            if (snake.get_head() in neighbours
                and snake.length >= self.samaritan.length): # enemy snake head is surrounding the node.
                cost += 999
        return cost

    def get_action(self):
        '''
        Priorities:
        - Need to be the biggest snake on the board.
        - Cornering is most important. If I am about to starve, calculate how
        long it's going to take to kill opponent (this is under the
        presupposition that only 1 enemy snake remains.)
        - Attacking. If my health is under 35, go for food immediately.
        - My tail. Might switch this for food instead.
        - Food
        - Stalling
        '''
        if len(self.other_snakes) == 0:
            safe_food_health_limit = 70
            risky_food_health_limit = 70
        else:
            safe_food_health_limit = 65
            risky_food_health_limit = 35
        objective, move = (None, None)
        # if self.samaritan.length < 4:
        #     objective, move = self.find_path_to_food() # should avoid doing this if i can win the game by killing the enemy by cornering.
        #     if not objective == None:
        #         return (objective, move)
        print "Cornering Enemies"
        objective, move = self.cornering_enemies()
        if not objective == None:
            return (objective, move)
        print "Trapping Enemies"
        objective, move = self.trapping_enemies()
        if not objective == None:
            return (objective, move)
        if self.samaritan.health > 50 and self.is_samaritan_biggest():
            objective, move = self.attack_enemy()
            if not objective == None:
                return (objective, move)
        objective, move = self.find_path_to_safe_food()
        if not objective == None:
            return (objective, move)
        if self.samaritan.health <= risky_food_health_limit:
            objective, move = self.find_path_to_risky_food()
            if not objective == None:
                return (objective, move)
        print "Finding My Tail"
        objective, move = self.find_path_to_my_tail()
        if not objective == None:
            return (objective, move)
        print "Stalling"
        objective, move = stall(self)
        if not objective == None:
            return (objective, move)
        return ("Death" , "left")

    def cornering_enemies(self):
        for snake in self.other_snakes:
            i = 2
            neighbours = self.get_neighbours(snake.get_head(), snake)
            if len(neighbours) != 1:
                continue
            curr_node = snake.get_head()
            while len(neighbours) == 1:
                prev_node = curr_node
                curr_node = neighbours[0]
                neighbours = self.get_neighbours(curr_node, snake, i)
                i += 1
                if prev_node in neighbours:
                    neighbours.remove(prev_node)
            exit_node = prev_node
            if len(neighbours) == 0:
                continue        # He's trapped himself so you can't do anything.

            enemy_cost, enemy_path = a_star(self, snake.get_head(), exit_node,
                                            snake)
            samaritan_cost, samaritan_path = a_star(self,
                                                    self.samaritan.get_head(),
                                                    exit_node,
                                                    self.samaritan)
            if samaritan_path == None:
                continue
            distance_of_enemy_to_exit = len(enemy_path) - 1
            distance_of_samaritan_to_exit = len(samaritan_path) - 1
            if (distance_of_samaritan_to_exit < distance_of_enemy_to_exit
                or (distance_of_samaritan_to_exit == distance_of_enemy_to_exit
                    and snake.length < self.samaritan.length)):
                return ("Cornering", translate(self.samaritan.get_head(),
                                               samaritan_path[1]))
        return (None, None)

    def trapping_enemies(self):
        for snake in self.other_snakes:
            xcoord, ycoord = snake.get_head()
            direction_of_enemy = translate(snake.coordinates[1],
                                           snake.get_head())
            permissible_directions_for_samaritan = [direction_of_enemy] # this process may be redundant as we check if it's a valid move later anyway?
            my_direction = translate(self.samaritan.coordinates[1],
                                     self.samaritan.get_head())
            move = None
            if xcoord == self.width-1:
                permissible_directions_for_samaritan.append('right')
                if my_direction in permissible_directions_for_samaritan:
                    if (self.samaritan.get_head() == (self.width-2, ycoord)
                        and self.is_valid_move(direction_of_enemy)):
                        move = direction_of_enemy
                    elif (self.samaritan.get_head() == (self.width-3, ycoord)
                          and self.is_valid_move('right')
                          and snake.length < self.samaritan.length):
                          move = 'right'
                    elif (self.samaritan.get_head() == (self.width-2, ycoord-1)
                          and direction_of_enemy == 'down'
                          and snake.length < self.samaritan.length
                          and self.is_valid_move('down')):
                          move = 'down'
                    elif (self.samaritan.get_head() == (self.width-2, ycoord+1)
                          and direction_of_enemy == 'up'
                          and snake.length < self.samaritan.length
                          and self.is_valid_move('up')):
                          move = 'up'
                    elif (self.samaritan.get_head() == (self.width-2, ycoord+1)
                          and direction_of_enemy == 'down'
                          and (len(self.get_neighbours(snake.get_head(),
                                                      snake)) <= 1)
                          and self.is_valid_move('down')):
                          move = 'down'
                    elif (self.samaritan.get_head() == (self.width-2, ycoord-1)
                          and direction_of_enemy == 'up'
                          and (len(self.get_neighbours(snake.get_head(),
                                                      snake, 1)) <= 1)
                          and self.is_valid_move('up')):
                          move = 'up'
            elif xcoord == 0:
                permissible_directions_for_samaritan.append('left')
                if my_direction in permissible_directions_for_samaritan:
                    if (self.samaritan.get_head() == (1, ycoord)
                        and self.is_valid_move(direction_of_enemy)):
                        move = direction_of_enemy
                    elif (self.samaritan.get_head() == (2, ycoord)
                          and self.is_valid_move('left')
                          and snake.length < self.samaritan.length):
                          move = 'left'
                    elif (self.samaritan.get_head() == (1, ycoord-1)
                          and direction_of_enemy == 'down'
                          and snake.length < self.samaritan.length
                          and self.is_valid_move('down')):
                          move = 'down'
                    elif (self.samaritan.get_head() == (1, ycoord+1)
                          and direction_of_enemy == 'up'
                          and snake.length < self.samaritan.length
                          and self.is_valid_move('up')):
                          move = 'up'
                    elif (self.samaritan.get_head() == (1, ycoord+1)
                          and direction_of_enemy == 'down'
                          and (len(self.get_neighbours(snake.get_head(),
                                                      snake, 1)) <= 1)
                          and self.is_valid_move('down')):
                          move = 'down'
                    elif (self.samaritan.get_head() == (1, ycoord-1)
                          and direction_of_enemy == 'up'
                          and (len(self.get_neighbours(snake.get_head(),
                                                      snake, 1)) <= 1)
                          and self.is_valid_move('up')):
                          move = 'up'
            elif ycoord == self.width-1:
                permissible_directions_for_samaritan.append('down')
                if my_direction in permissible_directions_for_samaritan:
                    if (self.samaritan.get_head() == (xcoord, self.height-2)
                        and self.is_valid_move(direction_of_enemy)):
                        move = direction_of_enemy
                    elif (self.samaritan.get_head() == (xcoord, self.height-3)
                          and self.is_valid_move('down')
                          and snake.length < self.samaritan.length):
                          move = 'down'
                    elif (self.samaritan.get_head() == (xcoord-1, self.height-2)
                          and direction_of_enemy == 'right'
                          and snake.length < self.samaritan.length
                          and self.is_valid_move('right')):
                          move = 'right'
                    elif (self.samaritan.get_head() == (xcoord+1, self.height-2)
                          and direction_of_enemy == 'left'
                          and snake.length < self.samaritan.length
                          and self.is_valid_move('left')):
                          move = 'left'
                    elif (self.samaritan.get_head() == (xcoord+1, self.height-2)
                          and direction_of_enemy == 'right'
                          and (len(self.get_neighbours(snake.get_head(),
                                                       snake, 1)) <= 1)
                          and self.is_valid_move('right')):
                          move = 'right'
                    elif (self.samaritan.get_head() == (xcoord-1, self.height-2)
                          and direction_of_enemy == 'left'
                          and (len(self.get_neighbours(snake.get_head(),
                                                       snake, 1)) <= 1)
                          and self.is_valid_move('left')):
                          move = 'left'
            elif ycoord == 0:
                permissible_directions_for_samaritan.append('up')
                if my_direction in permissible_directions_for_samaritan:
                    if (self.samaritan.get_head() == (xcoord, 1)
                        and self.is_valid_move(direction_of_enemy)):
                        move = direction_of_enemy
                    elif (self.samaritan.get_head() == (xcoord, 2)
                          and self.is_valid_move('up')
                          and snake.length < self.samaritan.length):
                          move = 'up'
                    elif (self.samaritan.get_head() == (xcoord-1, 1)
                          and direction_of_enemy == 'right'
                          and snake.length < self.samaritan.length
                          and self.is_valid_move('right')):
                          move = 'right'
                    elif (self.samaritan.get_head() == (xcoord+1, 1)
                          and direction_of_enemy == 'left'
                          and snake.length < self.samaritan.length
                          and self.is_valid_move('left')):
                          move = 'left'
                    elif (self.samaritan.get_head() == (xcoord+1, 1)
                          and direction_of_enemy == 'right'
                          and (len(self.get_neighbours(snake.get_head(),
                                                       snake, 1)) <= 1)
                          and self.is_valid_move('right')):
                          move = 'right'
                    elif (self.samaritan.get_head() == (xcoord-1, 1)
                          and direction_of_enemy == 'left'
                          and (len(self.get_neighbours(snake.get_head(),
                                                       snake, 1)) <= 1)
                          and self.is_valid_move('left')):
                          move = 'left'
            if move is not None:
                return ('Trapping', move)

        return (None, None)

    # def walling_enemies(self):
    #     neighbours = self.get_neighbours(self.samaritan.get_head(),
    #                                      self.samaritan)
    #     for neighbour in neighbours:
    #         start = self.samaritan.get_head()
    #         destination = neighbour
    #         distance_to_neighbour_node = 1
    #         direction = translate(start, destination)
    #         valid_move = True
    #         path_to_edge = []
    #         while valid_move:
    #             path_to_edge.append(destination)
    #             start = destination
    #             distance_to_neighbour_node += 1
    #             destination_x, destination_y = destination
    #             if direction == 'up':
    #                 destination = (destination_x, destination_y-1)
    #             elif direction == 'down':
    #                 destination = (destination_x, destination_y+1)
    #             elif direction == 'left':
    #                 destination = (destination_x-1, destination_y)
    #             else:
    #                 destination = (destination_x+1, destination_y)
    #             valid_move = self.is_valid_move(start, direction,
    #                                             distance_to_neighbour_node)
    #         for self.


    def find_path_to_safe_food(self):
        cost_and_path_to_all_foods = []
        for food in self.foods:
            heappush(cost_and_path_to_all_foods,
                     (get_manhattan_distance(self.samaritan.get_head(), food),
                      food))

        while cost_and_path_to_all_foods:
            distance_to_food, food = heappop(cost_and_path_to_all_foods)
            spaces_of_enemy_to_food = []
            for snake in self.other_snakes:
                space_of_enemy_to_food = get_manhattan_distance(
                                                    snake.get_head(), food)
                heappush(spaces_of_enemy_to_food, space_of_enemy_to_food)
                if space_of_enemy_to_food <= distance_to_food:
                    continue
            cost_of_food, path_to_food = a_star(self, self.samaritan.get_head(),
                                                food, self.samaritan)

            if cost_of_food == None:
                continue
            actual_distance_to_food = len(path_to_food) - 1
            if len(self.other_snakes) != 0:
                smallest_space_of_enemy_to_food = heappop(spaces_of_enemy_to_food)
                if smallest_space_of_enemy_to_food <= actual_distance_to_food:
                    continue
            if cost_of_food >= 6:
                continue
            data_for_new_board = deepcopy(self.data)        # this prevents changing self.data when changing the copy.
            for food in data_for_new_board['food']['data'][:]:
                if (food['x'], food['y']) == path_to_food[-1]:
                    data_for_new_board['food']['data'].remove(food)
                    break
            data_for_new_board['you']['health'] = 100
            data_for_new_board['you']['length'] = self.samaritan.length + 1
            my_snake_coords = data_for_new_board['you']['body']['data']
            new_snake_coords = []
            if self.samaritan.length <= actual_distance_to_food:
                for x in range(self.samaritan.length):
                    # Our new snake coordinates will start with head on food.
                    xcoord, ycoord = path_to_food[-1-x]
                    new_snake_coords.append({
                      "object": "point",
                      "x": xcoord,
                      "y": ycoord
                    })
            else:
                for x in range(actual_distance_to_food):
                    my_snake_coords.pop()
                for xcoord, ycoord in path_to_food[1:]:
                    my_snake_coords.insert(0, {
                      "object": "point",
                      "x": xcoord,
                      "y": ycoord
                    })
                new_snake_coords = my_snake_coords

            # Since our length is going to increase by 1 after getting the food.
            new_snake_coords.append(new_snake_coords[-1])
            data_for_new_board['you']['body']['data'] = new_snake_coords
            board_after_samaritan_eats = Board(data_for_new_board)
            objective, action = board_after_samaritan_eats.get_action()
            # print objective
            # print action
            if objective == 'Death' or objective == 'Stalling':
                continue
            else:
                return ('Safe Food', translate(self.samaritan.get_head(),
                                          path_to_food[1]))
        return (None, None)


    def find_path_to_risky_food(self):
        cost_and_path_to_all_foods = []
        for food in self.foods:
            heappush(cost_and_path_to_all_foods,
                     (get_manhattan_distance(self.samaritan.get_head(), food),
                      food))

        while cost_and_path_to_all_foods:
            distance_to_food, food = heappop(cost_and_path_to_all_foods)
            cost_of_food, path_to_food = a_star(self, self.samaritan.get_head(),
                                                food, self.samaritan)

            if cost_of_food == None:
                continue
            actual_distance_to_food = len(path_to_food) - 1
            if cost_of_food >= 12:
                continue
            data_for_new_board = deepcopy(self.data)        # this prevents changing self.data when changing the copy.
            for food in data_for_new_board['food']['data'][:]:
                if (food['x'], food['y']) == path_to_food[-1]:
                    data_for_new_board['food']['data'].remove(food)
                    break
            data_for_new_board['you']['health'] = 100
            data_for_new_board['you']['length'] = self.samaritan.length + 1
            my_snake_coords = data_for_new_board['you']['body']['data']
            new_snake_coords = []
            if self.samaritan.length <= actual_distance_to_food:
                for x in range(self.samaritan.length):
                    # Our new snake coordinates will start with head on food.
                    xcoord, ycoord = path_to_food[-1-x]
                    new_snake_coords.append({
                      "object": "point",
                      "x": xcoord,
                      "y": ycoord
                    })
            else:
                for x in range(actual_distance_to_food):
                    my_snake_coords.pop()
                for xcoord, ycoord in path_to_food[1:]:
                    my_snake_coords.insert(0, {
                      "object": "point",
                      "x": xcoord,
                      "y": ycoord
                    })
                new_snake_coords = my_snake_coords

            # Since our length is going to increase by 1 after getting the food.
            new_snake_coords.append(new_snake_coords[-1])
            data_for_new_board['you']['body']['data'] = new_snake_coords
            board_after_samaritan_eats = Board(data_for_new_board)
            objective, action = board_after_samaritan_eats.get_action()
            # print objective
            # print action
            if objective == 'Death' or objective == 'Stalling':
                continue
            else:
                return ('Risky Food', translate(self.samaritan.get_head(),
                                          path_to_food[1]))
        return (None, None)

    def find_path_to_my_tail(self):
        if (bfs(self, self.samaritan.get_head(), self.samaritan.get_tail(),
                self.samaritan)):
            cost_of_tail, path_to_tail = a_star(self,
                                                self.samaritan.get_head(),
                                                self.samaritan.get_tail(),
                                                self.samaritan)
            if path_to_tail == None:
                return (None, None)
            return ('Going To My Tail', translate(self.samaritan.get_head(),
                               path_to_tail[1]))
        else:
            return (None, None)

    def attack_enemy(self):
        distances_to_other_snakes = []
        for snake in self.other_snakes:
            heappush(distances_to_other_snakes,
                     (get_manhattan_distance(self.samaritan.get_head(),
                                             snake.get_head()), snake))

        while distances_to_other_snakes:
            distance_to_snake, snake = heappop(distances_to_other_snakes)
            if distance_to_snake <= 1:
                if self.is_head_on_collision(self.samaritan, snake):
                    continue
                else:
                    direction_of_enemy = translate(snake.coordinates[1],
                                                   snake.get_head())
                    if self.is_valid_move(direction_of_enemy):
                        return ('Attacking', direction_of_enemy)
                    else:
                        continue
            if (bfs(self, self.samaritan.get_head(), snake.get_head(),
                    self.samaritan, snake.get_head())):
                cost_of_enemy, path_to_enemy = a_star(self,
                                                self.samaritan.get_head(),
                                                snake.get_head(),
                                                self.samaritan,
                                                snake.get_head())
                if cost_of_enemy >= 8:
                    return (None, None)
                # print path_to_enemy
                if cost_of_enemy != None:
                    return ('Attacking', translate(self.samaritan.get_head(),
                                               path_to_enemy[1]))
        return (None, None)

    def is_head_on_collision(self, first_snake, second_snake):
        '''Returns a boolean telling us if two snakes are going in the opposite
        directions.
        '''
        first_node = first_snake.get_head()
        second_node = first_snake.coordinates[1]
        direction_of_first_snake = translate(second_node, first_node)
        first_node = second_snake.get_head()
        second_node = second_snake.coordinates[1]
        direction_of_second_snake = translate(second_node, first_node)
        return ((direction_of_first_snake == 'up' and
                 direction_of_second_snake == 'down') or
                (direction_of_first_snake == 'down' and
                 direction_of_second_snake == 'up') or
                (direction_of_first_snake == 'left' and
                 direction_of_second_snake == 'right') or
                (direction_of_first_snake == 'right' and
                 direction_of_second_snake == 'left'))

    def is_valid_move(self, move, distance=1, start=None):
        '''Tells us if taking a certain move with Samaritan is valid.
        '''
        if start == None:
            start = self.samaritan.get_head()
        xcoord, ycoord = start
        valid_coordinates = self.get_neighbours((xcoord, ycoord),
                                                self.samaritan, distance)
        if move == 'up':
            return (xcoord, ycoord-1) in valid_coordinates
        elif move == 'down':
            return (xcoord, ycoord+1) in valid_coordinates
        elif move == 'left':
            return (xcoord-1, ycoord) in valid_coordinates
        elif move == 'right':
            return (xcoord+1, ycoord) in valid_coordinates
        return False
