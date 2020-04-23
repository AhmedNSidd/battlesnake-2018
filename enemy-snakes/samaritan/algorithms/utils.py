def get_manhattan_distance(start, target):
    '''Returns the distance from start node to target node
    '''
    return abs(start[0] - target[0]) + abs(start[1] - target[1])


def translate(start, target):
    '''
    Given a start node and target node, it finds out what direction to head
    to to get to the target.
    '''
    if start[0] == target[0]:
        if start[1] > target[1]:
            return "up"
        elif start[1] < target[1]:
            return "down"
    elif start[1] == target[1]:
        if start[0] > target[0]:
            return "left"
        elif start[0] < target[0]:
            return "right"

def convert_2018_api_to_2019(api_2018):
    width = api_2018["width"]
    height = api_2018["height"]
    foods = api_2018["food"]["data"]
    all_snakes = api_2018["snakes"]["data"]
    you = api_2018["you"]
    api_2019 = {
        "board": {
            "food": foods,
            "width": width,
            "height": height,
            "snakes": []
        },
        "you": {
            "id": you["id"],
            "name": you["name"],
            "health": you["health"],
            "body": you["body"]["data"]
        }
    }
    for snake in all_snakes:
        api_2019["board"]["snakes"].append({
            "id": snake["id"],
            "name": snake["name"],
            "health": snake["health"],
            "body": snake["body"]["data"]
        })
    return api_2019
