###############################################################
# The world for the game
# and its entities...

###############################################################
# MODULES

import numpy as np
import textcolors as colors
import os

###############################################################
# DEFINITIONS

# World definition:
#
World_def = {
    "name":         "Lil' ASCII Lab",
    "width":        15,         # x from 0 to WIDTH -1
    "height":       10,         # y from 0 to HEIGHT -1
    "bg_color":     'reset',    # background color ('reset' for transparent)
    "bg_intensity": 'normal',   # background intensity ('normal' for transparent)
    "n_blocks_rnd": 0.4,        # % of +/- randomness in number of blocks.
    "max_ticks":    100,         # How long to run the world ('None' for infinite loop).
    "chk_ticks":    None           # How often to ask user for quit/go-on ('None' = never ask).
}

# Tiles definition:
# type of tile, aspect, color, intensity, position (not specified here)
Tile_def = (
    ("tile", ".", "black", "bright", [None, None])
)

# Block definition: 
# number of instances (or RND), block type, aspect, color, intensity, position (not specified here).
Block_def = (
    (4, "plant", "*", "yellow", "normal", [None, None]),
    (None, "block2", "█", "black", "bright", [None, None]),
)


# Agent definition:
# number of instances, agent type, aspect, color, intensity, initial position (or RND), ai.
Agents_def = (
    (1, "Omi", "𝝮", "green", "normal", [None, None], None),
    (3, "apple", "", "red", "bright", [None, None], None),
)

# Interesting characters:  ~ … . · ˙ • ° † ∞  ◊ ∆ ¯-_ |-/\  <v^> ∏ 
# Extended ASCII: 176░ 177▒ 178▓ 219█ 254■
# https://theasciicode.com.ar/extended-ascii-code/graphic-character-medium-density-dotted-ascii-code-177.html

# Output settings:
# Define how I/O will happen.
IO_def = {
    "color":        True,   # True for colors, False for B&G.
    "spacing":      1,      # Number of 'spc' chars to concatenate at the right of every tile.
    "extend_block": False,   # Whether blocks must be replicated to cover full tile.
}

###############################################################
# CLASSES

class Thing:
    # Root class containing the common attributes for all classes.
    def __init__(self, name, aspect, color, intensity, position):
        self.name = name                # Name of the thing
        self.aspect = aspect            # Text character to be printed like
        self.color = color              # Color for the character
        self.intensity = intensity    # intensity to apply
        self.position = position        # Its position in the world

class Tile(Thing):
    pass

class Block(Thing):
    num_blocks = 0
    # It passively occupies one tile, never moving.
    def __init__(self, name, aspect, color, intensity, position):
        # Initialize inherited attributes
        super().__init__(name, aspect, color, intensity, position)
        # Update class variable
        Block.num_blocks += 1

class Agent(Thing):
    num_agents = 0
    def __init__(self, name, aspect, color, intensity, position, ai = None):
        # Initialize inherited and specific attributes
        super().__init__(name, aspect, color, intensity, position)
        self.ai = ai
        self.ticks = 0
        # Update class variable
        Agent.num_agents += 1

    def tick(self):
        # TBA: execute agent's AI and return chosen action(s).
        self.ticks +=1

class World:
    # A tiled, rectangular setting on which a little universe takes life.
    def __init__(self, w_def, t_def, b_def, a_def):
        # Create a world from a World_def and an Agents_def
        # Assign values from w_def
        self.name = w_def["name"]
        self.width = w_def["width"]
        self.height = w_def["height"]
        self.bg_color = w_def["bg_color"]
        self.bg_intensity = w_def["bg_intensity"]
        self.n_blocks_rnd = w_def["n_blocks_rnd"]
        self.max_ticks = w_def["max_ticks"]
        self.chk_ticks = w_def["chk_ticks"]

        # Initialize world: ticks and list of things on it.
        self.ticks = 0
        self.things = np.full((self.width, self.height), None) # create grid for agents and blocks

        # put tiles on the ground
        self.ground = np.full((self.width, self.height), None) # fill in the basis of the world.
        for x in range(self.width):
            for y in range(self.height):
                # Create tile (position set in t_def[4] is ignored).
                tile = Tile(t_def[0], t_def[1], t_def[2], t_def[3], [x, y])
                self.ground[x, y] = tile           

        # put agents in the world
        self.agents = []                # list of all types of agent in the world
        for a in a_def:                 # loop over the types of agent defined
            for i in range(a[0]):       # create the # of instances specified
                # Create agent
                agent = Agent(a[1], a[2], a[3], a[4], a[5], a[6])    # definition of the agent
                # Put agent in the world on requested position, relocating on colisions.
                res = self.move(agent, agent.position[0], agent.position[1], relocate=True)
                self.agents.append(agent)

        # put some blocks in, # based on width
        self.blocks = []
        for b in b_def:                 # list of all types of block in the world.
            if(b[0] == None):           # Unspecified # of blocks.
                n_random_blocks = (self.width * self.n_blocks_rnd) // 1 # abs. max variation
                n_random_blocks = self.width + np.random.randint(-n_random_blocks, n_random_blocks+1)
            else:                       # Specified # of blocks.
                n_random_blocks = b[0]

            n = 0
            while n < n_random_blocks:
                block = Block(b[1], b[2], b[3], b[4], b[5])
                res = self.move(block)      # Put in random position
                self.blocks.append(block)
                n += 1

    def move(self, thing, x = None, y = None, relocate = False):
        # If x, y not defined, find a random free place and move the Thing there.
        # If x, y are defined,
        #       if not occupied, move a Thing to x, y;
        #       if occupied, relocate randomly if specified, or fail otherwise.
        if x == None or y == None:
            # x, y not defined; try to  find some random position.
            position, res = self.find_free_tile()
        else:
            # x, y are defined; check if position is empty.
            if self.is_empty(x, y):
                # position is empty
                position, res = [x, y], 0
            elif relocate:
                # position is occupied, try to relocate as requested
                position, res = self.find_free_tile()
            else:
                # position is occupied and no relocation requested; FAIL.
                res = 1
        
        if (res == 0):
            # The move is possible, proceed now.
            if (thing.position[0] != None and thing.position[1] != None):
                # The Thing was already in the world; clear out old place.
                self.things[thing.position[0], thing.position[1]] = None
            self.things[position[0], position[1]] = thing
            thing.position = position

        return (res)

    def is_empty(self, x, y):
        # Check if a given position is free
        return (self.things[x, y] == None)

    def find_free_tile(self):
        # Try a random tile
        x = np.random.randint(0, self.width)
        y = np.random.randint(0, self.height)
        found = self.is_empty(x, y)

        x0, y0 = x, y                   # Starting position to search from
        res = 0                         # Fail condition (0: success; 1: board is full)

        while not found and not (res == 1):
            x = (x+1)%self.width        # Increment x not exceeding width
            if x == 0 :                 # When x is back to 0, increment y not exceeding height
                y = (y+1)%self.height
            if self.is_empty(x, y):     # Check "success" condition
                found = True
            elif (x, y) == (x0, y0):    # Check "fail" condition
                res = 1

        return (x, y), res

    def tick(self):
        self.ticks +=1
        # Tick all agents
        map(Agent.tick, self.agents)

    def is_end_loop(self):
        if self.max_ticks is None:
            end = False
        else:
            end = self.ticks >= self.max_ticks
        return (end)

    def time_to_ask(self):
        if self.chk_ticks == None:
            ask = False
        else:
            ask = self.ticks % self.chk_ticks == 0
        return (ask)

    def draw(self):
        spc_len = IO_def["spacing"] # Multiplier for tiles spacing.
        spc_str = " " * spc_len
        extend_block = IO_def["extend_block"]

        # Clear screen and scrollback buffer
        os.system('clear')
        os.system("printf '\e[3J'")


        # Title on top
        title = " " + self.name + " "
        time = " " + str(self.ticks) + " "
        fill = " " * max(0, ((1+spc_len) * self.width - len(title) - len(time) - spc_len))
        title = colors.colorize_bg(title, 'white', 'normal', 'blue', 'normal', 'bold')
        time = colors.colorize_bg(time, 'white', 'normal', 'red')
        fill = colors.colorize_bg(fill, 'white', 'normal', 'blue')
        header = title + fill + time
        print(header)

        # Now the board: loop over rows from top down to bottom
        if IO_def["color"]:
            # COLOR version
            for y in range(self.height - 1, -1, -1):
                line = ""
                for x in range (self.width):
                    thing = self.things[x, y]
                    if thing == None:
                        # Empty tile
                        tile = self.ground[x, y]
                        line += colors.colorize_bg(tile.aspect + spc_str, \
                                tile.color, tile.intensity, self.bg_color, self.bg_intensity)
                    else:
                        # Some Agent/BLock on it. TBA: customize 'bold' as agent's attrib.
                        if isinstance(thing, Block) and extend_block:
                            t_aspect = thing.aspect * (1 + spc_len)
                        else:
                            t_aspect = thing.aspect + spc_str
                        line += colors.colorize_bg(t_aspect, \
                                thing.color, thing.intensity, self.bg_color, self.bg_intensity, 'bold')
                print(line)

        else:
            # MONOCHROME version
            for y in range(self.height - 1, -1, -1):
                line = ""
                for x in range (self.width):
                    thing = self.things[x, y]
                    if thing == None:
                        # Empty tile
                        line += self.ground[x, y].aspect + spc_str
                    else:
                        # Some Agent/Block on it
                        line += thing.aspect + spc_str
                print(line)

