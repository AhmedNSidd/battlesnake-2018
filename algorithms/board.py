import snake
from constants import *
from utils import get_manhattan_distance, translate
from heapq import heappush, heappop
from pathfinding import a_star, bfs


class Board(object):
    '''
    This board class is used to display the game state when the game server is
    requesting a move.
    '''

    def __init__(self, data):
        '''
        This function receives game state information as a parameter and creates
        an instance of a board object with relevant information set as instance
        variables for the object. It also marks and prints a grid representing
        the board.
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
        print

    def all_snake_objects(self):
        '''A method that returns all snake objects on the board.
        '''
        return self.other_snakes + [self.samaritan]

    def get_neighbours(self, node, snake, distance_to_node=None,
                       attacking=False):
        '''
        Return a list of neighbours of a node if they are valid coordinates that
        Samaritan can go to.
        '''
        xcoord, ycoord = node
        neighbours = [
            (xcoord + 1, ycoord), (xcoord - 1, ycoord),
            (xcoord, ycoord + 1), (xcoord, ycoord - 1)
            ]
        if distance_to_node != None:
            distance_to_node += 1

        return [(i, j)
                for i, j in neighbours
                if self.is_valid_coordinate(i, j, snake, distance_to_node,
                                            attacking)]

    def is_valid_coordinate(self, xcoord, ycoord, snake, distance_to_node=None,
                            attacking=False):
        '''
        Check if a node is a valid node that Samaritan can go to without dying
        i.e., it's not out of the board, and if it's a wall, it won't be a
        wall by the time I get to it.
        '''
        node = (xcoord, ycoord)
        if not (-1 < xcoord < self.width and -1 < ycoord < self.height):
            return False
        if attacking and self.grid[ycoord][xcoord] == ENEMY_SNAKE_HEAD_MARKER:
            return True
        node_empty = (self.grid[ycoord][xcoord] != SAMARITAN_BODY_MARKER
                      and self.grid[ycoord][xcoord] != ENEMY_SNAKE_BODY_MARKER
                      and self.grid[ycoord][xcoord] != SAMARITAN_HEAD_MARKER
                      and self.grid[ycoord][xcoord] != ENEMY_SNAKE_HEAD_MARKER
                      and self.grid[ycoord][xcoord] != SNAKE_TAIL_MARKER)
        if distance_to_node == None:
            distance_to_node = get_manhattan_distance(snake.get_head(), node)
        if not node_empty:
            for snake in self.all_snake_objects():
                if node in snake.coordinates:
                    if snake.health == 100:
                        time_to_disappear = 1
                        snake_coordinates = snake.coordinates[:-1]
                    else:
                        time_to_disappear = 0
                        snake_coordinates = snake.coordinates
                    for snakes_node in reversed(snake_coordinates):
                        time_to_disappear += 1
                        if snakes_node == node:
                            break
                    # print "neighbour: ", node
                    # print time_to_disappear
                    # print distance_to_node
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
            cost += 3
            if ((xcoord == (self.width-1) and ycoord == (self.height-1))
                or (xcoord == (self.width-1) and ycoord == 0)
                or (xcoord == 0 and ycoord == (self.height-1))
                or (xcoord == 0 and ycoord == 0)):
                cost+=5
            else:
                if (xcoord == (self.width-1) and
                   (self.grid[ycoord][xcoord-1] == ENEMY_SNAKE_HEAD_MARKER
                    or self.grid[ycoord][xcoord-1] == ENEMY_SNAKE_BODY_MARKER)):
                    cost += 999 # maybe change this and others to 999?
                elif (ycoord == (self.height-1)
                    and (self.grid[ycoord-1][xcoord] == ENEMY_SNAKE_HEAD_MARKER
                    or self.grid[ycoord-1][xcoord] == ENEMY_SNAKE_BODY_MARKER)):
                    cost += 999
                elif (xcoord == 0
                    and (self.grid[ycoord][xcoord+1] == ENEMY_SNAKE_HEAD_MARKER
                    or self.grid[ycoord][xcoord+1] == ENEMY_SNAKE_BODY_MARKER)):
                    cost += 999
                elif (ycoord == 0
                    and (self.grid[ycoord+1][xcoord] == ENEMY_SNAKE_HEAD_MARKER
                    or self.grid[ycoord+1][xcoord] == ENEMY_SNAKE_BODY_MARKER)):
                    cost += 999

        if node in self.foods:
            cost += 5

        neighbours = [
                (xcoord+1, ycoord), (xcoord-1, ycoord),
                (xcoord, ycoord+1), (xcoord, ycoord-1)
                ]
        for neighbour in neighbours:
            xcoord, ycoord = neighbour

            if ((-1 < xcoord < self.width and -1 < ycoord < self.height)
                and self.grid[ycoord][xcoord] == ENEMY_SNAKE_HEAD_MARKER):
                for snake in self.other_snakes:
                    if snake.coordinates[0] == neighbour:
                        if snake.length >= self.samaritan.length:
                            cost += 999
                        else:
                            cost -= 2 # questionable cost assignment?

        return cost

    def get_action(self):
        if self.samaritan.health > 70 and self.samaritan.length > 15:
            # attacking_info = self.attack_enemy()
            # if attacking_info:
            #     return attacking_info
            # else:
            cornering_info = self.cornering_enemies()
            if cornering_info:
                return cornering_info
            else:
                existing_path_to_tail = self.find_path_to_my_tail()

                if existing_path_to_tail:
                    return existing_path_to_tail
                else:
                    existing_path_to_food = self.find_path_to_food()
                    if existing_path_to_food:
                        return existing_path_to_food
                    else:
                        return ('Death', 'left')
        else:
            # print "Cornering"
            cornering_info = self.cornering_enemies()
            if cornering_info:
                return cornering_info
            else:
                # print "To Food"
                existing_path_to_food = self.find_path_to_food()
                if existing_path_to_food:
                    return existing_path_to_food
                else:
                    # print "To Tail"
                    existing_path_to_tail = self.find_path_to_my_tail()
                    if existing_path_to_tail:
                        return existing_path_to_tail
                    else:
                        # print "To Death"
                        return ('Death', 'left')


    def cornering_enemies(self):
        for snake in self.other_snakes:
            neighbours = self.get_neighbours(snake.get_head(), snake)
            if len(neighbours) != 1:
                continue
            curr_node = snake.get_head()
            while len(neighbours) == 1:
                prev_node = curr_node
                curr_node = neighbours[0]
                neighbours = self.get_neighbours(curr_node, snake)
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
                return False
            distance_of_enemy_to_exit = len(enemy_path) - 1
            distance_of_samaritan_to_exit = len(samaritan_path) - 1
            if (distance_of_samaritan_to_exit < distance_of_enemy_to_exit
                or (distance_of_samaritan_to_exit == distance_of_enemy_to_exit
                    and snake.length < self.samaritan.length)):
                return ("Cornering", translate(self.samaritan.get_head(),
                                               samaritan_path[1]))
            else:
                return False


    def find_path_to_food(self):
        cost_and_path_to_all_foods = []
        for food in self.foods:
            # print food
            heappush(cost_and_path_to_all_foods,
                     a_star(self, self.samaritan.get_head(), food,
                            self.samaritan))

        while cost_and_path_to_all_foods:
            cost, path_to_food  = heappop(cost_and_path_to_all_foods)
            if cost == None:
                continue
            data_for_new_board = self.data
            for food in data_for_new_board['food']['data'][:]:
                if (food['x'], food['y']) == path_to_food[-1]:
                    data_for_new_board['food']['data'].remove(food)
                    break
            steps_to_food = len(path_to_food) - 1
            data_for_new_board['you']['health'] = 100
            data_for_new_board['you']['length'] = self.samaritan.length + 1
            my_snake_coords = data_for_new_board['you']['body']['data']
            new_snake_coords = []
            if self.samaritan.length <= steps_to_food:
                for x in range(self.samaritan.length):
                    # Our new snake coordinates will start with head on food.
                    xcoord, ycoord = path_to_food[-1-x]
                    new_snake_coords.append({
                      "object": "point",
                      "x": xcoord,
                      "y": ycoord
                    })
            else:
                for x in range(steps_to_food):
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
            if objective == 'Death':
                continue
            else:
                return ('Getting Food', translate(self.samaritan.get_head(),
                                          path_to_food[1]))
        return False

    def find_path_to_my_tail(self):
        if (bfs(self, self.samaritan.get_head(), self.samaritan.get_tail(),
                self.samaritan)):
            cost_of_tail, path_to_tail = a_star(self,
                                                self.samaritan.get_head(),
                                                self.samaritan.get_tail(),
                                                self.samaritan)
            return ('Going To My Tail', translate(self.samaritan.get_head(),
                               path_to_tail[1]))
        else:
            return False

    # def attack_enemy(self):
    #     distances_to_other_snakes = []
    #     for snake in self.other_snakes:
    #         heappush(distances_to_other_snakes, (get_manhattan_distance(self.samaritan.get_head(), snake.get_head()), snake))
    #
    #     while distances_to_other_snakes:
    #         distance_to_snake, snake = heappop(distances_to_other_snakes)
    #         if distance_to_snake <= 6:
    #             return False
    #         if (bfs(self, self.samaritan.get_head(), snake.get_head(),
    #                 self.samaritan, True)):
    #             cost_of_enemy, path_to_enemy = a_star(self,
    #                                             self.samaritan.get_head(),
    #                                             snake.get_head(),
    #                                             self.samaritan, True)
    #             return ('Attacking', translate(self.samaritan.get_head(),
    #                                            path_to_enemy[1]))
    #     return False
