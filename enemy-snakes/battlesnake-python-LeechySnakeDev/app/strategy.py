import random
from grid import Grid
from snakestuff import *

# Values to put in grid, priorities TBD
OPEN_SPACE = '.'
FOOD = 'F'
ME_HEAD = '@'
ME_SNAKE = '#'
ME_TAIL = '~'
EATABLE_HEAD_ZONE = 'H'
OTHER_HEAD = 'O'
OTHER_BODY = 'o'
MAYBE_GO = '+'
#EAT_THIS_HEAD = '$'
#ORTHOGONAL_HEAD = '+'
#DIAGONAL_HEAD = '-'
#CLOSE_TO_WALL = '?'
#TAIL = 'T'
#NO_GO = 'X'
#WALL = -1


def executeStrategy(data):
    height = data['height']
    width = data['width']
    ourSnakeCoords = getOurSnakeCoords(data)
    ourHead = getHeadCoord(ourSnakeCoords)
    mySnakeCoords = getOurSnakeCoords(data)
    mySnakeLength = len(mySnakeCoords)
    myTrajectory = getTrajectory(mySnakeCoords)
    health = getOurSnakeHealth(data)
    largerThanUs = snakesLargerThanUs(data)

    # Build Grid with symbols for different things
    symbolGrid = buildSymbolGrid(data)
    symbolGrid.printGrid()

    maxSnakeMove = symbolGrid.getPerimeter()

    # Build grid that contains the number of moves that it would take to get
    # somewhere.
    distanceGrid = Grid(width, height, maxSnakeMove)
    # Build grid that contains which direction the snake should go to get to
    # that coordinate.
    moveGrid = Grid(width, height, None)

    # Get lists of stuff on the board
    noGoCoordsList = symbolGrid.getListOfType([ME_HEAD, ME_SNAKE, OTHER_HEAD, OTHER_BODY])
    # Note: You would expect ME_TAIL to be in the maybeGoCoordsList, but then
    # it doesn't get a distance associated with it. However the tail will
    # disappear for one move when the snake eats food (2 tail coords so it gets
    # covered up by the body) so actually we should be ok.
    maybeGoCoordsList = symbolGrid.getListOfType([MAYBE_GO])
    # build grid using only safe moves
    barrierCoordsList = noGoCoordsList + maybeGoCoordsList

    #print("NO GO COORDS={}".format(noGoCoordsList))
    #print("MAYBE GO COORDS={}".format(maybeGoCoordsList))
    #print("BARRIER COORDS={}".format(barrierCoordsList))

    # build up the list of moves at each location
    fillDistanceAndMoveGrids(distanceGrid, moveGrid, ourHead, barrierCoordsList)
    # Useful grids for debugging
    #distanceGrid.printGrid(2)
    #moveGrid.printGrid(4)

    # build a dictionary of the number of open spaces available at each move
    moveDict = {}
    moveDict['left'] = countOpenSpaces(data, symbolGrid, (ourHead[0]-1, ourHead[1]), barrierCoordsList)
    moveDict['right'] = countOpenSpaces(data, symbolGrid, (ourHead[0]+1, ourHead[1]), barrierCoordsList)
    moveDict['up'] = countOpenSpaces(data, symbolGrid, (ourHead[0], ourHead[1]-1), barrierCoordsList)
    moveDict['down'] = countOpenSpaces(data, symbolGrid, (ourHead[0], ourHead[1]+1), barrierCoordsList)

    # Print grids for debugging
    #distanceGrid.printGrid(2)
    #moveGrid.printGrid()


    # Decide on a direction
    print("Health={}, Size={}, Trajectory={}, snakes larger than us={}".format(health, mySnakeLength, myTrajectory, largerThanUs))
    ourMove = decisionTree(data, symbolGrid, distanceGrid, moveGrid, moveDict)

    if ourMove is None:
        print("Reassessing with maybe-go coordinates as OK")
        # Better reassess with a smaller set of no-go coordinates
        distanceGrid = Grid(width, height, maxSnakeMove)
        moveGrid = Grid(width, height, None)
        fillDistanceAndMoveGrids(distanceGrid, moveGrid, ourHead, noGoCoordsList)
        # build a dictionary of the number of open spaces available at each move
        moveDict = {}
        moveDict['left'] = countOpenSpaces(data, symbolGrid, (ourHead[0]-1, ourHead[1]), noGoCoordsList)
        moveDict['right'] = countOpenSpaces(data, symbolGrid, (ourHead[0]+1, ourHead[1]), noGoCoordsList)
        moveDict['up'] = countOpenSpaces(data, symbolGrid, (ourHead[0], ourHead[1]-1), noGoCoordsList)
        moveDict['down'] = countOpenSpaces(data, symbolGrid, (ourHead[0], ourHead[1]+1), noGoCoordsList)
        #distanceGrid.printGrid(2)
        #moveGrid.printGrid(4)
        ourMove = decisionTree(data, symbolGrid, distanceGrid, moveGrid, moveDict)

    if ourMove is None:
        ourMove = panicDecisionTree(data, symbolGrid, distanceGrid, moveGrid, moveDict)


    print("Our move is {}".format(ourMove))
    return(ourMove)


def buildSymbolGrid(data):
    """
    Build a grid and use symbols to represent all the items in the grid.
    Then you can use getListOfType() to get all the coordinates for a list
    of symbols. You can also print this grid (super useful for debugging).

    The grid should be built up in layers from least dangerous (eg. food) to
    most dangerous (eg. snake body). That way, any additional zones put in
    place do not clobber no-go coordinates.
    """

    height = data['height']
    width = data['width']
    myId = data['you']
    mySnakeObj = getMySnakeObj(data)

    grid = Grid(width, height, OPEN_SPACE)

    # Food (very safe)
    grid.setList(data['food'], FOOD)

    # Area around Eatable Snake Heads (safe)
    for snake in data['snakes']:
        if(snake['id'] != myId):
            if(len(snake['coords']) < len(mySnakeObj['coords'])):
                # snake is shorter than us. Positions around the head are
                # the goal, not the head itself, as the snake's head will not
                # be there on the next move.
                orthList = grid.getOrthogonal(snake['coords'][0])
                grid.setList(orthList, EATABLE_HEAD_ZONE)

    # Special case when the tail is hidden by the body (2 tail coordinates)
    # immediately after eating food. So in that case, put tail markers around
    # where the tail would be (can't mark the tail because it's not going to
    # move for 1 turn.
    if mySnakeObj['coords'][-1] == mySnakeObj['coords'][-2]:
        orthList = grid.getOrthogonal(mySnakeObj['coords'][-1])
        grid.setList(orthList, ME_TAIL)

    # Area around Non-eatable Snake Heads (risky: maybe-go)
    for snake in data['snakes']:
        if(snake['id'] != myId):
            if(len(snake['coords']) >= len(mySnakeObj['coords'])):
                # Bigger snake
                # put a danger zone around the head of larger snake
                orthList = grid.getOrthogonal(snake['coords'][0])
                grid.setList(orthList, MAYBE_GO)

    # Snake heads and bodies (deadly: no-go) and tails (risky: maybe-go)
    # Must lay down after everything else, so it doesn't get overwritten
    for snake in data['snakes']:
        if(snake['id'] == myId):
            # Keep this order (tail, snake, head). There are 2 tail coordinates
            # at the same location when the snake eats food. So the tail is
            # temporarily hidden by the body which gets overlayed after the
            # tail has been placed. This is actually what we want so we don't
            # choose the tail spot after a snake has eaten something.
            grid.set(snake['coords'][-1], ME_TAIL)
            grid.setList(snake['coords'][1:-1], ME_SNAKE)
            grid.set(snake['coords'][0], ME_HEAD)
            #print("me snake coords={}".format(snake['coords']))
        else:
            grid.set(snake['coords'][-1], MAYBE_GO)
            grid.setList(snake['coords'][1:-1], OTHER_BODY)
            grid.set(snake['coords'][0], OTHER_HEAD)
            #print("snake coords={}".format(snake['coords']))

    # Strategy from watching snakes engage in risky behaviour:
    # Plot areas where a snake head is one space over from a wall or another
    # snake. This is a high risk area since the snake is making a tunne and
    # could suddenly turn and close the area off. Better to mark as maybe-go
    # to avoid entering a high risk area.
    noGoList = [None, ME_SNAKE, OTHER_HEAD, OTHER_BODY, MAYBE_GO]
    for head in grid.getListOfType([OTHER_HEAD]):
        # left
        if grid.get((head[0]-1, head[1])) not in noGoList and grid.get((head[0]-2, head[1])) in noGoList:
            grid.set((head[0]-1, head[1]), MAYBE_GO)
        # right
        if grid.get((head[0]+1, head[1])) not in noGoList and grid.get((head[0]+2, head[1])) in noGoList:
            grid.set((head[0]+1, head[1]), MAYBE_GO)
        # up
        if grid.get((head[0], head[1]-1)) not in noGoList and grid.get((head[0], head[1]-2)) in noGoList:
            grid.set((head[0], head[1]-1), MAYBE_GO)
        # down
        if grid.get((head[0], head[1]+1)) not in noGoList and grid.get((head[0], head[1]+2)) in noGoList:
            grid.set((head[0], head[1]+1), MAYBE_GO)

    return(grid)


def fillDistanceAndMoveGrids(distanceGrid, moveGrid, startingCoord, noGoCoords):
    maxMoves = distanceGrid.getPerimeter()

    # make a list of all the coordinates to try this round
    # remove them if they are one of the no go coordinates
    stepDict = distanceGrid.getOrthogonalDict(startingCoord, noGoCoords)
    #print("stepDict={}".format(stepDict))

    for stepNumber in range(1, maxMoves):
        coordsForNextStep = {}
        #print("step {}: {}".format(stepNumber, stepDict))
        for stepCoord, move in stepDict.items():
            if distanceGrid.get(stepCoord) == maxMoves:
                distanceGrid.set(stepCoord, stepNumber)
                # update move grid
                moveGrid.set(stepCoord, move)
                # keep this coordinate for the next step
                coordsForNextStep[stepCoord] = move

        if len(coordsForNextStep) == 0:
            break
        # Get the coordinates for the next step
        for coord, move in coordsForNextStep.items():
            tempList = distanceGrid.getOrthogonal(coord, noGoCoords)
            stepDict.update({c:move for c in tempList})

def countOpenSpaces(data, symbolGrid, startingCoord, noGoCoords):
    """
    Count the number of spaces the snake could reach starting from the
    starting coordinate. Provide the list of barriers in the noGoCoords.

    The algorithm has some added complexity because if our tail is in the open
    space we are looking at, then we will always have an escape. That makes
    the space basically safe.
    """
    if startingCoord in noGoCoords:
        return(0)

    counterGrid = Grid(data['width'], data['height'], 0)
    if counterGrid.get(startingCoord) == None: # outside the grid
        return(0)

    # Set starting coordinate as valid
    counterGrid.set(startingCoord, 1)

    stepList = counterGrid.getOrthogonal(startingCoord, noGoCoords)

    for _ in range(counterGrid.getPerimeter()):
        tempList = []
        for stepCoord in stepList:
            if stepCoord not in noGoCoords and counterGrid.get(stepCoord) == 0:
                counterGrid.set(stepCoord, 1)
                tempList.append(stepCoord)
        stepList = tempList
        # if no coordinates to check out then we're done.
        if len(stepList) > 0:
            stepList = counterGrid.getOrthogonalFromList(stepList, noGoCoords)
        else:
            break
    numOpenSpaces = counterGrid.count(1)
    #counterGrid.printGrid()

    # special exception for our tail. If the tail is part of the open spaces
    # and the number of open spaces is shorter than our snake then set the
    # number of spaces to our snake length.
    ourSnakeLength = len(getOurSnakeCoords(data))
    if ourSnakeLength > numOpenSpaces:
        tailList = symbolGrid.getListOfType([ME_TAIL])
        openSpaceList = counterGrid.getListOfType([1])
        # is any tail coordinate in the open space coordinates?
        if len(set(tailList) & set(openSpaceList)) > 0:
            numOpenSpaces = ourSnakeLength

    return(numOpenSpaces)



def decisionTree(data, symbolGrid, distanceGrid, moveGrid, moveDict):
    """
    Decisions for Snake:
    - Goals are: Food, Heads of smaller snakes, Chase our own tail
    - The direction is determined by whatever is the top goal for this round
    - The top priority is food if below the health threshold
    - The second priority is go for heads of smaller snakes
    - If health is good and no smaller snakes then chase tail
    - If none of the goals can be reached then see if any of our directions are
      in the "MAYBE_GO" list, if so, take it.
    - If there is no move available, then make a random choice and die.
    """
    mySnakeCoords = getOurSnakeCoords(data)
    mySnakeLength = len(mySnakeCoords)
    ourMove = None
    health = getOurSnakeHealth(data)
    largerThanUs = snakesLargerThanUs(data)
    preferredMoveList = sorted(moveDict, key=moveDict.get, reverse=True)
    preferredMoveListRanked = getPreferredMoveListRanked(moveDict)

    # Useful runtime stats
    print("moveDict={}, rank={}".format(moveDict, preferredMoveListRanked))

    # stay healthy, try to be biggest snake, eat smaller snakes
    if ourMove == None:
        if health < 75:
            # must maintain health, only go for food
            nearestFoodList = getNearestOfType([FOOD], symbolGrid, distanceGrid)
            decisionString = "Eat food"
        elif largerThanUs == 0:
            # we're big and well feed, now get the snakes!
            nearestFoodList = getNearestOfType([EATABLE_HEAD_ZONE], symbolGrid, distanceGrid)
            decisionString = "Eat snakes"
        else:
            # heath is good, snack on snakes while growing
            nearestFoodList = getNearestOfType([FOOD, EATABLE_HEAD_ZONE], symbolGrid, distanceGrid)
            decisionString = "Eat food and snakes"

        numFood = len(nearestFoodList)
        #print("nearestFoodList={}".format(nearestFoodList))
        if numFood == 0:
            #print("No Food! Moving on...")
            pass
        elif numFood == 1:
            ourMove = moveGrid.get(nearestFoodList[0])
            print("Decision: {}: {}, distance={}, ourMove={}".format(decisionString, nearestFoodList[0], distanceGrid.get(nearestFoodList[0]), moveGrid.get(nearestFoodList[0])))
        else: # special case: more than one food at equal distance!
            moveList = [moveGrid.get(coord) for coord in nearestFoodList]
            for preferredmove in preferredMoveList:
                if preferredmove in moveList:
                    ourMove = preferredmove
                    break
            print("Decision: {}: {}, distance={}, ourMove={}".format(decisionString, nearestFoodList, distanceGrid.get(nearestFoodList[0]), ourMove))

        # Safety check: how many spaces are we moving into.
        if ourMove != None:
            if moveDict[ourMove] < mySnakeLength:
                print("Safety override for move {}! snake length={}, spaces available={}".format(ourMove, mySnakeLength, moveDict[ourMove]))
                ourMove = None

    # eating didn't work out - chase tail!
    if ourMove == None:
        myTailList = getNearestOfType([ME_TAIL], symbolGrid, distanceGrid)
        if len(myTailList) > 0:
            myTail = random.choice(myTailList)
            ourMove = moveGrid.get(myTail)
            print("Decision: Chase tail at {}, distance={}, ourMove={}".format(myTail, distanceGrid.get(myTail), ourMove))

    # Can't find tail - move wherever there is space
    # First check the moveDict to see if any direction shows available moves.
    # Go with whichever direction has the most coordinates marked.
    # Prefer current trajectory over random direction (testing this strategy)
    if ourMove == None:
        # make sure the top rated direction has at least one position to move
        # into.
        if moveDict[preferredMoveList[0]] >= mySnakeLength:
            ourMove = random.choice(preferredMoveListRanked[0])
            print("Decision: go with majority (random). Spaces={}, move={}".format(moveDict[preferredMoveList[0]], ourMove))

    return(ourMove)


def panicDecisionTree(data, symbolGrid, distanceGrid, moveGrid, moveDict):
    # Nothing within reach! Start to panic.
    ourMove = None
    preferredMoveList = sorted(moveDict, key=moveDict.get, reverse=True)
    preferredMoveListRanked = getPreferredMoveListRanked(moveDict)

    # Go with whichever direction has the most coordinates marked.
    if ourMove == None:
        # make sure the top rated direction has at least one position to move
        # into.
        if moveDict[preferredMoveList[0]] > 0:
            ourMove = random.choice(preferredMoveListRanked[0])
            print("Decision: go with what's left (random). Spaces={}, move={}".format(moveDict[preferredMoveList[0]], ourMove))


    # If we get here, then we should be panicing.
    # At this point, go to the list of "maybe go" positions. This is a last
    # resort because moving into these positions are high risk (eg. moving
    # beside the head of a larger snake). But if no other choice, then a
    # maybe-go is better than a random fate.
    # Prefer current trajectory over random direction (testing this strategy)
    if ourMove == None:
        ourSnakeHead = getHeadCoord(getOurSnakeCoords(data))
        orthogonalList = symbolGrid.getOrthogonal(ourSnakeHead)
        maybeGoCoordsList = symbolGrid.getListOfType([ME_TAIL, MAYBE_GO])
        possibleCoordinates = [a for a in orthogonalList if a in maybeGoCoordsList]
        possibleDirections = [getTrajectory([coord, ourSnakeHead]) for coord in possibleCoordinates]
        if len(possibleDirections) > 0:
            ourMove = random.choice(possibleDirections)
            print("Decision: No good options. Resort to the Maybe-go list (random), move={}".format(ourMove))

    # Full panic, we're probably going to die. Keep on our trajectory, so we
    # at least don't turn in on ourself.
    if ourMove == None:
        #directions = ['up', 'down', 'left', 'right']
        #ourMove = random.choice(directions)
        ourMove = getTrajectory(getOurSnakeCoords(data))
        print("Descision: PANIC! No moves available! Going straight ahead: {}".format(ourMove))

    return(ourMove)


def getNearestOfType(thingsToFindList, symbolGrid, distanceGrid):
    """
    Pass in an array of things to find in the symbol table, and return an
    array of coordinates of the nearest things. Normally there will be an arry
    with 1 coordinate, but in some cases there will be 2 things of equal
    distance away. When that happens, further decisions need to be made as
    to which thing to head towards.
    """
    maxSnakeMove = symbolGrid.getPerimeter()
    foundThingsList = symbolGrid.getListOfType(thingsToFindList)
    distanceDict = {} # key=coordinate, value=distance from head
    nearestThingsCoordsList = []
    for coord in foundThingsList:
        coordDistance = distanceGrid.get(coord)
        if coordDistance < maxSnakeMove: # check for unobtainium
            distanceDict[coord] = coordDistance
    #print("distanceDict={}".format(distanceDict))
    # klunktastic
    sortedCoords = sorted(distanceDict, key=distanceDict.get)
    sortedDistances = sorted(distanceDict.values())
    #print("sortedCoords={}, sortedDistances={}".format(sortedCoords, sortedDistances))
    shortestDistance = None
    for i in range(len(sortedCoords)):
        if shortestDistance == None or sortedDistances[i] == shortestDistance:
            nearestThingsCoordsList.append(sortedCoords[i])
            shortestDistance = sortedDistances[i]
    return(nearestThingsCoordsList)


def getPreferredMoveListRanked(moveDict):
    """
    Returns a list of lists of the moves in order of the number of spaces
    available. Eg. {'left': 8, 'right': 15, 'up': 15, 'down': 0}
    will return [['right', 'up'], ['left'], ['down']]
    This thing inverts the dictionary and the reverse sorts.
    """
    temp = {}
    for k, v in moveDict.items():
        temp[v] = temp.get(v, [])
        temp[v].append(k)
    preferredList = [temp[k] for k in sorted(temp, reverse=True)]
    return(preferredList)
