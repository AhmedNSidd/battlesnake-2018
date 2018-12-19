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
        self.my_snake = self._parse_snake_object(data['you'])
        self.other_snakes = [self._parse_snake_object(snake)
                             for snake in data['snakes']['data']
                             if self.my_snake.id != snake['id']]
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
        for x in range(0, self.height):
            self.grid.append([EMPTY_SPACE_MAKERS for y in range(0, self.width)])

        for x, y in self.my_snake.coordinates[1:-1]:
            self.grid[y][x] = SAMARITAN_BODY_MARKER

        x, y = self.my_snake.coordinates[0]
        self.grid[y][x] = SAMARITAN_HEAD_MARKER

        x, y = self.my_snake.coordinates[-1]
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
        return self.other_snakes + [self.my_snake]

    def get_neighbours(self, node):
        '''
        Return a list of neighbours of a node if they are valid coordinates that
        Samaritan can go to.
        '''
        xcoord, ycoord = node
        neighbours = [
            (xcoord + 1, ycoord), (xcoord - 1, ycoord),
            (xcoord, ycoord + 1), (xcoord, ycoord - 1)
            ]
        return [(i, j) for i, j in neighbours if self.is_valid_coordinate(i, j)]

    def is_valid_coordinate(self, xcoord, ycoord):
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
        distance_to_node = get_manhattan_distance(self.my_snake.get_head(),
                                                  node)
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
            cost += 2
        return cost

    def get_action(self):
        if self.my_snake.health > 70 and self.my_snake.length > 3:
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
            existing_path_to_food = self.find_path_to_food()
            if existing_path_to_food:
                return existing_path_to_food
            else:
                existing_path_to_tail = self.find_path_to_my_tail()
                if existing_path_to_tail:
                    return existing_path_to_tail
                else:
                    return ('Death', 'left')

    def find_path_to_food(self):
        cost_and_path_to_all_foods = []
        for food in self.foods:
            heappush(cost_and_path_to_all_foods,
                     a_star(self, self.my_snake.get_head(), food))

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
            data_for_new_board['you']['length'] = self.my_snake.length + 1
            my_snake_coords = data_for_new_board['you']['body']['data']
            new_snake_coords = []
            if self.my_snake.length <= steps_to_food:
                for x in range(0, self.my_snake.length):
                    xcoord, ycoord = path_to_food[-1-x]         # Our new snake coordinates will start with our head on the food.
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

            new_snake_coords.append(new_snake_coords[-1])         # Since our length is going to increase by 1.
            data_for_new_board['you']['body']['data'] = new_snake_coords
            board_after_samaritan_eats = Board(data_for_new_board)
            objective, action = board_after_samaritan_eats.get_action()
            if objective == 'Death':
                return False
            else:
                return ('Food', translate(self.my_snake.get_head(),
                                          path_to_food[1]))

    def find_path_to_my_tail(self):
        if (bfs(self, self.my_snake.get_head(), self.my_snake.get_tail())):
            cost_of_tail, path_to_tail = a_star(self,
                                                self.my_snake.get_head(),
                                                self.my_snake.get_tail())
            return ('My Tail', translate(self.my_snake.get_head(),
                               path_to_tail[1]))
        else:
            return False
