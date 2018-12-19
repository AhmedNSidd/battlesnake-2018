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
