import bottle
import os
from algorithms.board import Board
from time import time
from api import ping_response, end_response
from algorithms.utils import convert_2018_api_to_2019

@bottle.route('/')
def static():
    '''
    When someone does a get request on the application, it's going to say
    that it's running.
    '''
    return "<!DOCTYPE html><html><body><style>h1, h3 {color: red;font-family:"\
    "monospace;}</style><h1>Samaritan is running...</h1><h3>A snake created"\
    " by Ahmed Siddiqui</h3></body></html>"

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')

@bottle.post('/start')
def start():
    '''
    When a game starts, this endpoint is called and it gives the customization
    information for Samaritan. It also starts writing to the runtime text file.
    '''
    return {
        "color": "#D14F52",
        "secondary_color": "#ededed",
        "head_url": "https://i.ytimg.com/vi/er3BMWuf310/maxresdefault.jpg",
        "taunt": "Calculated.",
        "head_type": "smile",
        "tail_type": "freckled"
        }

@bottle.post('/move')
def move():
    '''
    When a game has started and the game server wants to know which direction
    I want to move in, this endpoint is hit as a POST request with data telling
    us about the game state (what the board looks like). We then figure out
    what move and taunt we want to return by creating an instance of the game
    state and getting an action for our snake, Samaritan.
    '''
    data = bottle.request.json
    # Comment the line below for 2019 game server, uncomment for 2018.
    data = convert_2018_api_to_2019(data)
    environment = Board(data)
    start = time()
    objective, action = environment.get_action()
    print("Time to get move: {}ms".format((time() - start) * 1000))
    print(objective, action)
    return {
        'move': action,
        'taunt': objective
        }

@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """

    return end_response()

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

application = bottle.default_app()

if __name__ == '__main__':
    if os.environ.get('APP_LOCATION') == 'heroku':
        bottle.run(
            application,
            host="0.0.0.0",
            port=int(os.environ.get("PORT", 5000))
        )
    else:
        bottle.run(
            application,
            host=os.getenv('IP', '0.0.0.0'),
            port=os.getenv('PORT', '8099'),
            debug = True)
