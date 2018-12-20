# Move Request Converter -- Jon Knoll (aka LeechySnake) (C)2018
# This converts the BattleSnake move request from the 2018 format to the 2017
# format, so you can run your 2017 battlensake on the 2018 server!
# There's nothing special about this code so it is free to use.


def move2018to2017(data):
    """
    convert 2018 move request to the 2017 format
    """
    data2017 = convertObject(data)
    return(data2017)


def convertPoint(obj):
    return [obj['x'], obj['y']]


def convertList(obj):
    myList = []
    for item in obj['data']:
        myList.append(convertObject(item))
    return myList


def convertSnake(obj):
    dict2017 = {}
    dict2017['taunt'] = obj['taunt']
    dict2017['name'] = obj['name']
    dict2017['id'] = obj['id']
    dict2017['health_points'] = obj['health']
    dict2017['coords'] = convertList(obj['body'])
    return dict2017


def convertWorld(obj):
    dict2017 = {}
    meSnake = convertSnake(obj['you'])
    dict2017['you'] = meSnake['id']
    dict2017['width'] = obj['width']
    dict2017['turn'] = obj['turn']
    dict2017['snakes'] = convertList(obj['snakes'])
    dict2017['height'] = obj['height']
    dict2017['game_id'] = obj['id']
    dict2017['food'] = convertList(obj['food'])
    dict2017['dead_snakes'] = []
    return dict2017

def convertObject(obj):
    type = obj['object']
    
    if type == 'point':
        return convertPoint(obj)
        
    if type == 'list':
        return convertList(obj)
    
    if type == 'snake':
        return convertSnake(obj)
    
    if type == 'world':
        return convertWorld(obj)
    
    else:
        return obj
    
