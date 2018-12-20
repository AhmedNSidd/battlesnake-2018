from __future__ import print_function

class Grid(object):
    def __init__(self, width, height, initialValue=None):
        self.width = width
        self.height = height
        self.grid = [[initialValue for _ in range(width)] for _ in range(height)]

    def set(self, coord, val):
        self.grid[coord[1]][coord[0]] = val

    def get(self, coord):
        if((coord[0] >= self.width) or (coord[0] < 0)):
            return(None)
        elif((coord[1] >= self.height) or (coord[1] < 0)):
            return(None)
        return self.grid[coord[1]][coord[0]]

    def setList(self, coordsList, val):
        for coord in coordsList:
            self.set(coord, val)

    def getListOfType(self, typeList):
        coordsList = []
        for y in range(self.height):
            for x in range(self.width):
                thingAtCoord = self.get((x, y))
                if(thingAtCoord in typeList):
                    coordsList.append((x, y))
        return(coordsList)

    def getOrthogonal(self, coord, noGoList=[]):
        coordsList = []
        right = (coord[0]+1, coord[1])
        left = (coord[0]-1, coord[1])
        down = (coord[0], coord[1]+1)
        up = (coord[0], coord[1]-1)
        if(self.get(right) != None) and (right not in noGoList):
            coordsList.append(right)
        if(self.get(left) != None) and (left not in noGoList):
            coordsList.append(left)
        if(self.get(down) != None) and (down not in noGoList):
            coordsList.append(down)
        if(self.get(up) != None) and (up not in noGoList):
            coordsList.append(up)
        return(coordsList)

    def getOrthogonalDict(self, coord, noGoList=[]):
        """
        Return the orthogonal directions from a given coordinate as a
        dictionary: keys=coordinates, values=direction strings (eg. 'left')
        """
        coordsDict = {}
        right = (coord[0]+1, coord[1])
        left = (coord[0]-1, coord[1])
        down = (coord[0], coord[1]+1)
        up = (coord[0], coord[1]-1)
        if(self.get(right) != None) and (right not in noGoList):
            coordsDict[right] = 'right'
        if(self.get(left) != None) and (left not in noGoList):
            coordsDict[left] = 'left'
        if(self.get(down) != None) and (down not in noGoList):
            coordsDict[down] = 'down'
        if(self.get(up) != None) and (up not in noGoList):
            coordsDict[up] = 'up'
        return(coordsDict)

    def getOrthogonalFromList(self, coordsList, noGoList=[]):
        orthCoords = []
        for coord in coordsList:
            orthCoords += self.getOrthogonal(coord, noGoList)
        return(set(orthCoords))


    def getDiagonal(self, coord):
        coordsList = []
        topLeft = (coord[0]-1, coord[1]-1)
        bottomLeft = (coord[0]-1, coord[1]+1)
        topRight = (coord[0]+1, coord[1]-1)
        bottomRight = (coord[0]+1, coord[1]+1)
        if(self.get(topLeft) != None):
            coordsList.append(topLeft)
        if(self.get(bottomLeft) != None):
            coordsList.append(bottomLeft)
        if(self.get(topRight) != None):
            coordsList.append(topRight)
        if(self.get(bottomRight) != None):
            coordsList.append(bottomRight)
        return(coordsList)

    def add(self, coord, val):
        origVal = self.get(coord)
        newVal = origVal + val
        self.set(coord, newVal)
        return(newVal)

    def getPerimeter(self):
        """
        This is the theoretical maximum number of moves that it could take to
        get to a location (all the way around the outside perimeter). Using this
        number instead of like MAX_INT
        """
        return((self.height + self.width) * 2)

    def printGrid(self, columnWidth=1):
        print("GRID: ({} x {})".format(self.width, self.height))
        for y in range(self.height):
            #print("y={}".format(y))
            for x in range(self.width):
                if(self.get((x,y)) == None):
                    print("{:{width}}".format(0, width=columnWidth), end='')
                else:
                    print("{:{width}}".format(self.get((x,y)), width=columnWidth), end='')
            print("")

    def count(self, thingToLookFor):
        """
        count the number of grid positions that have thingToLookFor
        """
        return(sum(x.count(thingToLookFor) for x in self.grid))


if __name__=='__main__':
    testGrid = Grid(5,10)
    testGrid.set([0,2], 22)
    testGrid.set([4,0], 44)
    testGrid.print2()
    testGrid.printGrid()
