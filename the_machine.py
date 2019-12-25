import bottle
import os
from algorithms.board import Board
from time import time
from api import ping_response, end_response
from algorithms.utils import convert_2018_api_to_2019
from algorithms.strategy_controllers import SmallSnakeStrategy

@bottle.route("/")
def static():
    """
    When someone does a get request on the application, it"s going to say
    that it's running.
    """
    return "<!DOCTYPE html><html><body><style>h1, h3 {color: red;font-family:"\
    "monospace;}</style><h1>Can You Hear Me?</h1><h3>A snake created"\
    " by Ahmed Siddiqui</h3></body></html>"

@bottle.post("/start")
def start():
    """
    When a game starts, this endpoint is called and it gives the customization
    information for The Machine.
    """
    # TODO: Change customization info from samaritan to the machine
    return {
        "color": "#FFFFFF",
        "secondary_color": "#ededed",
        "head_url": "https://i.ytimg.com/vi/XR9KGlTgbAs/maxresdefault.jpg",
        "taunt": "Calculated.",
        "head_type": "smile",
        "tail_type": "freckled"
        }

@bottle.post("/move")
def move():
    """
    When a game has started and the game server wants to know which direction
    I want to move in, this endpoint is hit as a POST request with data telling
    us about the game state (what the board looks like). We then figure out
    what move and taunt we want to return by creating an instance of the game
    state and getting an action for our snake, The Machine.
    """
    data = bottle.request.json
    # Comment the line below for 2019 game server, uncomment for 2018.
    data = convert_2018_api_to_2019(data)
    board = Board(data)
    start = time()
    objective, move = SmallSnakeStrategy.get_action(board, board.my_snake)
    print("Time to get move: {}ms".format((time() - start) * 1000))
    print(objective, move)
    return {
        "move": move,
        "taunt": objective
        }

@bottle.post("/end")
def end():
    return end_response()

@bottle.post("/ping")
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

application = bottle.default_app()

if __name__ == "__main__":
    if os.environ.get("APP_LOCATION") == "heroku":
        bottle.run(
            application,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 5000))
        )
    else:
        bottle.run(
            application,
            host=os.getenv("IP", "0.0.0.0"),
            port=os.getenv("PORT", "9226"),
            debug=True)
