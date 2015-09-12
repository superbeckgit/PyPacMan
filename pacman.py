# -*- coding: utf-8 -*-
"""
Python implementation of PacMan game
project guide at http://www.openbookproject.net/pybiblio/gasp/course/6-chomp.html

@author: Matt Beck
"""

# pylint: disable=C0326,

#%% Imports
from __future__ import print_function
from __future__ import division
import graphics as gx
import math
import time
import random


#%% Global vars
# Set sizes in pixels
GRID_SIZE   = 30
MARGIN      = GRID_SIZE
PAC_SIZE    = GRID_SIZE * 0.8
PAC_SPEED   = 0.25 # grid points per tick
GHOST_SPEED = 0.20
FOOD_SIZE   = GRID_SIZE * 0.15
DEG_TO_RAD  = math.pi / 180
CAP_SIZE    = GRID_SIZE * 0.3
SCARED_TIME = 100
WARN_TIME   = 50

# Set colors
BACKGROUND_COLOR = 'black'
WALL_COLOR       = gx.color_rgb(0.6 * 255, 0.9 * 255, 0.9 * 255)
PAC_COLOR        = 'yellow'
FOOD_COLOR       = 'red'
GHOST_COLORS     = ['red','green','blue','purple']
CAP_COLOR        = 'white'
SCARED_COLOR     = 'white'

# Ghost shape layout
GHOST_SHAPE = [
    ( 0.00,  0.50),
    ( 0.25,  0.75),
    ( 0.50,  0.50),
    ( 0.75,  0.75),
    ( 0.75, -0.50),
    ( 0.50, -0.75),
    (-0.50, -0.75),
    (-0.75, -0.50),
    (-0.75,  0.75),
    (-0.50,  0.50),
    (-0.25,  0.75)]

# The shape of the maze.  Each character
# represents a different type of object
#   % - Wall
#   . - Food
#   o - Capsule
#   G - Ghost
#   P - PacMan
# Other characters are ignored

# Create a layout, currently 31 x 15
raw_layout = r"""
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  %.....%.................%.....%
  %o%%%.%.%%%.%%%%%%%.%%%.%.%%%o%
  %.%.....%......%......%.....%.%
  %...%%%.%.%%%%.%.%%%%.%.%%%...%
  %%%.%...%.%.........%.%...%.%%%
  %...%.%%%.%.%%% %%%.%.%%%.%...%
  %.%%%.......%GG GG%.......%%%.%
  %...%.%%%.%.%%%%%%%.%.%%%.%...%
  %%%.%...%.%.........%.%...%.%%%
  %...%%%.%.%%%%.%.%%%%.%.%%%...%
  %.%.....%......%......%.....%.%
  %o%%%.%.%%%.%%%%%%%.%%%.%.%%%o%
  %.....%........P........%.....%
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
my_layout = [x.strip() for x in raw_layout.split('\n') if x.strip()]


#%% Class Definitions
class Maze:
    """ Maze class
        opens a graphic window
        initializes all objects in map layout
        updates location of all objects in map
        controls master game state (win/lose)

        Parameters:
            food_count : number of food objects in map
            game_over  : T/F to end gameplay
            height     : map height in objects
            map        : 2D array of objects
            movables   : list of movable objects
            width      : map width in objects
            win        : graphics window object

        Methods:
            __init__        : Initialize parameters and maze layout
            prompt_to_close : Put up player prompt for click to close
            set_layout      : initialize window object and objects in map
            make_window     : make and return main game window
            make_map        : initialize map of Nothing objects
            to_screen       : convert from map coords to screen coords
            make_object     : initialize objects in map
            object_at       : return object at specified map coords
            remove_food     : process food removal logic & win check
            remove_capsule  : process capsule removal and ghost fear
            pacman_loc      : update all movers with pacman location
            finished        : return game status, game_over(T) or not(F)?
            winner          : set game over flag to true
            loser           : send player message of loss, set game over flag to true
            play            : Move movers, update window graphic object, animation delay
            done            : Release map and movable objects, call for closure
    """

    def __init__(self):
        """ Initialize parameters and maze layout """
        # initialize maze parameters
        self.game_over   = False
        self.movables    = []
        self.food_count  = 0
        self.win         = None
        self.map         = []
        self.height      = None
        self.width       = None
        # Initialize all objects in the layout
        self.set_layout(my_layout)

    def prompt_to_close(self):
        """ Put up player prompt for click to close, close window """
        mes_loc = gx.Point(self.win.getWidth()/2, self.win.getHeight()/2)
        message = gx.Text(mes_loc, 'Click anywhere to quit.')
        message.setTextColor('white')
        message.draw(self.win)
        self.win.getMouse()
        self.win.close()

    def set_layout(self, layout):
        """ set height and wideth parameters
            initialize window graphics object
            calls for map to be drawn
            loop through objects in master layout and initialize them
        """
        self.height = len(layout)
        self.width  = len(layout[0])
        self.win    = self.make_window()
        self.make_map()
        # loop through layout and create objects
        for x in range(self.width):
            for y in range(self.height):
                char = layout[y][x]
                self.make_object((x, y), char)
        # loop through movables and draw them
        for mover in self.movables:
            mover.draw_me()

    def make_window(self):
        """ makes and returns main game window object """
        grid_width    = (self.width-1)  * GRID_SIZE
        grid_height   = (self.height-1) * GRID_SIZE
        screen_width  = 2*MARGIN + grid_width
        screen_height = 2*MARGIN + grid_height
        # start window
        win = gx.GraphWin(title = 'PacMan!',
                          width = screen_width,
                          height = screen_height)
        win.setBackground(BACKGROUND_COLOR)
        return win

    def make_map(self):
        """ Initialize map of Nothing objects """
        for y in range(self.height):
            new_row = []
            # fill row list with nothing objects
            for x in range(self.width):
                new_row.append(Nothing())
            # append row list to map
            self.map.append(new_row)

    def to_screen(self, point):
        """ convert from map coordinates to screen coordinates """
        (x, y) = point
        x = x*GRID_SIZE + MARGIN
        y = y*GRID_SIZE + MARGIN
        return (x, y)

    def make_object(self, location, character):
        """ initialize all objects on map """
        (x, y) = location
        if character == '%':
            # it's a wall
            self.map[y][x] = Wall(self, location)
        if character == 'P':
            # it's pacman
            mypac = Pacman(self, location)
            self.movables.append(mypac)
        if character == '.':
            # it's food
            self.food_count += 1
            self.map[y][x]   = Food(self, location)
        if character == 'G':
            # it's a ghost
            ghost = Ghost(self, location)
            self.movables.append(ghost)
        if character == 'o':
            # it's a power capsule
            self.map[y][x] = Capsule(self, location)

    def object_at(self, location):
        """ return the object in the map at desired location """
        (x, y) = location
        # check for out of bounds locations and return Nothing object
        if y < 0 or y >= self.height:
            return Nothing()
        if x < 0 or x >= self.width:
            return Nothing()
        # return object at location for valid locations
        return self.map[y][x]

    def remove_food(self, place):
        """ replace food object with nothing object,
            decrease food count
            check for win condition (ate all food)
        """
        (x, y) = place
        self.map[y][x]   = Nothing()
        self.food_count -= 1
        if self.food_count == 0:
            self.winner()

    def remove_capsule(self, place):
        """ replace power capsule with nothing object
            trigger ghost fear
        """
        (x, y) = place
        self.map[y][x] = Nothing()
        # tricgger ghost fear for all ghosts
        for mover in self.movables:
            mover.capsule_eaten()

    def pacman_loc(self, mypac, location):
        """ update all movers with pacman location """
        for mover in self.movables:
            mover.pacman_loc(mypac, location)

    def finished(self):
        """ return game status, game_over(T) or not(F)? """
        return self.game_over

    def winner(self):
        """ set game over flag to true """
        self.game_over = True

    def loser(self):
        """ send player message of loss and set game over flag to true """
        mes_loc = gx.Point(self.win.getWidth()/2, self.win.getHeight()/4)
        message = gx.Text(mes_loc, 'You Lose!')
        message.setTextColor('white')
        message.draw(self.win)
        self.game_over = True

    def play(self):
        """ Move all movables
            Update window graphic object
            Insert game delay
        """
        for mover in self.movables:
            mover.move()
        self.win.update()
        time.sleep(0.05)

    def done(self):
        """ Release map and movable objects, call for closure """
        self.map = []
        self.movables = []
        self.prompt_to_close()


class Immovable:
    """ Immovable Class
            Basic non-mobile objects in the map, includes walls and food items

        Parameters:
            NONE

        Methods:
            eat_me  : empty method, used by child classes
            is_wall : return T/F if object is wall, set by child classes
    """

    def eat_me(self, pacman):
        """ empty method, used by child classes """
        pass

    def is_wall(self):
        """ return T/F if object is wall, set by child classes """
        return False

class Nothing(Immovable):
    """ Nothing Class [inherits from Immovable]
            Non-mobile objects in the map, used to fill empty locations

        Parameters:
            NONE

        Methods:
            NONE
    """
    pass

class Capsule(Immovable):
    """ Capsule Class [inherits from Immovable]
            Non-mobile capsule objects in the map, causes ghost fear when eaten

        Parameters:
            dot          : graphics object
            maze         : handle for maze object
            place        : location in map
            screen_point : location on screen

        Methods:
            __init__ : Initialize all capsule parameters
            draw_me  : Initialize graphics object and draw on window
            eat_me   : Triggers capsule removal logic
    """

    def __init__(self, maze, point):
        """ Initialize all capsule parameters """
        self.place        = point
        self.screen_point = maze.to_screen(point)
        self.maze         = maze
        self.draw_me()

    def draw_me(self):
        """ Initialize graphics object and draw on window """
        self.dot = gx.Circle(gx.Point(*self.screen_point), CAP_SIZE)
        self.dot.setFill(CAP_COLOR)
        self.dot.setOutline(CAP_COLOR)
        self.dot.draw(self.maze.win)

    def eat_me(self, mypac):
        """ Triggers capsule removal logic """
        self.dot.undraw()
        self.maze.remove_capsule(self.place)


class Food(Immovable):
    """ Food Class [inherits from Immovable]
            Non-mobile food objects in the map, player wins if all are eaten

        Parameters:
            dot          : graphics object
            maze         : handle for maze object
            place        : location in map
            screen_point : location on screen

        Methods:
            __init__ : Initialize all food parameters
            draw_me  : Initialize graphics object and draw on window
            eat_me   : Triggers food removal logic
    """

    def __init__(self, maze, point):
        """ Initialize all food parameters """
        self.place        = point
        self.screen_point = maze.to_screen(point)
        self.maze         = maze
        self.draw_me()

    def draw_me(self):
        """ Initialize graphics object and draw on window """
        self.dot = gx.Circle(gx.Point(*self.screen_point),FOOD_SIZE)
        self.dot.setFill(FOOD_COLOR)
        self.dot.setOutline(FOOD_COLOR)
        self.dot.draw(self.maze.win)

    def eat_me(self, pacman):
        """ Triggers capsule removal logic """
        self.dot.undraw()
        self.maze.remove_food(self.place)


class Wall(Immovable):
    """ Wall Class [inherits from Immovable]
            Non-mobile wall objects in the map

        Parameters
        ----------
            maze         : handle for maze object
            neighbors    : list of coords surrounding wall coords
            place        : location in map
            screen_point : location on screen

        Methods:
            __init__       : Initialize all wall parameters
            check_neighbor : Check if neighbor object is a wall, if so draw line
            draw_me        : Initialize graphics object and draw on window
            is_wall        : Inherited/Overloaded, returns True
    """
    def __init__(self, maze, location):
        """ Initialize all wall parameters """
        self.place        = location
        (x, y)            = self.place
        self.neighbors    = [(x+1, y),(x-1, y),(x, y+1),(x, y-1)]
        self.maze         = maze
        self.screen_point = self.maze.to_screen(location)
        self.draw_me(maze.win)

    def draw_me(self, win):
        """ Initialize graphics object and draw on window """
        (screen_x, screen_y) = self.screen_point
        for point in self.neighbors:
            self.check_neighbor(point)

    def is_wall(self):
        """ Inherited/Overloaded, returns True """
        return True

    def check_neighbor(self, location):
        """ Check if neighbor object is a wall, if so draw line """
        neighbor = self.maze.object_at(location)
        if neighbor.is_wall():
            a = self.screen_point
            b = neighbor.screen_point
            # line object is drawn once, never needed again
            # No need to make a parameter like food/capsule dot objects
            my_line = gx.Line(gx.Point(*a), gx.Point(*b))
            my_line.setWidth(2)
            my_line.setOutline(WALL_COLOR)
            my_line.draw(self.maze.win)

class Movable:
    def __init__(self, maze, location, speed):
        self.maze  = maze
        self.place = location
        self.speed = speed

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
        return (int(round(cur_x)), int(round(cur_y)))

    def update_position(self, move):
        (old_x, old_y)   = self.place
        (move_x, move_y) = move
        (new_x, new_y)   = (old_x + move_x, old_y + move_y)
        self.place = (new_x, new_y)

    def capsule_eaten(self):
        pass

class Pacman(Movable):
    def __init__(self, maze, location):
        Movable.__init__(self, maze, location, PAC_SPEED)
        self.direction = 0

    def draw_me(self):
        maze         = self.maze
        screen_point = maze.to_screen(self.place)
        angle        = (self.get_angle()+self.direction) * DEG_TO_RAD
        mouthpoints = []
        # set mouth verticies based on direction
        if self.direction in [0, 180]:
            # +/- sin for left and right
            mouthpoints.append((screen_point[0] + PAC_SIZE *math.cos(angle), screen_point[1] + PAC_SIZE *math.sin(angle)))
            mouthpoints.append((screen_point[0] + PAC_SIZE *math.cos(angle), screen_point[1] - PAC_SIZE *math.sin(angle)))
        else:
            # +/- cos for up and down
            mouthpoints.append((screen_point[0] + PAC_SIZE *math.cos(angle), screen_point[1] + PAC_SIZE *math.sin(angle)))
            mouthpoints.append((screen_point[0] - PAC_SIZE *math.cos(angle), screen_point[1] + PAC_SIZE *math.sin(angle)))
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
        if   'Left'  in keys:
            self.try_move((-1,  0))
        elif 'Right' in keys:
            self.try_move(( 1,  0))
        elif 'Up'    in keys:
            # directions reversed for graphics.py
            self.try_move(( 0, -1))
        elif 'Down'  in keys:
            # directions reversed for graphics.py
            self.try_move(( 0,  1))
        elif 'q'     in keys:
            self.maze.game_over = True
        self.maze.pacman_loc(self, self.place)

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

    def move_by(self, move):
        self.update_position(move)
        old_body  = self.body
        old_mouth = self.mouth
        self.draw_me()
        old_body.undraw()
        old_mouth.undraw()
        (cur_x, cur_y)   = self.place
        (near_x, near_y) = self.nearest_grid_point()
        distance = (abs(cur_x - near_x) + abs(cur_y-near_y))
        if distance < self.speed * 3/4:
            item = self.maze.object_at((near_x, near_y))
            item.eat_me(self)

        # set direction in degrees
        (move_x, move_y) = move
        if   move_x > 0:
            self.direction = 0
        elif move_y > 0:
            self.direction = 90
        elif move_x < 0:
            self.direction = 180
        elif move_y < 0:
            self.direction = 270

    def pacman_loc(self, mypac, location):
        pass

class Ghost(Movable):
    num = 0

    def __init__(self, maze, start):
        Ghost.num       += 1
        self.place      = start
        self.next_point = start
        self.movement   = (0, 0)
        self.color      = GHOST_COLORS[Ghost.num % 4]
        self.orig_color = self.color
        self.time_left  = 0
        self.start      = start
        Movable.__init__(self, maze, start, GHOST_SPEED)

    def draw_me(self):
        maze = self.maze
        (screen_x, screen_y) = maze.to_screen(self.place)
        body_points = []
        for (x,y) in GHOST_SHAPE:
            body_points.append((x*GRID_SIZE + screen_x, y*GRID_SIZE + screen_y))
        vertices = [gx.Point(x,y) for (x,y) in body_points]
        self.body = gx.Polygon(*vertices)
        self.body.setFill(self.color)
        self.body.setOutline(self.color)
        self.body.draw(maze.win)

    def capsule_eaten(self):
        self.change_color(SCARED_COLOR)
        self.time_left = SCARED_TIME

    def change_color(self, new_color):
        self.color = new_color
        self.body.setFill(new_color)

    def move(self):
        (cur_x, cur_y)   = self.place
        (next_x, next_y) = self.next_point
        move = (next_x - cur_x, next_y - cur_y)
        move = self.furthest_move(move)
        if move == (0,0):
            move = self.choose_move()
        self.move_by(move)
        if self.time_left > 0:
            self.update_scared()

    def update_scared(self):
        self.time_left = self.time_left - 1
        time_left      = self.time_left
        if time_left < WARN_TIME:
            if time_left % 2 == 0:
                color = self.orig_color
            else:
                color = SCARED_COLOR
            self.change_color(color)

    def choose_move(self):
        (move_x, move_y) = self.movement
        (near_x, near_y) = self.nearest_grid_point()
        possible_moves = []

        if move_x >= 0 and self.can_move_by(( 1,  0)):
            possible_moves.append(( 1,  0))
        if move_x <= 0 and self.can_move_by((-1,  0)):
            possible_moves.append((-1,  0))
        if move_y >= 0 and self.can_move_by(( 0,  1)):
            possible_moves.append(( 0,  1))
        if move_y <= 0 and self.can_move_by(( 0, -1)):
            possible_moves.append(( 0, -1))

        if len(possible_moves) != 0:
            choice = random.randint(0, len(possible_moves)-1)
            move   = possible_moves[choice]
            (move_x, move_y) = move
        else:
            move_x = -move_x
            move_y = -move_y
            move   = (move_x, move_y)

        (cur_x, cur_y)  = self.place
        self.next_point = (cur_x + move_x, cur_y + move_y)

        self.movement = move
        return self.furthest_move(move)

    def can_move_by(self, move):
        move = self.furthest_move(move)
        return move != (0,0)

    def move_by(self, move):
        self.update_position(move)
        old_body  = self.body
        self.draw_me()
        old_body.undraw()

    def pacman_loc(self, mypac, location):
        (my_x, my_y)     = self.place
        (pac_x, pac_y)   = location
        (delt_x, delt_y) = (my_x - pac_x, my_y - pac_y)
        dis_sq           = delt_x*delt_x + delt_y*delt_y
        limit            = 1.6*1.6
        if dis_sq < limit:
            self.bump_into(mypac)

    def bump_into(self, mypac):
        if self.time_left != 0:
            self.captured(mypac)
        else:
            self.maze.loser()

    def captured(self, mypac):
        self.place = self.start
        self.color = self.orig_color
        self.time_left = 0
        self.body.undraw()
        self.draw_me()

#%% Instance variables


#%% main run procedure
if __name__ == '__main__':
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
""" with numpydoc standards, run examples with
    >>>import doctest
    >>>doctest.testmod(verbose=False)
    in __name__ == __main__ block
"""