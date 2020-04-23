import bottle
import os
import sys
import strategy
from moveconvert import move2018to2017
#from app.scenarios import *


# Running battle_snake locally (Feb 2018)
# Install virtualbox
# You probably need to install Vagrant, but I'm not sure what it does.
# Install Docker, which should install kitematic.
# Run kitematic and search for the battlesnake container.
# And Run
# If the docker container cannot connect locally, then make sure you either
# a) turn off the McAfee firewall (but it will just turn back on in 15min)
# b) use one of the ports that it has open (any port listed as "local" with
#    no other caveates. The list as of Feb 2018 is:
#    20-21, 111, 502, 4987, 4988-4989, 5500-5509, 6001-6002, 8282, 13777
# ALSO: make sure the URL you give the server doesn't have a trailing slash!
# or you will have to add a slash to all the bottle post requests



##############################################
# WEB CALLS
#############################################


@bottle.route('/static/<path:path>')
def static(path):
    print("STATIC request")
    print("path={}".format(path))
    return bottle.static_file(path, root='static')


@bottle.post('/start')
def start():
    print("START request")
    data = bottle.request.json

    print("\nSNAKE START!")
    for k,v in data.items():
        print("{}={}".format(k,v))


    #game_id = data['game_id']
    #board_width = data['width']
    #board_height = data['height']
    print("URL Parts:")
    #for k,v in bottle.request.urlparts.items():
    #    print("{}={}".format(k, v))
    print(bottle.request.urlparts)

    head_url = "{}://{}/static/leechy.png".format(
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    return {
        # What color your snake should be on the board.
        # Accepts any valid CSS color.
        # https://developer.mozilla.org/en-US/docs/Web/CSS/color
        'color': '#3F3F3F',
        'name': "Leechy",

        # URL of the image to display as your avatar.
        'head_url': head_url,
        'taunt': "No room for error", #'{} ({}x{})'.format(game_id, board_width, board_height),
        'head_type': 'smile',
        'tail_type': 'freckled',
        'secondary_color': '#ff00ff',
    }


@bottle.post('/move')
def move():
    print("MOVE request")
    data = bottle.request.json

    data = move2018to2017(data)

    ourMove = strategy.executeStrategy(data)
    return {
        'move': ourMove,
        'taunt': ourMove
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()
if __name__ == '__main__':
    print("RUNNING MAIN... STARTING BOTTLE...")
    print(sys.version)
    # Using one of the allowed TCP ports in the McAfee firewall so it doesn't block traffic
    # As of Feb 2018 we can use: 20-21, 111, 502, 4987, 4988-4989, 5500-5509,
    # 6001-6002, 8282, 13777
    # ALSO: make sure the URL you give the server doesn't have a trailing slash!
    bottle.run(application, host=os.getenv('IP', '0.0.0.0'), port=os.getenv('PORT', '9080'))
    #strategy.executeStrategy(move2018to2017(test8))

#curl http://192.168.99.1:8080
