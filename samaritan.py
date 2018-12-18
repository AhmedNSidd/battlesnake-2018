import bottle
import os
import random
from algorithms.board import Board
import time

@bottle.route('/')
def static():
    return "the server is running"

@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')

@bottle.post('/start')
def start():
    data = bottle.request.json

    return {
        "color": "#FF0000",
        "secondary_color": "#00FF00",
        "head_url": "https://i.ytimg.com/vi/er3BMWuf310/maxresdefault.jpg",
        "taunt": "Calculated.",
        "head_type": "pixel",
        "tail_type": "pixel"
        }

@bottle.post('/move')
def move():
    data = bottle.request.json
    environment = Board(data)
    start = time.time()
    objective, action = environment.my_snake.get_action(environment)
    print (time.time() - start) * 1000, "ms"
    return {
        'move': action,
        'taunt': "Can you hear me?"
    }

@bottle.post('/end')
def end():
    pass

# Expose WSGI app (so gunicorn can find it)

application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8099'),
        debug = True)
