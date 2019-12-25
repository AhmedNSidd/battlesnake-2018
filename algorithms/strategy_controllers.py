from .routes import find_path_to_my_tail, sp_find_path_to_food, longest_path_to_tail, go_to_least_dense_region
from .generators import generate_new_board_with_move


class Strategy():

    @staticmethod
    def get_action():
        raise NotImplementedError("This has not yet been implemented.")

class SmallSnakeStrategy(Strategy):

    @staticmethod
    def get_action(board, main_snake):
        if not board.other_snakes:
            return SpTailChasingStrategy.get_action(board, main_snake)
        elif len(board.other_snakes) == 1:
            return ("Can You Hear Me?", "left")
        else:
            # Small snake strategy
            # go for safe food if possible
            # if health is low
            #   go for risky food.
            # go to least dense region
            # if stil no objective, chase tail
            return go_to_least_dense_region(board)


class SpTailChasingStrategy(Strategy):
    """
    This is a singleplayer strategy the functioning of which is well
    documented in ideal_snake.md as strategy #1 for singleplayer snake games.
    """

    @staticmethod
    def get_action(board, main_snake):
        """
        Keep chasing tail until we can't anymore (otherwise we'd die). After,
        go get food.
        """
        curr_food_obj, curr_food_move = sp_find_path_to_food(board)
        if curr_food_obj != None:
            return (curr_food_obj, curr_food_move)
        return longest_path_to_tail(board)
        # tail_obj, tail_move = find_path_to_my_tail(board)
        # print("tail move is {}".format(tail_move))
        # if tail_obj:
        #     new_board = generate_new_board_with_move(board, tail_move)
        #     next_food_obj, next_food_move = sp_find_path_to_food(new_board)
        #     print("next food move is {}".format(next_food_move))
        #     if next_food_obj == None:
        #         curr_food_obj, curr_food_move = sp_find_path_to_food(board)
        #         print("curr food move is {}".format(curr_food_move))
        #         if curr_food_obj == None:
        #             return (tail_obj, tail_move)
        #         return (curr_food_obj, curr_food_move)
        #     else:
        #         return (tail_obj, tail_move)
        # curr_food_obj, curr_food_move = sp_find_path_to_food(board)
        # print("curr food move is {}".format(curr_food_move))
        # if curr_food_obj != None:
        #     return (curr_food_obj, curr_food_move)
        # return longest_path_to_tail(board)
