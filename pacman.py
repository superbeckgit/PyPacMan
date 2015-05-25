# -*- coding: utf-8 -*-
"""
Python implementation of PacMan game
project guide at http://www.openbookproject.net/pybiblio/gasp/course/6-chomp.html 

@author: Matt Beck
"""
import graphics as gx

#%% Global vars
# Set sizes in pixels
GRID_SIZE = 30
MARGIN    = GRID_SIZE

# Set colors
BACKGROUND_COLOR = 'black'
WALL_COLOR       = gx.color_rgb(0.6 * 255, 0.9 * 255, 0.9 * 255)

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
        message = gx.Text(gx.Point(self.win.getWidth()/2, 20), 'Click to quit.')
        message.setTextColor('gray')
        message.draw(self.win)
        self.win.getMouse()
        self.win.close()
        
    def set_layout(self, layout):
        height = len(layout)
        width  = len(layout[0])
        self.win = self.make_window(width, height)
        self.make_map(width, height)
        
        # loop through layout and create objects
        for x in range(width):
            for y in range(height):
                char = layout[y][x] 
                print('make '+char+' at '+str(x)+', '+str(y))                
                self.make_object((x, y), char)
                
        self.prompt_to_close()

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
        update_when('next_tick')
    
    def done(self):
        self.prompt_to_close(self.win)
        
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
        dot_size = GRID_SIZE * 0.2
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
    pass



#%% Instance variables



#%% main run procedure

my_maze = Maze()
#while not my_maze.finished():
#    my_maze.play()
#my_maze.done()

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