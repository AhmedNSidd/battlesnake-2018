from .routes import (find_path_to_my_tail, sp_find_path_to_food,
                     sp_path_to_tail, go_to_least_dense_region,
                     find_path_to_food, get_safest_move)
from .attack_algorithms import (cornering_enemies, walling_enemies,
                                trapping_enemies, attack_enemy,
                                get_best_enemy_attack)
from .generators import generate_new_board_with_move


class Controller():

    @staticmethod
    def get_action(board):
        for x in range(3):
            objective, move = BigSnakeStrategy.get_action(board)
            if objective == None:
                objective, move = get_safest_move(board)
                return (objective, move)
            e_objective, e_move, e_id = get_best_enemy_attack(board, move)
            if e_objective == None:
                return (objective, move)
            board.bad_moves.append(move)
        objective, move = get_safest_move(board)
        return (objective, move)


class BigSnakeStrategy():

    @staticmethod
    def get_action(board):
        if not board.other_snakes:
            curr_food_obj, curr_food_move = sp_find_path_to_food(board)
            if curr_food_obj != None:
                return (curr_food_obj, curr_food_move)
            return sp_path_to_tail(board)
        elif len(board.other_snakes) == 1:
            objective, move, e_id = cornering_enemies(board)
            if objective != None:
                return (objective, move)
            objective, move, e_id = walling_enemies(board)
            if objective != None:
                return (objective, move)
            objective, move, e_id = trapping_enemies(board)
            if objective != None:
                return (objective, move)
            if board.is_my_snake_biggest():
                objective, move = attack_enemy(board)
                if objective != None:
                    return (objective, move)
            objective, move = find_path_to_food(board)
            if objective != None:
                return (objective, move)
            objective, move = find_path_to_my_tail(board)
            return (objective, move)
        else:
            if board.my_snake.health <= 30:
                objective, move = find_path_to_food(board)
                if objective is not None:
                    return (objective, move)
            objective, move = get_safest_move(board)
            return (objective, move)