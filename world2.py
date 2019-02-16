###############################################################
# The world for the game
# and its entities...

###############################################################
# MODULES

import numpy as np
import ui

###############################################################
# DEFINITIONS

# World definition:
#
World_def = {
    "name":         "Lil' ASCII Lab",
    "width":        10,                 # x from 0 to WIDTH -1
    "height":       6,                  # y from 0 to HEIGHT -1
    "bg_color":     ui.BLACK,           # background color (-1 for transparent in curses)
    "bg_intensity": ui.NORMAL,          # background intensity (NORMAL or BRIGHT)
    "n_blocks_rnd": 0.4,                # % of +/- randomness in number of blocks.
    "max_ticks":    100,                # How long to run the world ('None' for infinite loop).
    "chk_ticks":    10                  # How often to ask user for quit/go-on ('None' = never ask).
}

# Tiles definition:
# type of tile, aspect, color, intensity, position (not specified here)
Tile_def = (
    ("tile", "…", ui.BLACK, ui.BRIGHT, [None, None])
)

# Block definition: 
# number of instances (or RND), block type, aspect, color, intensity, position (not specified here).
Block_def = (
    (4, "plant", " ", ui.BLUE, ui.NORMAL, [None, None]),
    (None, "block", "█", ui.BLACK, ui.BRIGHT, [None, None]),
)

# Agent definition:
# number of instances, agent type, aspect, color, intensity, initial position (or RND), ai.
Agents_def = (
    (1, "Omi", "𝝮", ui.GREEN, ui.BRIGHT, [0, 0], None),
    (3, "apple", "", ui.RED, ui.BRIGHT, [None, None], None),
    (3, "star", "*", ui.YELLOW, ui.BRIGHT, [None, None], None),
)

# Interesting characters:  ~ … . · ˙ • ° † ∞  ◊ ∆ ¯-_ |-/\  <v^> ∏ 
# Extended ASCII: 176░ 177▒ 178▓ 219█ 254■
# https://theasciicode.com.ar/extended-ascii-code/graphic-character-medium-density-dotted-ascii-code-177.html


###############################################################
# CLASSES

class Thing:
    # Root class containing the common attributes for all classes.
    def __init__(self, name, aspect, color, intensity, position):
        self.name = name                # Name of the thing
        self.aspect = aspect            # Text character to be printed like
        self.color = color              # Color for the character
        self.intensity = intensity      # intensity to apply
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


