# -*- coding: utf-8 -*-
"""
Python implementation of PacMan game
project guide at http://www.openbookproject.net/pybiblio/gasp/course/6-chomp.html 

@author: Matt Beck
"""
import graphics as gx
import math as math
import time as time

#%% Global vars
# Set sizes in pixels
GRID_SIZE = 30
MARGIN    = GRID_SIZE
PAC_SIZE  = GRID_SIZE * 0.8
PAC_SPEED = 0.25 # grid points per tick

# Set colors
BACKGROUND_COLOR = 'black'
WALL_COLOR       = gx.color_rgb(0.6 * 255, 0.9 * 255, 0.9 * 255)
PAC_COLOR        = 'yellow'
# The shape of the maze.  Each character
# represents a different type of object
#   % - Wall
#   . - Food
#   o - Capsule
#   G - Ghost
#   P - PacMan
# Other characters are ignored
my_layout = [
  "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",     # There are 31 '%'s in this line
  "%.....%.................%.....%",
  "%o%%%.%.%%%.%%%%%%%.%%%.%.%%%o%",
  "%.%.....%......%......%.....%.%",
  "%...%%%.%.%%%%.%.%%%%.%.%%%...%",
  "%%%.%...%.%.........%.%...%.%%%",
  "%...%.%%%.%.%%% %%%.%.%%%.%...%",
  "%.%%%.......%GG GG%.......%%%.%",
  "%...%.%%%.%.%%%%%%%.%.%%%.%...%",
  "%%%.%...%.%.........%.%...%.%%%",
  "%...%%%.%.%%%%.%.%%%%.%.%%%...%",
  "%.%.....%......%......%.....%.%",
  "%o%%%.%.%%%.%%%%%%%.%%%.%.%%%o%",
  "%.....%........P........%.....%",
  "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"]


#%% Class Definitions
class Maze:
    def __init__(self):
        # do you have a window yet?
        self.have_window = False
        # did the player fail?
        self.game_over   = False
        # initialize all objects in the layout
        self.set_layout(my_layout)
        # set loop rate (Hz) MJB tbd
        # set_speed(20)

    def prompt_to_close(self):
        message = gx.Text(gx.Point(self.win.getWidth()/2, self.win.getHeight()/2),
                          'Click anywhere to quit.')
        message.setTextColor('white')
        message.draw(self.win)
        self.win.getMouse()
        self.win.close()
        
    def set_layout(self, layout):
        height = len(layout)
        width  = len(layout[0])
        self.win = self.make_window(width, height)
        self.make_map(width, height)
        self.movables = []
        
        # loop through layout and create objects
        for x in range(width):
            for y in range(height):
                char = layout[y][x] 
                #print('make '+char+' at '+str(x)+', '+str(y))                
                self.make_object((x, y), char)
        # loop through movables and move them
        for mover in self.movables:
            mover.draw_me()
        
        #self.prompt_to_close()

    def make_window(self, width, height):
        # makes and returns the main game window
        grid_width    = (width-1)  * GRID_SIZE
        grid_height   = (height-1) * GRID_SIZE
        screen_width  = 2*MARGIN + grid_width
        screen_height = 2*MARGIN + grid_height
        # start window
        win = gx.GraphWin(title = 'PacMan!', width = screen_width, height = screen_height)
        win.setBackground(BACKGROUND_COLOR)
        return win
    
    def to_screen(self, point):
        # convert from map coordinates to screen coordinates
        (x, y) = point
        x = x*GRID_SIZE + MARGIN
        y = y*GRID_SIZE + MARGIN
        return (x, y)

    def make_object(self, location, character):
        (x, y) = location
        if character == '%':
            # it's a wall
            self.map[y][x] = Wall(self, location)
        if character == 'P':
            # it's pacman
            mypac = Pacman(self, location)
            self.movables.append(mypac)
    
    def make_map(self, width, height):
        # map of objects in the grid (initialized to all Nothing objects)
        self.width  = width
        self.height = height
        self.map    = []
        for y in range(height):
            new_row = []
            for x in range(width):
                new_row.append(Nothing())
            self.map.append(new_row)
    
    def object_at(self, location):
        (x, y) = location
        # check for out of bounds locations and return Nothing object
        if y < 0 or y >= self.height:
            return Nothing()
        if x < 0 or x >= self.width:
            return Nothing()
        return self.map[y][x]
        
    
    def finished(self):
        return self.game_over
        
    def play(self):
        for mover in self.movables:
            mover.move()
        self.win.update()
        time.sleep(0.05);
    
    def done(self):
        self.map = []
        self.movables = []
        self.prompt_to_close()
        
class Immovable:
    pass

class Nothing(Immovable):
    def is_wall(self):
        return False

class Wall(Immovable):
    def __init__(self, maze, location):
        self.place        = location
        (x, y)            = self.place
        self.neighbors    = [(x+1, y),(x-1, y),(x, y+1),(x, y-1)]
        self.maze         = maze
        self.screen_point = self.maze.to_screen(location)
        self.draw_me(maze.win)
        
    def draw_me(self, win):
        (screen_x, screen_y) = self.screen_point
        for point in self.neighbors:
            self.check_neightbor(point)

    def is_wall(self):
        return True
        
    def check_neightbor(self, location):
        # check if neighbor object is a wall, if so draw line
        neighbor = self.maze.object_at(location)
        if neighbor.is_wall():
            a = self.screen_point
            b = neighbor.screen_point
            my_line = gx.Line(gx.Point(*a), gx.Point(*b))
            my_line.setWidth(2)
            my_line.setOutline(WALL_COLOR)
            my_line.draw(self.maze.win)
    
class Movable:
    def __init__(self, maze, location, speed):
        self.maze  = maze
        self.place = location
        self.speed = speed

class Pacman(Movable):
    def __init__(self, maze, location):
        Movable.__init__(self, maze, location, PAC_SPEED)
        self.direction = 0

    def draw_me(self):
        maze         = self.maze
        screen_point = maze.to_screen(self.place)
        angle        = (self.get_angle()+self.direction) * 3.14159 / 180
        #mouthpoints  = (self.direction + angle, self.direction + 360 - angle)
        mouthpoints = []
        mouthpoints.append((screen_point[0] + PAC_SIZE *math.cos(angle), screen_point[1] + PAC_SIZE *math.sin(angle)))
        mouthpoints.append((screen_point[0] + PAC_SIZE *math.cos(angle), screen_point[1] - PAC_SIZE *math.sin(angle)))
        self.body    = gx.Circle(gx.Point(*screen_point),PAC_SIZE)
        self.mouth   = gx.Polygon([gx.Point(*screen_point), gx.Point(*[math.ceil(x) for x in mouthpoints[0]]), gx.Point(*[math.ceil(x) for x in mouthpoints[1]])])
        self.body.setFill(PAC_COLOR)
        self.mouth.setFill(BACKGROUND_COLOR)
        self.body.draw(self.maze.win)
        self.mouth.draw(self.maze.win)
        
    def get_angle(self):
        (x, y) = self.place
        (near_x, near_y) = self.nearest_grid_point()
        distance = abs(x - near_x) + abs(y - near_y)
        return 1 + 90*distance
        
    def move(self):
        keys = self.maze.win.lastKey
        print('Pressed : '+keys)
        if   'Left'  in keys:
            self.move_left()
        elif 'Right' in keys:
            self.move_right()
        elif 'Up'    in keys:
            self.move_up()
        elif 'Down'  in keys:
            self.move_down()
        elif 'q'     in keys:
            self.maze.game_over = True
    
    def move_left (self):
        self.try_move((-1,  0))
 
    def move_right(self):
        self.try_move(( 1,  0))

    def move_up   (self):
        # directions reversed for graphics.py
        self.try_move(( 0, -1))

    def move_down (self):
        # directions reversed for graphics.py
        self.try_move(( 0,  1))

    def try_move(self, move):
        (move_x, move_y) = move
        (cur_x, cur_y)   = self.place
        (near_x, near_y) = self.nearest_grid_point()
        if self.furthest_move(move) == (0,0):
            # can't go that direction
            return
        if move_x != 0 and cur_y != near_y:
            # want horizontal, not at a grid point, get to nearest grid point
            move_x = 0
            move_y = near_y - cur_y
        elif move_y != 0 and cur_x != near_x:
            # want vertical, not at a grid point, get to nearest grid point
            move_x = near_x - cur_x
            move_y = 0
        # restrict movement to furthest available without hitting walls
        move = self.furthest_move((move_x, move_y))
        self.move_by(move)
    
    def furthest_move(self, move):
        (move_x, move_y) = move
        (cur_x, cur_y)   = self.place
        (near_x, near_y) = self.nearest_grid_point()
        maze             = self.maze

        # check for walls and truncate movement if heading for one        
        if move_x > 0:
            # moving right
            next_point = (near_x + 1, near_y)
            if maze.object_at(next_point).is_wall() and cur_x + move_x > near_x:
                # heading for a wall to the right
                move_x = near_x - cur_x
        elif move_x < 0:
            # moving left
            next_point = (near_x - 1, near_y)
            if maze.object_at(next_point).is_wall() and cur_x + move_x < near_x:
                # heading for a wall to the left
                move_x = near_x - cur_x
        if move_y > 0:
            # moving down (reversed direction for graphics.py)
            next_point = (near_x, near_y + 1)
            if maze.object_at(next_point).is_wall() and cur_y + move_y > near_y:
                # heading for a wall above
                move_y = near_y - cur_y
        elif move_y < 0:
            # moving up (reversed direction for graphics.py)
            next_point = (near_x, near_y - 1)
            if maze.object_at(next_point).is_wall() and cur_y + move_y < near_y:
                # heading for a wall below
                move_y = near_y - cur_y
        
        # truncate movement by speed (movement per tick) 
        if   move_x >  self.speed:
            move_x = self.speed
        elif move_x < -self.speed:
            move_x = -self.speed
        if   move_y >  self.speed:
            move_y = self.speed
        elif move_y < -self.speed:
            move_y = -self.speed
        
        return (move_x, move_y)
        
    def nearest_grid_point(self):
        (cur_x, cur_y) = self.place
        return (round(cur_x), round(cur_y))
    
    def move_by(self, move):
        self.update_position(move)
        old_body  = self.body
        old_mouth = self.mouth
        self.draw_me()
        old_body.undraw()
        old_mouth.undraw()
    
    def update_position(self, move):
        (old_x, old_y)   = self.place
        (move_x, move_y) = move
        (new_x, new_y)   = (old_x + move_x, old_y + move_y)
        self.place = (new_x, new_y)
        
        # set direction in degrees
        if   move_x > 0:
            self.direction = 0
        elif move_y > 0:
            self.direction = 90
        elif move_x < 0:
            self.direction = 180
        elif move_y < 0:
            self.direction = 270
    
    
        

#%% Instance variables



#%% main run procedure

my_maze = Maze()
while not my_maze.finished():
    my_maze.play()
my_maze.done()

#%% scratch pad
"""
# example window
win = gx.GraphWin()
win.setBackground(BACKGROUND_COLOR)
# example circle
pac = Circle(Point(100,100),50)
pac.setFill(WALL_COLOR)
pac.draw(win)
# close on click
message = gx.Text(Point(win.getWidth()/2, 20), 'Click to quit.')
message.draw(win)
win.getMouse()
win.close()
"""