
def getMySnakeObj(data):
    myId = data['you']

    # fill with the living snakes
    for snake in data['snakes']:
        theId = snake['id']
        if(theId == myId):
            return(snake)
        
def getOurSnakeCoords(data):
    myId = data['you']
    for snake in data['snakes']:
        if(snake['id'] == myId):
            return(snake['coords'])

def getHeadCoord(snakeCoordsList):
    return(snakeCoordsList[0])

def getTailCoord(snakeCoordsList):
    return(snakeCoordsList[-1])

def getOurSnakeHealth(data):
    return(getMySnakeObj(data)['health_points'])

def getOtherSnakeCoordsList(data):
    myId = data['you']
    snakeList = []
    for snake in data['snakes']:
        if(snake['id'] != myId):
            snakeList.append(snake['coords'])
    return(snakeList)

def getTrajectory(snakeCoordsList):
    xh = snakeCoordsList[0][0]
    yh = snakeCoordsList[0][1]
    x1 = snakeCoordsList[1][0]
    y1 = snakeCoordsList[1][1]
    if(xh > x1):
        return('right')
    elif(xh < x1):
        return('left')
    elif(yh > y1):
        return('down')
    else:
        return('up')

def compareSnake(snakeA, snakeB):
    lenA = len(snakeA['coords'])
    lenB = len(snakeB['coords'])
    if lenA > lenB:
        return(">")
    elif lenA < lenB:
        return("<")
    else:
        return("=")
    
def snakesLargerThanUs(data):
    ourSnake = getOurSnakeCoords(data)
    otherSnakesList = getOtherSnakeCoordsList(data)
    largerSnakes = 0
    for otherSnake in otherSnakesList:
        if len(ourSnake) <= len(otherSnake):
            largerSnakes += 1
    return(largerSnakes)
    