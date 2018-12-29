class Snake(object):
    '''This snake class is used to create snake objects to store basic info on
    them. For Samaritan, we can also get an action based on a given board.
    '''

    def __init__(self, s_id, list_of_coords, health, length):
        '''Initializes snake object with important instance variables.
        '''
        self.id = s_id
        self.coordinates = list_of_coords
        self.health = health
        self.length = length

    def get_head(self):
        '''Returns head coords of Snake object
        '''
        return self.coordinates[0]

    def get_tail(self):
        '''Returns tail coords of Snake object
        '''
        return self.coordinates[-1]

    def how_long_to_grow(self):
        '''
        If the coordinates of the last indices of the snake are the same,
        that means that the snake is still growing out of his tail. This
        function calculates how long it will it take for the tail node to
        disappear
        '''
        time_to_disappear = 0
        snake_tail = self.get_tail()
        for snake_node in reversed(self.coordinates[:-1]):
            if snake_node == snake_tail:
                time_to_disappear += 1
        return time_to_disappear

    def coordinates_with_no_repeats(self):
        '''Returns a list of coordinates with no repeat nodes e.g. when a snake
        is still growing out of it's tail.
        '''
        snake_coordinates = [self.get_head()]
        for node in self.coordinates:
            if node != snake_coordinates[-1]:
                snake_coordinates.append(node)
        return snake_coordinates




        '''
        If health (< 60) or length is low:
        1st priority: Food (A* + BFS) (If you're going to die when getting a food then go to another food)
        2nd priority: If no food, My Tail (A*)
        3rd priority: If not my tail, then Enemy's tail (A*)
        4th priority: At this point, i'm probably trapped, so stall until an exit opens. (???)

        If health and length is fine:
        1st priority: Tail (A*)
        2nd priority: Enemy's tail (A*)
        3rd priority: At this point, i'm probably trapped, so stall until an exit opens. (DFS + Floodfill)

        How to stall:
        1 - Keep using BFS to find a path to snakes tail starting from the end until algorithm returns true
        2 - Use that node as the destination for reverse-floodfill algorithm
            a) Create a grid of WxH with -1 everywhere
            b) set i = 0
            c) add the destination to the grid as i++
            d) get_neighbours to mark the neighbours with i++
            * How to get neighbours: make sure a neighbour is within the height and width, is not a tail or a head of snake and is -1
            e) mark the neighbours of neighbours with i++ (check that the neighbours of neighbours are -1, if not, don't mark them.)
            f) keep marking until all valid neighbours are marked.
        3- from the start (snake's head), get valid neighbours of start, compare neighbour's values, whichever one is bigger, that's your destination
        '''
