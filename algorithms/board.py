import snake
import time
from constants import (EMPTY_SPACE_MAKERS, FOOD_MARKER, SAMARITAN_HEAD_MARKER,
    SAMARITAN_BODY_MARKER, ENEMY_SNAKE_HEAD_MARKER, ENEMY_SNAKE_BODY_MARKER,
    SNAKE_TAIL_MARKER)
from utils import get_manhattan_distance, translate
from heapq import heappush, heappop
from graph_algorithms import a_star, stall
from copy import deepcopy


class Board(object):
    '''
    This board class is used to display the game state when the game server is
    requesting a move.
    '''

    def __init__(self, data, mode=0):
        '''
        This function receives board information such as width and height and
        creates an empty grid to fill out once we recieve more information.
        It also has a mode instance variable:
        If mode is 0, everything is accessible in Board
        If mode is 1, then we are in a recursive call for the purposes of seeing
        whether getting food is going to kill us afterwards. So it's going to
        restrict all attacking strategies and check if we have defensive
        strategies
        If mode is 2, then we are in a recursive call for the purposes of
        paranoia, it's going to need all the attacking strategies but no
        defensive one.
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
        self.mode = mode
        self.bad_moves = []
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
            if snake.length + 2 >= self.samaritan.length:
                return False
        return True

    def get_neighbours(self, node, snake, distance_to_neighbour_nodes=1,
                       foods_in_path=0):
        '''
        Return a list of neighbours of a node if they are valid coordinates that
        Samaritan can go to.

        Parameters:
        node: necessary to get the neighbours around a node.
        snake: Necessary to get the distance from the snake's head to the
        neighbouring node. If the distance is greater than the time it'll take
        to get to the node from the snake's head, then it's a valid neighbour.
        distance_to_neighbour_nodes: Helps with calculating the distance to the
        neighboring nodes since calculating the manhattan distance doesn't
        always give us a true distance.
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
                                            foods_in_path)]

    def is_valid_coordinate(self, xcoord, ycoord, snake, distance_to_node,
                            foods_in_path=0):
        '''
        Check if a node is a valid node that Samaritan can go to without dying
        i.e., it's not out of the board, and if it's a wall, it won't be a
        wall by the time I get to it.
        '''
        node = (xcoord, ycoord)
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
                for snakes_node in reversed(snake_coordinates):
                    time_to_disappear += 1
                    if snakes_node == node:
                        break
                if time_to_disappear <= distance_to_node:
                    node_empty = True

        return node_empty

    # TODO: Add feature to give costs depending on which snake is asking. (The
    # lack of this feature is why the beginning move is timely.)
    def get_cost(self, node, my_snake, distance_to_node, foods_in_path):
        '''
        Calculates the cost to travel to the node in the parameter depending on
        from which snake's perspective we are looking at it from.
        '''
        cost = 1
        if (distance_to_node == 1
            and translate(my_snake.get_head(), node) in self.bad_moves):
            print translate(my_snake.get_head(), node)
            print self.bad_moves
            cost += 99999
        xcoord, ycoord = node
        if (xcoord == (self.width-1)
            or ycoord == (self.height-1)
            or xcoord == 0
            or ycoord == 0):
            cost += 2
            for snake in self.all_snake_objects():
                if (snake != my_snake and
                    get_manhattan_distance(snake.get_head(), node)
                    <= distance_to_node + 2):
                    cost += 4
            if ((xcoord == (self.width-1) and ycoord == (self.height-1))
                or (xcoord == (self.width-1) and ycoord == 0)
                or (xcoord == 0 and ycoord == (self.height-1))
                or (xcoord == 0 and ycoord == 0)):
                cost += 2
            else:
                if xcoord == self.width-1:
                    if (self.grid[ycoord][xcoord-1] == ENEMY_SNAKE_BODY_MARKER
                        and (xcoord-1, ycoord) not in my_snake.coordinates):
                        cost += 6
                elif ycoord == self.height-1:
                    if (self.grid[ycoord-1][xcoord] == ENEMY_SNAKE_BODY_MARKER
                        and (xcoord, ycoord-1) not in my_snake.coordinates):
                        cost += 6
                elif xcoord == 0:
                      if (self.grid[ycoord][xcoord+1] == ENEMY_SNAKE_BODY_MARKER
                          and (xcoord+1, ycoord) not in my_snake.coordinates):
                          cost += 6
                elif ycoord == 0:
                      if (self.grid[ycoord+1][xcoord] == ENEMY_SNAKE_BODY_MARKER
                          and (xcoord, ycoord+1) not in my_snake.coordinates):
                          cost += 6
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
        valid_neighbours = self.get_neighbours(node, my_snake, distance_to_node,
                                               foods_in_path)
        if (self.grid[ycoord][xcoord] == EMPTY_SPACE_MAKERS
            and len(valid_neighbours) == 0):
            cost += 999
        for snake in self.all_snake_objects():
            if snake != my_snake:
                if (snake.get_head() in neighbours
                    and snake.length >= my_snake.length):
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
        if self.mode == 0:
            iteration = 0
            if len(self.other_snakes) == 0:
                health_limit = 70
            else:
                health_limit = 40
            objective = None
            while True:
                iteration += 1
                if iteration < 2:
                    if objective == None:
                        objective, move, enemy_id = self.cornering_enemies()
                    if objective == None:
                        objective, move, enemy_id = self.trapping_enemies()
                    if objective == None:
                        objective, move, enemy_id = self.walling_enemies()

                if (self.samaritan.health <= health_limit
                    or not self.is_samaritan_biggest()):
                    if objective == None:
                        objective, move = self.find_path_to_safe_food()
                    if objective == None:
                        objective, move = self.find_path_to_risky_food()
                    if objective == None:
                        objective, move = self.find_path_to_my_tail()
                else:
                    if objective == None:
                        objective, move = self.attack_enemy()
                    if objective == None:
                        objective, move = self.find_path_to_my_tail()
                    if objective == None:
                        objective, move = self.find_path_to_safe_food()
                    if objective == None:
                        objective, move = self.find_path_to_risky_food()
                if objective == None:
                    objective, move = stall(self)
                if objective != None:
                    print "My move is", objective, move
                    e_objective, e_move, snake = self.get_best_enemy_attack(
                                                        objective, move)
                    print "The counter move is", e_objective, e_move
                    if e_objective == None:
                        break
                    else:
                        if iteration > 4:
                            return ('Best Bad Move', self.bad_moves[0])
                        else:
                            self.bad_moves.append(move)
                            objective, move = None, None
                else:
                    return ('Death', 'left')
            return (objective, move)
        elif self.mode == 1:
            objective, move = None, None
            if objective == None:
                objective, move = self.find_path_to_my_tail()
            if objective != None:
                return objective, move
            else:
                return ('Death', 'left')
        elif self.mode == 2:
            samaritan = self.other_snakes[-1]
            accessible_to_tail = a_star(self, samaritan.get_head(),
                                        samaritan.get_tail(), samaritan)
            if accessible_to_tail == (None, None):
                return ('Walling off', 'right', samaritan.id)
            objective, move, enemy_id = self.cornering_enemies()
            if not objective == None:
                return (objective, move, enemy_id)
            objective, move, enemy_id = self.trapping_enemies()
            if not objective == None:
                return (objective, move, enemy_id)
            objective, move, enemy_id = self.walling_enemies()
            if not objective == None:
                return (objective, move, enemy_id)
            return (None, None, None)

    def cornering_enemies(self):
        '''This attack tactic by samaritan corners an enemy if the enemy is
        'going through a tunnel' i.e. there's only one valid move the enemy
        snake can do if it goes to that node. This typically occurs when an
        enemy is going along the edges.
        '''
        for snake in self.other_snakes:
            distance = 2
            neighbours = self.get_neighbours(snake.get_head(), snake)
            if len(neighbours) != 1:
                continue
            curr_node = snake.get_head()
            while len(neighbours) == 1:
                prev_node = curr_node
                curr_node = neighbours[0]
                neighbours = self.get_neighbours(curr_node, snake, distance)
                distance += 1
                if prev_node in neighbours:
                    neighbours.remove(prev_node)
            exit_node = prev_node
            if len(neighbours) == 0:
                continue
            if (get_manhattan_distance(snake.get_head(), exit_node)
                < get_manhattan_distance(self.samaritan.get_head(), exit_node)):
                exit_node = curr_node
            if (get_manhattan_distance(snake.get_head(), exit_node)
                < get_manhattan_distance(self.samaritan.get_head(), exit_node)):
                return (None, None, None)
            enemy_cost, enemy_path = a_star(self, snake.get_head(), exit_node,
                                            snake)
            samaritan_cost, samaritan_path = a_star(self,
                                    self.samaritan.get_head(), exit_node,
                                    self.samaritan)
            if (samaritan_cost == None or enemy_cost == None
                or len(samaritan_path) == 1):
                continue
            distance_of_enemy_to_exit = len(enemy_path) - 1
            distance_of_samaritan_to_exit = len(samaritan_path) - 1
            if (distance_of_samaritan_to_exit < distance_of_enemy_to_exit
                or (distance_of_samaritan_to_exit == distance_of_enemy_to_exit
                    and snake.length < self.samaritan.length)):
                return ("Cornering", translate(self.samaritan.get_head(),
                                               samaritan_path[1]), snake.id)
            else:
                if exit_node == curr_node:
                    return (None, None, None)
                exit_node = curr_node

                enemy_cost, enemy_path = a_star(self, snake.get_head(), exit_node,
                                                snake)
                samaritan_cost, samaritan_path = a_star(self,
                                                        self.samaritan.get_head(),
                                                        exit_node,
                                                        self.samaritan)
                if samaritan_cost == None or enemy_cost == None:
                    continue
                distance_of_enemy_to_exit = len(enemy_path) - 1
                distance_of_samaritan_to_exit = len(samaritan_path) - 1
                if (distance_of_samaritan_to_exit < distance_of_enemy_to_exit
                    or (distance_of_samaritan_to_exit == distance_of_enemy_to_exit
                        and snake.length < self.samaritan.length)):
                    return ("Cornering", translate(self.samaritan.get_head(),
                                                   samaritan_path[1]), snake.id)
        return (None, None, None)

    def trapping_enemies(self):
        '''
        An attack tactic used to trap enemies if they are going along the edges
        and I can trap them by walling them off from going anywhere else other
        than into a wall.
        '''
        for snake in self.other_snakes:
            xcoord, ycoord = snake.get_head()
            direction_of_enemy = translate(snake.coordinates[1],
                                           snake.get_head())
            permissible_directions_for_samaritan = [direction_of_enemy]
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
                return ('Trapping', move, snake.id)

        return (None, None, None)

    def walling_enemies(self):
        '''
        An attack tactic used by Samaritan used against enemy snakes. If there
        are nodes that Samaritan can restrict that would disallow the enemy from
        reaching his tail, Samaritan will wall the enemy off. This results in a
        lot of kills.
        '''
        if len(self.other_snakes) == 0:
            return (None, None, None)
        neighbours = self.get_neighbours(self.samaritan.get_head(),
                                         self.samaritan)
        moves_to_edge = []
        for neighbour in neighbours:
            food_coordinates = self.foods[:]
            other_snakes = deepcopy(self.other_snakes)
            samaritan = deepcopy(self.samaritan)
            start = self.samaritan.get_head()
            destination = neighbour
            distance_to_edge = 0
            direction = translate(start, destination)
            valid_move = True
            path_to_edge = [self.samaritan.get_head()]
            foods = 0
            health_loss = 0
            while valid_move:
                target_x, target_y = destination
                if self.grid[target_y][target_x] != EMPTY_SPACE_MAKERS:
                    if destination in food_coordinates:
                        food_coordinates.remove(destination)
                        samaritan.health = 100
                        foods += 1
                        health_loss = 0
                    else:
                        if destination not in samaritan.coordinates:
                            its_a_tail = False
                            for snake in other_snakes:
                                if snake.get_tail() == destination:
                                    if len(snake.coordinates) == 1:
                                        break
                                    its_a_tail = True
                                    snake.coordinates.remove(destination)
                            if not its_a_tail:
                                break
                path_to_edge.append(destination)
                start = destination
                distance_to_edge += 1
                health_loss += 1
                if direction == 'up':
                    destination = (target_x, target_y-1)
                elif direction == 'down':
                    destination = (target_x, target_y+1)
                elif direction == 'left':
                    destination = (target_x-1, target_y)
                else:
                    destination = (target_x+1, target_y)
                valid_move = self.is_valid_coordinate(destination[0],
                                                      destination[1],
                                                      self.samaritan,
                                                      distance_to_edge+1,
                                                      foods_in_path=foods)
            samaritan.health -= health_loss
            new_snake_coords = []
            if samaritan.health == 100:
                samaritan.length += foods
                if samaritan.length-1 <= distance_to_edge:
                    for x in range(samaritan.length-1):
                        xcoord, ycoord = path_to_edge[-1-x]
                        new_snake_coords.append((xcoord, ycoord))
                    samaritan.coordinates = new_snake_coords
                else:
        # did divided by 2 here to see if it works better, maybe change it back.
                    for x in range((distance_to_edge/2)-(foods-1)):
                        samaritan.coordinates.pop()
                    for xcoord, ycoord in path_to_edge[1:]:
                        samaritan.coordinates.insert(0, (xcoord, ycoord))
                samaritan.coordinates.append(samaritan.coordinates[-1])
            else:
                samaritan.length += foods
                if samaritan.length <= distance_to_edge:
                    for x in range(samaritan.length):
                        xcoord, ycoord = path_to_edge[-1-x]
                        new_snake_coords.append((xcoord, ycoord))
                    samaritan.coordinates = new_snake_coords
                else:
        # did divided by 2 here to see if it works better, maybe change it back.
                    for x in range((distance_to_edge/2)-foods):
                        samaritan.coordinates.pop()
                    for xcoord, ycoord in path_to_edge[1:]:
                        samaritan.coordinates.insert(0, (xcoord, ycoord))

            new_board = Board(self.generate_data_dictionary(food_coordinates,
                                                    other_snakes, samaritan), 1)
            for x in range(len(new_board.other_snakes)):
                enemy_snake = self.other_snakes[x]
                future_enemy_snake = new_board.other_snakes[x]
                if (a_star(self, enemy_snake.get_head(), enemy_snake.get_tail(),
                        enemy_snake)) == (None, None):
                        continue
                if (a_star(new_board, future_enemy_snake.get_head(),
                          future_enemy_snake.get_tail(), future_enemy_snake)
                          == (None, None)):
                    can_wall_off_faster = True
                    for node in path_to_edge[1:]:
                        my_distance_to_node = get_manhattan_distance(
                                                self.samaritan.get_head(), node)
                        enemy_distance_to_node = get_manhattan_distance(
                                                 enemy_snake.get_head(), node)
                        if my_distance_to_node > enemy_distance_to_node:
                            can_wall_off_faster = False
                            break
                        elif (my_distance_to_node == enemy_distance_to_node
                              and enemy_snake.length >= self.samaritan.length):
                              can_wall_off_faster = False
                              break
                    if can_wall_off_faster:
                        heappush(moves_to_edge, (len(path_to_edge),
                                                 translate(
                                                     self.samaritan.get_head(),
                                                     path_to_edge[1]),
                                                 enemy_snake.id))
        if len(moves_to_edge) == 0:
            return (None, None, None)
        x, move, enemy_id = heappop(moves_to_edge)
        return ('Walling off', move, enemy_id)

    def find_path_to_safe_food(self):
        '''Used by Samaritan to find safe food.
        '''
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
            food_cost, food_path = a_star(self, self.samaritan.get_head(),
                                                food, self.samaritan,
                                                self.max_cost_to_food('safe'))
            if food_cost == None:
                continue
            actual_distance_to_food = len(food_path) - 1
            if len(self.other_snakes) != 0:
                if heappop(spaces_of_enemy_to_food) <= actual_distance_to_food:
                    continue
            food_coordinates = self.foods[:]
            other_snakes = deepcopy(self.other_snakes)
            samaritan = deepcopy(self.samaritan)
            foods = 0
            for node_x, node_y in food_path[1:]:
                if self.grid[node_y][node_x] != EMPTY_SPACE_MAKERS:
                    if (node_x, node_y) in food_coordinates:
                        food_coordinates.remove((node_x, node_y))
                        foods += 1
                    else:
                        if (node_x, node_y) not in samaritan.coordinates:
                            for snake in other_snakes:
                                if (node_x, node_y) in snake.coordinates:
                                    x = snake.coordinates.index((node_x,
                                                                 node_y))
                                    if x == 0:
                                        break
                                    snake.coordinates = snake.coordinates[:x]
            samaritan.health = 100
            new_snake_coords = []
            samaritan.length += foods
            if samaritan.length-1 <= actual_distance_to_food:
                for x in range(samaritan.length-1):
                    xcoord, ycoord = food_path[-1-x]
                    new_snake_coords.append((xcoord, ycoord))
                samaritan.coordinates = new_snake_coords
            else:
                for x in range(actual_distance_to_food-(foods-1)):
                    samaritan.coordinates.pop()
                for xcoord, ycoord in food_path[1:]:
                    samaritan.coordinates.insert(0, (xcoord, ycoord))
            samaritan.coordinates.append(samaritan.coordinates[-1])
            new_board = Board(self.generate_data_dictionary(food_coordinates,
                                                    other_snakes, samaritan), 1)
            objective, action = new_board.get_action()
            if objective == 'Death' or objective == 'Stalling':
                continue
            else:
                return ('Safe Food', translate(self.samaritan.get_head(),
                                          food_path[1]))
        return (None, None)


    def find_path_to_risky_food(self):
        '''Function used by Samaritan if he needs food desperately i.e. he's low
        on health or he isn't the biggest snake on the board.
        '''
        cost_and_path_to_all_foods = []
        for food in self.foods:
            heappush(cost_and_path_to_all_foods,
                     (get_manhattan_distance(self.samaritan.get_head(), food),
                      food))

        while cost_and_path_to_all_foods:
            distance_to_food, food = heappop(cost_and_path_to_all_foods)
            food_cost, food_path = a_star(self, self.samaritan.get_head(),
                                                food, self.samaritan,
                                                self.max_cost_to_food('risky'))
            if food_cost == None:
                continue
            actual_distance_to_food = len(food_path) - 1
            food_coordinates = self.foods[:]
            other_snakes = deepcopy(self.other_snakes)
            samaritan = deepcopy(self.samaritan)
            foods = 0
            for node_x, node_y in food_path[1:]:
                if self.grid[node_y][node_x] != EMPTY_SPACE_MAKERS:
                    if (node_x, node_y) in food_coordinates:
                        food_coordinates.remove((node_x, node_y))
                        foods += 1
                    else:
                        if (node_x, node_y) not in samaritan.coordinates:
                            for snake in other_snakes:
                                if (node_x, node_y) in snake.coordinates:
                                    x = snake.coordinates.index((node_x,
                                                                node_y))
                                    # if it's the head of an enemy snake,
                                    # then it's impossible to tell where
                                    # that snake is going to go next.
                                    if x == 0:
                                        break
                                    snake.coordinates = snake.coordinates[:x]
            samaritan.health = 100
            new_snake_coords = []
            samaritan.length += foods
            if samaritan.length-1 <= actual_distance_to_food:
                for x in range(samaritan.length-1):
                    xcoord, ycoord = food_path[-1-x]
                    new_snake_coords.append((xcoord, ycoord))
                samaritan.coordinates = new_snake_coords
            else:
                for x in range(actual_distance_to_food-(foods-1)):
                    samaritan.coordinates.pop()
                for xcoord, ycoord in food_path[1:]:
                    samaritan.coordinates.insert(0, (xcoord, ycoord))
            samaritan.coordinates.append(samaritan.coordinates[-1])
            new_board = Board(self.generate_data_dictionary(food_coordinates,
                                                    other_snakes, samaritan), 1)
            objective, action = new_board.get_action()
            if objective == 'Death' or objective == 'Stalling':
                continue
            else:
                return ('Risky Food', translate(self.samaritan.get_head(),
                                          food_path[1]))
        return (None, None)

    def find_path_to_my_tail(self):
        '''A* algorithm used by Samaritan to find a path to his tail.
        '''
        print 'Checking path to tail'
        cost_of_tail, path_to_tail = a_star(self,
                                            self.samaritan.get_head(),
                                            self.samaritan.get_tail(),
                                            self.samaritan)
        print 'path found: ', path_to_tail
        if path_to_tail == None or len(path_to_tail) == 1:
            return (None, None)
        return ('Going To My Tail', translate(self.samaritan.get_head(),
                           path_to_tail[1]))
    def attack_enemy(self):
        '''Used to attack the node that the enemy is most likely going to go to.
        '''
        attack_points = []
        for snake in self.other_snakes:
            neighbours = self.get_neighbours(snake.get_head(), snake)
            if len(neighbours) == 0:
                continue
            heappush(attack_points, (get_manhattan_distance(
                                     self.samaritan.get_head(), neighbours[0]),
                                     neighbours[0]))

        while attack_points:
            distance_to_attack_point, attack_point = heappop(attack_points)
            cost_of_enemy, path_to_enemy = a_star(self,
                                            self.samaritan.get_head(),
                                            attack_point,
                                            self.samaritan, 15)
            if cost_of_enemy != None:
                return ('Attacking', translate(self.samaritan.get_head(),
                                           path_to_enemy[1]))
        return (None, None)

    def get_best_enemy_attack(self, objective, move):
        '''A paranoid move checker function used by Samaritan after he finds a
        move that he wants to execute. This function predicts how enemies will
        be able to hurt Samaritan by making an instance of our board where
        the enemy is Samaritan and we check if the enemy can trap, wall or
        corner Samaritan if he executes his move.
        '''
        if len(self.other_snakes) == 0:
            return (None, None, None)
        samaritan = deepcopy(self.samaritan)
        other_snakes = deepcopy(self.other_snakes)
        foods = self.foods[:]
        target_x, target_y = (None, None)
        if move == 'up':
            head_x, head_y = samaritan.get_head()
            target_x, target_y = head_x, head_y-1
        elif move == 'down':
            head_x, head_y = samaritan.get_head()
            target_x, target_y = head_x, head_y+1
        elif move == 'left':
            head_x, head_y = samaritan.get_head()
            target_x, target_y = head_x-1, head_y
        else:
            head_x, head_y = samaritan.get_head()
            target_x, target_y = head_x+1, head_y

        samaritan.coordinates.insert(0, (target_x, target_y))
        if (target_x, target_y) in foods:
            foods.remove((target_x, target_y))
        samaritan.coordinates.pop()
        samaritan.health -= 1
        closest_snake = []
        for snake in other_snakes:
            neighbours = self.get_neighbours(snake.get_head(), snake)
            if len(neighbours) == 0:
                continue
            heappush(closest_snake, (get_manhattan_distance(snake.get_head(),
                                            samaritan.get_head()), snake))
        if len(closest_snake) == 0:
            return (None, None, None)
        all_enemy_threats = [heappop(closest_snake)]
        while len(closest_snake) != 0:
            prev_threat_distance, prev_threat_snake = all_enemy_threats[0]
            new_threat_distance, new_threat_snake = heappop(closest_snake)
            if new_threat_distance - prev_threat_distance <= 3:
                all_enemy_threats.append((new_threat_distance,
                                          new_threat_snake))
            else:
                break
        for x, snake in all_enemy_threats:
            new_samaritan = deepcopy(samaritan)
            new_other_snakes = deepcopy(other_snakes)
            new_foods = foods[:]
            for a_snake in new_other_snakes:
                if a_snake.id == snake.id:
                    new_other_snakes.remove(a_snake)
                    new_other_snakes = new_other_snakes + [new_samaritan]
                    new_samaritan = a_snake
                    neighbours = self.get_neighbours(a_snake.get_head(),
                                                     a_snake)
                    if a_snake.health != 100:
                        a_snake.coordinates.pop()
                    coordinates = a_snake.coordinates[:]
                    for neighbour in neighbours:
                        a_snake.coordinates = coordinates[:]
                        if neighbour == new_other_snakes[-1].get_head():
                            if a_snake.length >= new_other_snakes[-1].length:
                                return ('Walling off', translate(
                                    a_snake.get_head(), neighbour), a_snake.id)
                            else:
                                continue
                        if neighbour in foods:
                            new_foods.remove(neighbour)
                        a_snake.coordinates.insert(0, neighbour)
                        new_board = Board(self.generate_data_dictionary(foods,
                                            new_other_snakes, new_samaritan), 2)
                        objective, move, enemy_id = new_board.get_action()
                        if self.samaritan.id == enemy_id:
                            return (objective, move, snake.id)
        return (None, None, None)

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


    def generate_data_dictionary(self, foods, enemies, samaritan):
        '''
        This function generates the same request JSON that the game server sends
        us (given information about the game board entity location). The purpose
        of this is to create another board instance somewhere else. In order to
        do that, I need the same JSON request formatting that was used by the
        game server, hence the structure of the data dictionary below is based
        on that JSON request.
        '''
        data = {
          "food": {
            "data": []
          },
          "height": self.height,
          "snakes": {
            "data": []
          },
          "width": self.width,
        }
        for food_x, food_y in foods:
            data['food']['data'].append({
                "x": food_x,
                "y": food_y
            })

        for x in range(len(enemies)):
            data['snakes']['data'].append({
              "body": {
                "data": []
              },
              "health": enemies[x].health,
              "id": enemies[x].id,
              "length": enemies[x].length,
             })
            for coordinate_x, coordinate_y in enemies[x].coordinates:
                data['snakes']['data'][x]['body']['data'].append({
                    'x': coordinate_x,
                    'y': coordinate_y
                })

        data['you'] = {
            "body": {
              "data": []
            },
            "health": samaritan.health,
            "id": samaritan.id,
            "length": samaritan.length,
        }
        for coordinate_x, coordinate_y in samaritan.coordinates:
            data['you']['body']['data'].append({
                'x': coordinate_x,
                'y': coordinate_y
            })
        return data

    def max_cost_to_food(self, mode):
        '''
        Determines the max cost to food depending on the size of the board.
        If Samaritan is going for risky food then the cost limit to the food is
        going to be higher.
        '''
        if mode == 'risky':
            return self.height + self.width
        if mode == 'safe':
            return (self.height + self.width)/2



    '''The bottom 5 commented-out functions are currently not in use but are
    kept here in case the may be needed in the future.  '''
    # def area(self, snake):
    #     '''
    #     Given a snake, returns the area around the snake by doing a floodfill.
    #     '''
    #     return floodfill(self, snake)
    #
    # def advanced_area(self, snake):
    #     '''
    #     Given a snake, returns the area around the snake by doing a floodfill.
    #     '''
    #     return advanced_floodfill(self, snake)
    #
    # def stall_after_walled(self, snake_id, move):
    #     food_coordinates = self.foods[:]
    #     other_snakes = deepcopy(self.other_snakes)
    #     samaritan = deepcopy(self.samaritan)
    #     for other_snake in other_snakes:
    #         if snake_id == other_snake.id:
    #             destination = (None, None)
    #             start = other_snake.get_head()
    #             start_x, start_y = start
    #             if move == 'up':
    #                 destination = start_x, start_y-1
    #             elif move == 'down':
    #                 destination = start_x, start_y+1
    #             elif move == 'left':
    #                 destination = start_x-1, start_y
    #             else:
    #                 destination = start_x+1, start_y
    #             valid_move = True
    #             path_to_edge = [start]
    #             foods = 0
    #             health_loss = 0
    #             distance_to_edge = 0
    #             while valid_move:
    #                 target_x, target_y = destination
    #                 if self.grid[target_y][target_x] != EMPTY_SPACE_MAKERS:
    #                     if destination in food_coordinates:
    #                         food_coordinates.remove(destination)
    #                         other_snake.health = 100
    #                         foods += 1
    #                         health_loss = 0
    #                     else:
    #                         if destination not in other_snake.coordinates:
    #                             break
    #                 path_to_edge.append(destination)
    #                 start = destination
    #                 distance_to_edge += 1
    #                 health_loss += 1
    #                 if move == 'up':
    #                     destination = (target_x, target_y-1)
    #                 elif move == 'down':
    #                     destination = (target_x, target_y+1)
    #                 elif move == 'left':
    #                     destination = (target_x-1, target_y)
    #                 else:
    #                     destination = (target_x+1, target_y)
    #                 valid_move = self.is_valid_coordinate(destination[0],
    #                                                       destination[1],
    #                                                       other_snake,
    #                                                       distance_to_edge+1,
    #                                                       foods_in_path=foods)
    #             other_snake.health -= health_loss
    #             new_snake_coords = []
    #             if other_snake.health == 100:
    #                 other_snake.length += foods
    #                 if other_snake.length-1 <= distance_to_edge:
    #                     for x in range(other_snake.length-1):
    #                         xcoord, ycoord = path_to_edge[-1-x]
    #                         new_snake_coords.append((xcoord, ycoord))
    #                     other_snake.coordinates = new_snake_coords
    #                 else:
    #                     for x in range(distance_to_edge-(foods-1)):
    #                         other_snake.coordinates.pop()
    #                     for xcoord, ycoord in path_to_edge[1:]:
    #                         other_snake.coordinates.insert(0, (xcoord, ycoord))
    #                 other_snake.coordinates.append(other_snake.coordinates[-1])
    #             else:
    #                 other_snake.length += foods
    #                 if other_snake.length <= distance_to_edge:
    #                     for x in range(other_snake.length):
    #                         xcoord, ycoord = path_to_edge[-1-x]
    #                         new_snake_coords.append((xcoord, ycoord))
    #                     other_snake.coordinates = new_snake_coords
    #                 else:
    #                     for x in range(distance_to_edge-foods):
    #                         other_snake.coordinates.pop()
    #                     for xcoord, ycoord in path_to_edge[1:]:
    #                         other_snake.coordinates.insert(0, (xcoord, ycoord))
    #
    #             new_board = Board(self.generate_data_dictionary(
    #                             food_coordinates, other_snakes, samaritan), 1)
    #             return stall(new_board)

    # def get_simple_neighbours(self, node):
    #     '''
    #     Return a list of neighbours of a node if they are valid coordinates that
    #     Samaritan can go to.
    #
    #     Parameters:
    #     node: necessary to get the neighbours around a node.
    #     snake: Necessary to get the distance from the snake's head to the
    #     neighbouring node. If the distance is greater than the time it'll take
    #     to get to the node from the snake's head, then it's a valid neighbour.
    #     distance_to_neighbour_node: Helps with calculating the distance to the
    #     neighboring nodes since calculating the manhattan distance doesn't
    #     always give us a true distance.
    #     ignoring_node: if we're attacking then we automatically want this method
    #     to tell us that a snake's head is a valid coordinate even though it's
    #     not.
    #     foods_in_path: If there is > 0 food in our path, this will increase the
    #     time to disappear for non-empty nodes that are samaritan's snake.
    #     '''
    #     xcoord, ycoord = node
    #     neighbours = [
    #         (xcoord + 1, ycoord), (xcoord - 1, ycoord),
    #         (xcoord, ycoord + 1), (xcoord, ycoord - 1)
    #         ]
    #     return [(i, j)
    #             for i, j in neighbours
    #             if self.is_simple_valid_coordinate(i, j)]
    #
    # def is_simple_valid_coordinate(self, xcoord, ycoord):
    #     if not (-1 < xcoord < self.width and -1 < ycoord < self.height):
    #         return False
    #     if not self.grid[ycoord][xcoord] == EMPTY_SPACE_MAKERS:
    #         return False
    #     return True
