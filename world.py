###############################################################
# The world 
# for "Lil' ASCII Lab" and its entities...

###############################################################
# IMPORT

# libraries
import numpy as np
import random
import time

# Modules
import ui

###############################################################
#   SETTINGS
#   color:  from among 8 options (BLACK, BLUE, CYAN, GREEN, MAGENTA, RED, WHITE, YELLOW)
#   intensity: NORMAL or BRIGHT

# World definition:
#
World_def = {
    "name":         "Random Blox",
    "width":        20,                 # x from 0 to width - 1
    "height":       14,                 # y from 0 to height - 1
    "bg_color":     ui.BLACK,           # background color
    "bg_intensity": ui.NORMAL,          # background intensity (NORMAL or BRIGHT)
    "n_blocks_rnd": 0.4,                # % of +/- randomness in number of blocks [0, 1]
    "max_steps":    None,               # How long to run the world ('None' for infinite loop)
    "chk_steps":    100,                 # How often to ask user for quit/go-on ('None' = never ask)
    "fps":          10,                 # Number of steps to run per second (TBA: full speed if 'None'?)
    "random_seed":  None,               # Define seed to produce repeatable executions or None for random.
}

# Tiles definition:
# type of tile, aspect, color, intensity, position (not specified here)
Tile_def = (
    ("tile", "·", ui.BLACK, ui.BRIGHT, [None, None])
)

# Block definition: 
#   number of instances (or None for RND, based on world's width and % of randomness)
#   type, i.e. its name
#   aspect: " " for a generic full block (which will be doubled to fit world's spacing)
#           ONE single Unicode character, e.g. "#" (which will be doubled to fit world's spacing)
#           TWO Unicode characters for specific styles (e.g. "[]", "▛▜", "◢◣")
#   color & intensity:  (see above)
#   position:   (a tuple, currently ignored)
Block_def = (
#    (None, "block", " ", ui.BLACK, ui.BRIGHT, [None, None]),
#    (4, "block2", "▛▜", ui.BLUE, ui.NORMAL, [None, None]),
    (10, "fence", "#", ui.BLACK, ui.BRIGHT, [None, None]),
    (40, "fence2", "▓", ui.BLACK, ui.BRIGHT, [None, None]),
)

# Agent definition:
#   number of instances
#   type, i.e. its name
#   aspect: one single Unicode character (e.g. "𝝮")
#   color & intensity:  (see above)
#   initial position (or RND). If more than one instance, it will be ignored.
#   (energy-related settings:)
#       initial energy assigned at start
#       maximum energy the agent can acquire
#       bite power, amount of energy the agent can take with one bite
#       step_cost, i.e. energy consumption per step regardless of action
#   ai (currently ignored)
Agents_def = (
    (1, "wanderer", "⚉", ui.GREEN, ui.BRIGHT, [None, None], \
        (110, 110.5, 5, -0.001), None),
    (1, "Omi", "Ω", ui.BLUE, ui.BRIGHT, [None, None], \
        (100, 110, 5, -1), None),
    (2, "foe", "Д", ui.MAGENTA, ui.NORMAL, [None, None], \
        (100, 110, 10, -1), None),
    (3, "apple", "", ui.RED, ui.BRIGHT, [None, None], \
        (20, 20, 0, -0.001), None),
    (3, "star", "*", ui.YELLOW, ui.BRIGHT, [None, None], \
        (30, 30, 0, 0), None),
)

# Actions definition:
# An action consists of a verb and some arguments, expressed between brackets here.
Actions_def = (
    None,       # None (None)   Passive action, it has no arguments.
    "MOVE",     # MOVE (X, Y)   Moving to specified coordinates.
    "FEED",     # FEED (X, Y)   Feed on Agent in coordinates.
)

###############################################################
# CLASSES
# Thing --- Tile
#        |- Block
#        |- Agent

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
    # Default class for Agents
    num_agents = 0
    def __init__(self, a_def):
        # Initialize inherited and specific attributes
        super().__init__(a_def[0], a_def[1], a_def[2], a_def[3], a_def[4])
        self.energy     = a_def[5][0]
        self.max_energy = a_def[5][1]
        self.bite_power = a_def[5][2]
        self.step_cost  = a_def[5][3]
        self.ai = a_def[6]
        self.steps = 0
        # Initialize current_state, current_energy_delta and chosen_action
        self.current_state = None
        self.current_energy_delta = 0
        self.chosen_action = None
        # Update class variable
        Agent.num_agents += 1

    def update_energy(self, delta):
        # Keep within 0 and agent's max_energy
        self.current_energy_delta = delta
        self.energy = max(min(self.energy + delta, self.max_energy), 0)

    def choose_action(self, world):
        self.current_state = self.interpret_state(world)
        action = self.policy(self.current_state)
        return action

    def interpret_state(self, world):
        # Extraction of the information available for the agent.
        # Default: Complete information, the whole world is visible.
        return world

    def policy(self, state):
        # Policy function returning the action chosen by the agent
        # Default: No action
        action = None
        self.chosen_action = action

        return action

    def update(self, action, success, energy_delta):
        # Update state of agent after trying some action
        # No moves or anything for now...
        # self.aspect = ...
        # self.color = ...
        # self.position = ...
        self.update_energy(energy_delta)

        # Execute policy update (learning) based on:
        #   self.current_state (S_t)
        #   self.current_energy_delta (r_t)
        #   self.chosen_action (A_t)

        self.steps +=1

###############################################################
# CLASSES
# World

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
        self.max_steps = w_def["max_steps"]
        self.chk_steps = w_def["chk_steps"]
        self.fps = w_def["fps"]
        self.spf = 1/self.fps
        self.creation_time = time.time

        # Initialize world: randomness, steps and list of 'things' on it.
        seed = w_def["random_seed"]
        if seed == None: seed = time.time()
        self.random_seed = seed
        random.seed(seed)

        self.steps = 0
        self.things = np.full((self.width, self.height), None) # create grid for agents and blocks

        # put TILES on the ground
        self.ground = np.full((self.width, self.height), None) # fill in the basis of the world.
        for x in range(self.width):
            for y in range(self.height):
                # Create tile (position set in t_def[4] is ignored).
                tile = Tile(t_def[0], t_def[1], t_def[2], t_def[3], [x, y])
                self.ground[x, y] = tile           

        # put AGENTS in the world
        self.agents = []                # list of all types of agent in the world
        self.tracked_agent = None       # the agent to track during simulation
        for a in a_def:                 # loop over the types of agent defined
            for i in range(a[0]):       # create the # of instances specified
                # Create agent
                agent = Agent(a[1:])    # definition of the agent
                # Put agent in the world on requested position, relocating on colisions.
                _ = self.move_to(agent, agent.position[0], agent.position[1], relocate=True)
                self.agents.append(agent)
                if self.tracked_agent == None:
                    self.tracked_agent = agent

        # put in some BLOCKS, # based on width
        self.blocks = []
        for b in b_def:                 # list of all types of block in the world.
            if(b[0] == None):           # Unspecified number of blocks.
                n_random_blocks = (self.width * self.n_blocks_rnd) // 1 # abs. max variation
                n_random_blocks = self.width + random.randint(-n_random_blocks, n_random_blocks)
            else:                       # Specified # of blocks.
                n_random_blocks = b[0]

            n = 0
            while n < n_random_blocks:
                block = Block(b[1], b[2], b[3], b[4], b[5])
                _ = self.move_to(block)      # Put in random position
                self.blocks.append(block)
                n += 1

    def move_to(self, thing, x = None, y = None, relocate = False):
        # If x, y not defined, find a random free place and move the Thing there.
        # If x, y are defined,
        #       if not occupied, move a Thing to x, y;
        #       if occupied, relocate randomly if specified, or fail otherwise.
        # Fail condition (0: success; 1: fail)        
        if x == None or y == None:
            # x, y not defined; try to  find some random position.
            position, success = self.find_free_tile()
        else:
            # x, y are defined; check if position is empty.
            if self.is_empty(x, y):
                # position is empty
                position, success = [x, y], 0
            elif relocate:
                # position is occupied, try to relocate as requested
                position, success = self.find_free_tile()
            else:
                # position is occupied and no relocation requested; FAIL.
                success = 1
        
        if (success == 0):
            # The move is possible, proceed now.
            if (thing.position[0] != None and thing.position[1] != None):
                # The Thing was already in the world; clear out old place.
                self.things[thing.position[0], thing.position[1]] = None
            self.things[position[0], position[1]] = thing
            thing.position = position

        return (success)

    def is_empty(self, x, y):
        # Check if a given position is free
        return (self.things[x, y] == None)

    def find_free_tile(self):
        # Try a random tile
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        found = self.is_empty(x, y)

        x0, y0 = x, y                   # Starting position to search from
        success = 0                         # Fail condition (0: success; 1: board is full)
        while not found and not (success == 1):
            x = (x+1)%self.width        # Increment x not exceeding width
            if x == 0 :                 # When x is back to 0, increment y not exceeding height
                y = (y+1)%self.height
            if self.is_empty(x, y):     # Check "success" condition
                found = True
            elif (x, y) == (x0, y0):    # Check "fail" condition
                success = 1

        return (x, y), success

    def step(self):
        # Run step over all "living" agents
        for agent in filter(lambda a: a.energy > 0, self.agents):
            # request action from agent based on world state
            action = agent.choose_action(self)
            # resolve results of trying to execute action
            success, energy_delta = self.execute_action(agent, action)
            # Set new position, reward, other internal information
            agent.update(action, success, energy_delta)

        # update the world's info
        self.agents.sort(key = lambda x: x.energy, reverse=True)
        self.steps +=1

    def execute_action(self, agent, action):
        # Check if the action is feasible and execute it returning results
        # if action == None:
        success = True
        energy_delta = 0
            
        return success, energy_delta + agent.step_cost

    def is_end_loop(self):
        if self.max_steps is None:
            end = False
        else:
            end = self.steps >= self.max_steps
        return (end)

    def time_to_ask(self):
        if self.chk_steps == None:
            ask = False
        else:
            ask = self.steps % self.chk_steps == 0
        return (ask)

###############################################################
# MAIN PROGRAM
# code for TESTING purposes only

if __name__ == '__main__':
    print("world.py is a module of Lil' ASCII Lab and has no real main module.")
    _ = input("Press to exit...")



