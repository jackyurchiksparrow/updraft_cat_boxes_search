import numpy as np
from numpy import random

class Room:
    # constructor that holds value for territory_size (matrix dimension), boxes count (boxes to randomize)
    def __init__(self, territory_size, boxes_count):
        self.N = territory_size # dimensions for the initial matrix
        self.territory = np.zeros((territory_size, territory_size))# filling the initial matrix with zeroes
        self.BOX = boxes_count# quantity of boxes to randomize
        # in case it made duplicate points we ensure there are exactly boxes_count points
        while len(np.where(self.territory==1)[0]) < boxes_count:
            # randomized boxes are shown as "ones"
            self.territory[random.randint(0, territory_size)][random.randint(0, territory_size)] = 1
            
    N = 0  # matrix size
    BOX = 0 # initial box count
    territory = [] # initial matrix

class Cat:
    # constructor that recieves a set Room object
    def __init__(self, terr: Room):
        self.cat_pos_i = random.randint(0, terr.N) # initial x position of cat to start from
        self.cat_pos_j = random.randint(0, terr.N) # initial y position of cat to start from
        self.map_visited = np.full_like(terr.territory, 0) # an N-sized matrix to track the progress
        self.boxes_left_count = terr.BOX # quantity of boxes to randomize
        self.max_dist_to_move = 2*self.VIS+1 # maximum cells for the cat to look at once (in a straight line)

    cat_pos_i = 0 # current cat position (x)
    cat_pos_j = 0 # current cat position (y)

    VIS = 3 # cat vision ability (in cells, around)

    map_visited = [] # cat's map (where it has already been)

    boxes_to_pick = [] # current boxes to pick in a queue
    boxes_left_count = 0 # quantity of boxes yet to be found

    prev_directions = [] # previous directions the cat had followed

    max_dist_to_move = 0 # maximum cells for the cat to look at once (in a straight line)

    # territory - the initial matrix; room
    # returns [submatrix VISxVIS, respective borders to get that submatrix from the room matrix]
    # memorizes location around the cat
    def look_around(self, territory: np.ndarray):
        pos_left_i = self.cat_pos_i-self.VIS 
        pos_left_j = self.cat_pos_j-self.VIS

        if pos_left_i < 0:
            pos_left_i = 0
        if pos_left_j < 0:
            pos_left_j = 0

        pos_right_i = self.cat_pos_i+self.VIS+1
        pos_right_j = self.cat_pos_j+self.VIS+1

        if pos_right_i > territory.shape[0]:
            pos_right_i = territory.shape[0]
        if pos_right_j > territory.shape[1]:
            pos_right_j = territory.shape[1]

        self.map_visited[pos_left_i:pos_right_i, pos_left_j:pos_right_j] = 1
        return [territory[pos_left_i:pos_right_i, pos_left_j:pos_right_j], 
                [(pos_left_i,pos_right_i), (pos_left_j, pos_right_j)]]
    
    # terr_size - the initial matrix size
    # decides the direction to move further
    def get_direction(self, terr_size: int):
        if len(self.prev_directions) == 0:
            # "DOWN" given we have space
            if (self.cat_pos_i+self.VIS) < terr_size-1:
                self.prev_directions.append("DOWN")
            else:
                # if there's no space, move "RIGHT"
                self.prev_directions.append("RIGHT")
        elif self.prev_directions[-1] == "UP" or self.prev_directions[-1] == "DOWN":
            # "RIGHT" given we have space
            if (self.cat_pos_j + self.VIS) < terr_size-1:
                self.prev_directions.append("RIGHT")
            else:
                # if there's no space, return to the start
                self.prev_directions = ["RETURN"]
        # previous element was "RIGHT" and there is no space to move right anymore
        elif (self.prev_directions[-1] == "RIGHT") and ((self.cat_pos_j + self.VIS) >= terr_size-1):
            if len(self.prev_directions)==1:
                # "DOWN" given we have space
                if (self.cat_pos_i+self.VIS) < terr_size-1:
                    self.prev_directions.append("DOWN")
                else:
                    # if there's no space, return to the start
                    self.prev_directions.append("RETURN")
            else:
                if self.prev_directions[-2] == "DOWN":
                    # "UP" and return to the start
                    self.prev_directions.append(("UP", "RETURN"))
                else:
                    # "DOWN" and return to the start
                    self.prev_directions.append(("DOWN", "RETURN"))
        else:
            if len(self.prev_directions)==1:
                # "UP" given it's a second direction
                self.prev_directions.append("UP")
            elif self.prev_directions[-2] == "DOWN":
                # "UP" given the direction before previous was "DOWN"
                self.prev_directions.append("UP")
            else:
                # "DOWN" otherwise
                self.prev_directions.append("DOWN")

    # territory - the initial matrix; room
    # finds boxes in location using look_around()
    def search_for_boxes(self, territory: np.ndarray):
        if self.boxes_left_count > 0:
            print("Searching for boxes...")
            look = self.look_around(territory)

            # look for boxes (ones) in the submatrix
            for x in np.argwhere(look[0] == 1).tolist():
                x[0] += look[1][0][0]
                x[1] += look[1][1][0]

                # if we haven't added them earlier
                if x not in self.boxes_to_pick:
                    self.boxes_to_pick.append(x)
            if len(self.boxes_to_pick) > 0:
                print("Found:", self.boxes_to_pick)
        else:
            return   
        
    # returns cat's (x,y) position
    def get_cat_pos(self):
        return (self.cat_pos_i, self.cat_pos_j)
    
    # moves the cat to the specific coordinates
    def move_to(self, coords: tuple):
        self.cat_pos_i = coords[0]
        self.cat_pos_j = coords[1]

    # takes the boxes found by search_for_boxes(), meanwhile searching for new boxes
    def take_the_boxes(self, territory: np.ndarray):
        if len(self.boxes_to_pick) == 0:
            print("No boxes around...")
            return
        
        for box in list(self.boxes_to_pick):
            # steps to make for i and j
            steps_i = box[0]-self.cat_pos_i
            steps_j = box[1]-self.cat_pos_j
            
            print("Taking ", box, "...")

            self.move_to((self.cat_pos_i+steps_i, self.cat_pos_j+steps_j)) # move to the box
            self.boxes_to_pick.remove(box) # mark the box as picked
            self.boxes_left_count -= 1 # decrease left boxes count
            territory[self.cat_pos_i][self.cat_pos_j] = 0 # mark the box as found

            print(box, "is taken, current map (1 for checked cells):")
            print(self.map_visited)

            if self.boxes_left_count > 0:
                self.search_for_boxes(territory)
            else:
                print("Finished")
                return
                
        self.take_the_boxes(territory) # we need it if we find other boxes while taking these

    # terr - Room object
    # moves down exactly max_dist_to_move or less, if necessary
    def move_down(self, terr: Room):
        if self.boxes_left_count == 0:
            return
        
        print("Going down..")

        boxes_left = self.boxes_left_count
        undiscovered_cells_down = terr.N - (self.cat_pos_i + self.VIS) - 1 # cells that are still zeros (down)
 
        if undiscovered_cells_down > 0:
            for i in range(0, undiscovered_cells_down // self.max_dist_to_move): # how many time we can move max distance down
                print("To", self.cat_pos_i + self.max_dist_to_move, self.cat_pos_j + 0)

                self.move_to((self.cat_pos_i + self.max_dist_to_move, self.cat_pos_j + 0)) # move there
                self.search_for_boxes(terr.territory) # search for boxes
                self.take_the_boxes(terr.territory) # and take them

                if self.boxes_left_count == 0:
                    return
            
            if self.boxes_left_count == boxes_left: # no boxes were found in the loop
                if undiscovered_cells_down % self.max_dist_to_move > 0: # we can't go with max distance, so we'll use exactly the remainder
                    print("Going down..")
                    print("To", self.cat_pos_i + (undiscovered_cells_down % self.max_dist_to_move), self.cat_pos_j + 0)

                    self.move_to((self.cat_pos_i + (undiscovered_cells_down % self.max_dist_to_move), self.cat_pos_j + 0)) # move there
                    self.search_for_boxes(terr.territory) # search for boxes
                    self.take_the_boxes(terr.territory) # and take them
            else:
                self.move_down(terr) # if we found new boxes on the way

    # territory - the initial matrix; room
    # moves up exactly max_dist_to_move or less, if necessary
    def move_up(self, territory: np.ndarray):
        if self.boxes_left_count == 0:
            return
        
        print("Going up...")

        boxes_left = self.boxes_left_count
        undiscovered_cells_up = self.cat_pos_i - self.VIS # cells that are still zeros (up)

        if undiscovered_cells_up > 0:
            for i in range(0, undiscovered_cells_up // self.max_dist_to_move): # how many time we can move max distance up
                print("To", self.cat_pos_i - self.max_dist_to_move, self.cat_pos_j + 0)

                self.move_to((self.cat_pos_i - self.max_dist_to_move, self.cat_pos_j + 0)) # move there
                self.search_for_boxes(territory) # search for boxes
                self.take_the_boxes(territory) # and take them

                if self.boxes_left_count == 0:
                    return
            
            if self.boxes_left_count == boxes_left: # no boxes were found in the loop
                if undiscovered_cells_up % self.max_dist_to_move > 0: # we can't go with max distance, so we'll use exactly the remainder
                    print("Going up...")
                    print("To", self.cat_pos_i - (undiscovered_cells_up % self.max_dist_to_move), self.cat_pos_j + 0)

                    self.move_to((self.cat_pos_i - (undiscovered_cells_up % self.max_dist_to_move), self.cat_pos_j + 0)) # move there
                    self.search_for_boxes(territory) # search for boxes
                    self.take_the_boxes(territory) # and take them
            else:
                self.move_up(territory) # if we found new boxes on the way

    # terr - Room object
    # moves up exactly max_dist_to_move or less, if necessary; can't call itself
    def move_right(self, terr: Room):
        if self.boxes_left_count == 0:
            return
        
        print("Going right...")

        undiscovered_cells_right = terr.N - (self.cat_pos_j + self.VIS)-1 # cells that are still zeros (right)

        if undiscovered_cells_right > 0:
            if (undiscovered_cells_right // self.max_dist_to_move) > 0: # if we can take max distance step once
                print("To", self.cat_pos_i + 0, self.cat_pos_j + self.max_dist_to_move)

                self.move_to((self.cat_pos_i + 0, self.cat_pos_j + self.max_dist_to_move)) # take it
                self.search_for_boxes(terr.territory) # search for boxes
                self.take_the_boxes(terr.territory) # and take them
            
            else: # then move less amount of steps
                print("Going right...")
                print("To", self.cat_pos_i + 0, self.cat_pos_j + (undiscovered_cells_right % self.max_dist_to_move))

                self.move_to((self.cat_pos_i + 0, self.cat_pos_j + (undiscovered_cells_right % self.max_dist_to_move))) # move
                self.search_for_boxes(terr.territory) # search for boxes
                self.take_the_boxes(terr.territory) # and take them

    # territory - the initial matrix; room
    # return to the upper-left corner of the room
    def return_to_start(self, territory: np.ndarray):
        if self.boxes_left_count == 0:
            return
        
        print("Returning to start...")
        boxes_left = self.boxes_left_count

        N = territory.shape # matrix size
        self.move_to((N[0]//2, N[1]//2)) # go to the matrix center
        self.search_for_boxes(territory) # search for boxes there
        self.take_the_boxes(territory) # take them

        # move one cell at a time, checking for boxes, until we reach (0, 0) or find all boxes
        while self.cat_pos_i > 0 and self.boxes_left_count > 0:
            print("On the way to the start ( to", self.cat_pos_i-1, self.cat_pos_j-1, ")")

            self.move_to((self.cat_pos_i-1, self.cat_pos_j-1))
            self.search_for_boxes(territory)
            self.take_the_boxes(territory)

            if boxes_left != self.boxes_left_count: # if another box was found on the way to (0, 0)
                self.return_to_start(territory)
                return
        print(self.map_visited)

    # terr - Room object
    # look for remaining boxes
    def location_search(self, terr: Room):
        while(self.boxes_left_count > 0): # while we still have something to look for
            # get the right direction
            self.get_direction(terr.N) 
            curr_direction = self.prev_directions[-1]

            if type(curr_direction) == tuple: # if we recieved two instructions (one includes "RETURN")
                if curr_direction[0] == "UP":
                    self.move_up(terr.territory)
                else:
                    self.move_down(terr)
                self.return_to_start(terr.territory)
            elif curr_direction == "UP":
                self.move_up(terr.territory)
            elif curr_direction == "DOWN":
                self.move_down(terr)
            elif curr_direction == "RIGHT":
                self.move_right(terr)
            else:
                self.return_to_start(terr.territory)

        print("All boxes were found. End")
        return
        

if __name__ == "__main__":
    cats_playground = Room(13, 6) # generating Room object with Room size 13 and 6 boxes
    cat = Cat(cats_playground) # creating a cat inside the room

    print("Generated boxes:", list(zip(*np.where(cats_playground.territory==1))))
    print("We have the territory with size", cats_playground.N, "and", cats_playground.BOX, "boxes (marked as 1):")
    print(cats_playground.territory)
    print("Cat is starting from", cat.get_cat_pos())
    
    # Initial boxes search
    cat.search_for_boxes(cats_playground.territory)
    cat.take_the_boxes(cats_playground.territory)

    # Start to look for others (if necessary)
    cat.location_search(cats_playground)

    print("The final map:")
    print(cat.map_visited)
    print("The cat has finished at", cat.get_cat_pos())