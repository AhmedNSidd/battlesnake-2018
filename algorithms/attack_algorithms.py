from .utils import get_manhattan_distance, translate
from .graph_algorithms import a_star, bfs
from copy import deepcopy
from .board import Board
from .constants import EMPTY_SPACE_MAKERS
from heapq import heappush, heappop


def attack_enemy(board):
    """Used to attack the node that the enemy is most likely going to go to.
    """
    attack_points = []
    for snake in board.other_snakes:
        neighbours = board.get_neighbours(snake.get_head(), snake)
        if len(neighbours) == 0:
            continue
        heappush(attack_points, (get_manhattan_distance(
                                    board.samaritan.get_head(), neighbours[0]),
                                    neighbours[0]))

    while attack_points:
        distance_to_attack_point, attack_point = heappop(attack_points)
        cost_of_enemy, path_to_enemy = a_star(board,
                                        board.samaritan.get_head(),
                                        attack_point,
                                        board.samaritan, 5)
        if cost_of_enemy != None:
            return ("Attacking", translate(board.samaritan.get_head(),
                                        path_to_enemy[1]))
    return (None, None)

def cornering_enemies(board):
    """
    This attack tactic by samaritan corners an enemy if the enemy is
    'going through a tunnel' i.e. there's only one valid move the enemy
    snake can do if it goes to that node. This typically occurs when an
    enemy is going along the edges.
    """
    for snake in board.other_snakes:
        distance = 2
        neighbours = board.get_neighbours(snake.get_head(), snake)
        if len(neighbours) != 1:
            continue
        curr_node = snake.get_head()
        while len(neighbours) == 1:
            prev_node = curr_node
            curr_node = neighbours[0]
            neighbours = board.get_neighbours(curr_node, snake, distance)
            distance += 1
            if prev_node in neighbours:
                neighbours.remove(prev_node)
        exit_node = prev_node
        if len(neighbours) == 0:
            continue
        enemy_distance = get_manhattan_distance(snake.get_head(), exit_node)
        if (enemy_distance < get_manhattan_distance(
                                    board.samaritan.get_head(), exit_node)):
            exit_node = curr_node
        if (enemy_distance < get_manhattan_distance(
                                    board.samaritan.get_head(), exit_node)):
            return (None, None, None)
        samaritan_cost, samaritan_path = a_star(board,
                                board.samaritan.get_head(), exit_node,
                                board.samaritan)
        # removed "or enemy_distance == None" from below
        if (samaritan_cost == None or len(samaritan_path) == 1):
            continue
        distance_of_samaritan_to_exit = len(samaritan_path) - 1
        if (distance_of_samaritan_to_exit < enemy_distance
            or (distance_of_samaritan_to_exit == enemy_distance
                and snake.length < board.samaritan.length)):
            return ("Cornering", translate(board.samaritan.get_head(),
                                            samaritan_path[1]), snake.id)
        else:
            if exit_node == curr_node:
                return (None, None, None)
            exit_node = curr_node
            enemy_distance = get_manhattan_distance(snake.get_head(),
                                                    exit_node)
            samaritan_cost, samaritan_path = a_star(board,
                    board.samaritan.get_head(), exit_node, board.samaritan)
            # removed "or enemy_distance == None" from below
            if (samaritan_cost == None or len(samaritan_path) == 1):
                continue
            distance_of_samaritan_to_exit = len(samaritan_path) - 1
            if (distance_of_samaritan_to_exit < enemy_distance
                or (distance_of_samaritan_to_exit == enemy_distance
                    and snake.length < board.samaritan.length)):
                return ("Cornering", translate(board.samaritan.get_head(),
                                                samaritan_path[1]), snake.id)
    return (None, None, None)

def trapping_enemies(board):
    """
    An attack tactic used to trap enemies if they are going along the edges
    and I can trap them by walling them off from going anywhere else other
    than into a wall.
    """
    for snake in board.other_snakes:
        xcoord, ycoord = snake.get_head()
        direction_of_enemy = translate(snake.coordinates[1],
                                        snake.get_head())
        permissible_directions_for_samaritan = [direction_of_enemy]
        my_direction = translate(board.samaritan.coordinates[1],
                                    board.samaritan.get_head())
        move = None
        if xcoord == board.width-1:
            permissible_directions_for_samaritan.append("right")
            if my_direction in permissible_directions_for_samaritan:
                if (board.samaritan.get_head() == (board.width-2, ycoord)
                    and board.is_valid_move(direction_of_enemy)):
                    move = direction_of_enemy
                elif (board.samaritan.get_head() == (board.width-3, ycoord)
                        and board.is_valid_move("right")
                        and snake.length < board.samaritan.length):
                        move = "right"
                elif (board.samaritan.get_head() == (board.width-2, ycoord-1)
                        and direction_of_enemy == "down"
                        and snake.length < board.samaritan.length
                        and board.is_valid_move("down")):
                        move = "down"
                elif (board.samaritan.get_head() == (board.width-2, ycoord+1)
                        and direction_of_enemy == "up"
                        and snake.length < board.samaritan.length
                        and board.is_valid_move("up")):
                        move = "up"
                elif (board.samaritan.get_head() == (board.width-2, ycoord+1)
                        and direction_of_enemy == "down"
                        and (len(board.get_neighbours(snake.get_head(),
                                                    snake)) <= 1)
                        and board.is_valid_move("down")):
                        move = "down"
                elif (board.samaritan.get_head() == (board.width-2, ycoord-1)
                        and direction_of_enemy == "up"
                        and (len(board.get_neighbours(snake.get_head(),
                                                    snake, 1)) <= 1)
                        and board.is_valid_move("up")):
                        move = "up"
        elif xcoord == 0:
            permissible_directions_for_samaritan.append("left")
            if my_direction in permissible_directions_for_samaritan:
                if (board.samaritan.get_head() == (1, ycoord)
                    and board.is_valid_move(direction_of_enemy)):
                    move = direction_of_enemy
                elif (board.samaritan.get_head() == (2, ycoord)
                        and board.is_valid_move("left")
                        and snake.length < board.samaritan.length):
                        move = "left"
                elif (board.samaritan.get_head() == (1, ycoord-1)
                        and direction_of_enemy == "down"
                        and snake.length < board.samaritan.length
                        and board.is_valid_move("down")):
                        move = "down"
                elif (board.samaritan.get_head() == (1, ycoord+1)
                        and direction_of_enemy == "up"
                        and snake.length < board.samaritan.length
                        and board.is_valid_move("up")):
                        move = "up"
                elif (board.samaritan.get_head() == (1, ycoord+1)
                        and direction_of_enemy == "down"
                        and (len(board.get_neighbours(snake.get_head(),
                                                    snake, 1)) <= 1)
                        and board.is_valid_move("down")):
                        move = "down"
                elif (board.samaritan.get_head() == (1, ycoord-1)
                        and direction_of_enemy == "up"
                        and (len(board.get_neighbours(snake.get_head(),
                                                    snake, 1)) <= 1)
                        and board.is_valid_move("up")):
                        move = "up"
        elif ycoord == board.width-1:
            permissible_directions_for_samaritan.append("down")
            if my_direction in permissible_directions_for_samaritan:
                if (board.samaritan.get_head() == (xcoord, board.height-2)
                    and board.is_valid_move(direction_of_enemy)):
                    move = direction_of_enemy
                elif (board.samaritan.get_head() == (xcoord, board.height-3)
                        and board.is_valid_move("down")
                        and snake.length < board.samaritan.length):
                        move = "down"
                elif (board.samaritan.get_head() == (xcoord-1, board.height-2)
                        and direction_of_enemy == "right"
                        and snake.length < board.samaritan.length
                        and board.is_valid_move("right")):
                        move = "right"
                elif (board.samaritan.get_head() == (xcoord+1, board.height-2)
                        and direction_of_enemy == "left"
                        and snake.length < board.samaritan.length
                        and board.is_valid_move("left")):
                        move = "left"
                elif (board.samaritan.get_head() == (xcoord+1, board.height-2)
                        and direction_of_enemy == "right"
                        and (len(board.get_neighbours(snake.get_head(),
                                                    snake, 1)) <= 1)
                        and board.is_valid_move("right")):
                        move = "right"
                elif (board.samaritan.get_head() == (xcoord-1, board.height-2)
                        and direction_of_enemy == "left"
                        and (len(board.get_neighbours(snake.get_head(),
                                                    snake, 1)) <= 1)
                        and board.is_valid_move("left")):
                        move = "left"
        elif ycoord == 0:
            permissible_directions_for_samaritan.append("up")
            if my_direction in permissible_directions_for_samaritan:
                if (board.samaritan.get_head() == (xcoord, 1)
                    and board.is_valid_move(direction_of_enemy)):
                    move = direction_of_enemy
                elif (board.samaritan.get_head() == (xcoord, 2)
                        and board.is_valid_move("up")
                        and snake.length < board.samaritan.length):
                        move = "up"
                elif (board.samaritan.get_head() == (xcoord-1, 1)
                        and direction_of_enemy == "right"
                        and snake.length < board.samaritan.length
                        and board.is_valid_move("right")):
                        move = "right"
                elif (board.samaritan.get_head() == (xcoord+1, 1)
                        and direction_of_enemy == "left"
                        and snake.length < board.samaritan.length
                        and board.is_valid_move("left")):
                        move = "left"
                elif (board.samaritan.get_head() == (xcoord+1, 1)
                        and direction_of_enemy == "right"
                        and (len(board.get_neighbours(snake.get_head(),
                                                    snake, 1)) <= 1)
                        and board.is_valid_move("right")):
                        move = "right"
                elif (board.samaritan.get_head() == (xcoord-1, 1)
                        and direction_of_enemy == "left"
                        and (len(board.get_neighbours(snake.get_head(),
                                                    snake, 1)) <= 1)
                        and board.is_valid_move("left")):
                        move = "left"
        if move is not None:
            return ("Trapping", move, snake.id)

    return (None, None, None)

def walling_enemies(board):
    """
    An attack tactic used by Samaritan used against enemy snakes. If there
    are nodes that Samaritan can restrict that would disallow the enemy from
    reaching his tail, Samaritan will wall the enemy off. This results in a
    lot of kills.
    """
    if len(board.other_snakes) == 0:
        return (None, None, None)
    neighbours = board.get_neighbours(board.samaritan.get_head(),
                                        board.samaritan)
    moves_to_edge = []
    for neighbour in neighbours:
        food_coordinates = board.foods[:]
        other_snakes = deepcopy(board.other_snakes)
        samaritan = deepcopy(board.samaritan)
        start = board.samaritan.get_head()
        destination = neighbour
        distance_to_edge = 0
        direction = translate(start, destination)
        valid_move = True
        path_to_edge = [board.samaritan.get_head()]
        foods = 0
        health_loss = 0
        while valid_move:
            target_x, target_y = destination
            if board.grid[target_y][target_x] != EMPTY_SPACE_MAKERS:
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
            if direction == "up":
                destination = (target_x, target_y-1)
            elif direction == "down":
                destination = (target_x, target_y+1)
            elif direction == "left":
                destination = (target_x-1, target_y)
            else:
                destination = (target_x+1, target_y)
            valid_move = board.is_valid_coordinate(destination[0],
                                                    destination[1],
                                                    board.samaritan,
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
                for x in range(int(distance_to_edge/2)-(foods-1)):
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
                for x in range(int(distance_to_edge/2)-foods):
                    samaritan.coordinates.pop()
                for xcoord, ycoord in path_to_edge[1:]:
                    samaritan.coordinates.insert(0, (xcoord, ycoord))

        new_board = Board(board.generate_data_dictionary(food_coordinates,
                                                other_snakes, samaritan))
        for x in range(len(new_board.other_snakes)):
            enemy_snake = board.other_snakes[x]
            future_enemy_snake = new_board.other_snakes[x]
            if (bfs(new_board, future_enemy_snake.get_head(),
                    future_enemy_snake.get_tail(), future_enemy_snake)
                    == (None, None)):
                if (bfs(board, enemy_snake.get_head(),
                            enemy_snake.get_tail(), enemy_snake)
                            == (None, None)):
                            continue
                can_wall_off_faster = True
                for node in path_to_edge[1:]:
                    my_distance_to_node = get_manhattan_distance(
                                            board.samaritan.get_head(), node)
                    enemy_distance_to_node = get_manhattan_distance(
                                                enemy_snake.get_head(), node)
                    if my_distance_to_node > enemy_distance_to_node:
                        can_wall_off_faster = False
                        break
                    elif (my_distance_to_node == enemy_distance_to_node
                            and enemy_snake.length >= board.samaritan.length):
                            can_wall_off_faster = False
                            break
                if can_wall_off_faster:
                    heappush(moves_to_edge, (len(path_to_edge),
                                                translate(
                                                    board.samaritan.get_head(),
                                                    path_to_edge[1]),
                                                enemy_snake.id))
    if len(moves_to_edge) == 0:
        return (None, None, None)
    x, move, enemy_id = heappop(moves_to_edge)
    return ("Walling off", move, enemy_id)


def get_best_enemy_attack(board, objective, move):
    """A paranoid move checker function used by my snake after it
    finds a move that it wants to execute. This function predicts how
    enemies will be able to hurt my snake by making an instance of
    our board where the enemy is the current my snake and we check if the
    enemy can trap, wall or corner the current my snake if it executes
    it's move.
    """
    if len(board.other_snakes) == 0:
        return (None, None, None)
    my_snake = deepcopy(board.my_snake)
    other_snakes = deepcopy(board.other_snakes)
    foods = board.foods[:]
    target_x, target_y = (None, None)
    if move == "up":
        head_x, head_y = my_snake.get_head()
        target_x, target_y = head_x, head_y-1
    elif move == "down":
        head_x, head_y = my_snake.get_head()
        target_x, target_y = head_x, head_y+1
    elif move == "left":
        head_x, head_y = my_snake.get_head()
        target_x, target_y = head_x-1, head_y
    else:
        head_x, head_y = my_snake.get_head()
        target_x, target_y = head_x+1, head_y

    my_snake.coordinates.insert(0, (target_x, target_y))
    my_snake.health -= 1
    if (target_x, target_y) in foods:
        foods.remove((target_x, target_y))
        my_snake.coordinates.append(my_snake.coordinates[-1])
        my_snake.health = 100
    my_snake.coordinates.pop()

    closest_snake = []
    for snake in other_snakes:
        neighbours = board.get_neighbours(snake.get_head(), snake)
        if len(neighbours) == 0:
            continue
        heappush(closest_snake, (get_manhattan_distance(snake.get_head(),
                                        my_snake.get_head()), snake))
    if len(closest_snake) == 0:
        return (None, None, None)
    all_enemy_threats = [heappop(closest_snake)]
    while len(closest_snake) != 0:
        prev_threat_distance, prev_threat_snake = all_enemy_threats[0]
        new_threat_distance, new_threat_snake = heappop(closest_snake)
        # if new_threat_distance - prev_threat_distance <= 3:
        all_enemy_threats.append((new_threat_distance, new_threat_snake))
        # else:
        #     break
    for x, snake in all_enemy_threats:
        new_main_snake = deepcopy(my_snake)
        new_other_snakes = deepcopy(other_snakes)
        new_foods = deepcopy(foods)
        for a_snake in new_other_snakes:
            if a_snake.id == snake.id:
                new_other_snakes.remove(a_snake)
                new_other_snakes = new_other_snakes + [new_main_snake]
                new_main_snake = a_snake
                neighbours = board.get_neighbours(a_snake.get_head(),
                                                    a_snake)
                if a_snake.health != 100:
                    a_snake.coordinates.pop()
                coordinates = a_snake.coordinates[:]
                for neighbour in neighbours:
                    a_snake.coordinates = coordinates[:]
                    if neighbour == new_other_snakes[-1].get_head():
                        if a_snake.length >= new_other_snakes[-1].length:
                            return ("Walling off", translate(
                                a_snake.get_head(), neighbour), a_snake.id)
                        else:
                            continue
                    if neighbour in foods:
                        new_foods.remove(neighbour)
                    a_snake.coordinates.insert(0, neighbour)
                    new_board = Board(board.generate_data_dictionary(
                            new_foods, new_other_snakes, new_main_snake))
                    objective, move, enemy_id = new_board.get_action()
                    if board.my_snake.id == enemy_id:
                        return (objective, move, snake.id)
    return (None, None, None)
