from .routes import find_path_to_my_tail, sp_find_path_to_food
from .board import generate_new_board_with_move


class Strategy():

    @staticmethod
    def get_action():
        raise NotImplementedError("This has not yet been implemented.")

class SmallSnakeStrategy(Strategy):

    @staticmethod
    def get_action(board, main_snake):
        if not board.other_snakes:
            return SpTailChasingStrategy.get_action(board, main_snake)
        else:
            return ("Can You Hear Me?", "left")

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
        tail_obj, tail_move = find_path_to_my_tail(board)
        return translate(board.my_snak)
