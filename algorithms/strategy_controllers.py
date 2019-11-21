class Strategy():

    @staticmethod
    def get_action():
        raise NotImplementedError("This has not yet been implemented.")

class EfficientStrategy(Strategy):

    @staticmethod
    def get_action(board, main_snake):
        return ("Can you hear me?", "left")