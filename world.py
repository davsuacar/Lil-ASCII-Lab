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
import things
import ui

###############################################################
#   SETTINGS

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
    "chk_steps":    100,                 # How often user will be asked for quit/go-on ('None' = never ask)
    "fps":          2,                 # Number of steps to run per second (TODO: full speed if 'None'?)
    "random_seed":  None,               # Define seed to produce repeatable executions or None for random.
}
#   color:  from among 8 options (BLACK, BLUE, CYAN, GREEN, MAGENTA, RED, WHITE, YELLOW)
#   intensity: NORMAL or BRIGHT


# Simulation defition:
# The settings provided to the world.
Simulation_def = (
    World_def,          # Some specific world definition.
    things.Tile_def,    # The tiles it will contain.
    things.Blocks_def,  # The blocks to put in it.
    things.Agents_def,  # The agents who will live in it.
)

###############################################################
# CLASSES
# World

class World:
    # A tiled, rectangular setting on which a little universe takes life.
    def __init__(self, Simulation_def):
        # Create a world from the definitions given
        w_def = Simulation_def[0]
        t_def = Simulation_def[1]
        b_def = Simulation_def[2]
        a_def = Simulation_def[3]

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
        self.things = np.full((self.width, self.height), None) # Create grid for agents and blocks.

        # Put TILES on the ground.
        self.ground = np.full((self.width, self.height), None) # Fill in the basis of the world.
        for x in range(self.width):
            for y in range(self.height):
                # Create tile (position set in t_def[4] is ignored).
                tile = things.Tile(t_def[0], t_def[1], t_def[2], t_def[3], [x, y])
                self.ground[x, y] = tile           

        # Put AGENTS in the world.
        self.agents = []                # List of all types of agent in the world.
        self.tracked_agent = None       # The agent to track during simulation.
        for a in a_def:                 # Loop over the types of agent defined.
            for i in range(a[0]):       # Create the # of instances specified.
                # Create agent as defined.
                agent = things.Agent(a[1:])
                # Put agent in the world on requested position, relocating on colisions (on failure, Agent is ignored).
                _ = self.move_to(agent, agent.position[0], agent.position[1], relocate=True)
                self.agents.append(agent)
                if self.tracked_agent == None:
                    self.tracked_agent = agent

        # Put in some BLOCKS, quantity based on width,
        self.blocks = []
        for b in b_def:                 # List of all types of block in the world.
            if(b[0] == None):           # Unspecified number of blocks.
                n_random_blocks = (self.width * self.n_blocks_rnd) // 1 # abs. max variation.
                n_random_blocks = self.width + random.randint(-n_random_blocks, n_random_blocks)
            else:                       # Specified # of blocks.
                n_random_blocks = b[0]

            n = 0
            while n < n_random_blocks:
                block = things.Block(b[1], b[2], b[3], b[4], b[5])
                _ = self.move_to(block)      # Put in random position is possible (fail condition ignored).
                self.blocks.append(block)
                n += 1

    def move_to(self, thing, x = None, y = None, relocate = False):
        # TODO: simplify interface to 'position' instead of x, y.
        # If x, y not defined, find a random free place and move the Thing there.
        # If x, y are defined,
        #       if not occupied, move a Thing to x, y;
        #       if occupied, relocate randomly if allowed by 'relocate', or fail otherwise.
        # Result of action: (True: success; False: fail).
        if x == None or y == None:
            # x, y are not defined; try to  find some random position.
            position, success = self.find_free_tile()
        else:
            # x, y are defined; check if position is empty.
            if self.is_tile_empty([x, y]):
                # Position is empty: success!
                position, success = [x, y], True
            elif relocate:
                # Position is occupied, try to relocate as requested.
                position, success = self.find_free_tile()
            else:
                # Position is occupied and no relocation requested; FAIL.
                success = False
        
        if success:
            # The move is possible, relocate Thing.
            if (thing.position[0] != None and thing.position[1] != None):
                # The Thing was already in the world; clear out old place.
                self.things[thing.position[0], thing.position[1]] = None
            self.things[position[0], position[1]] = thing
            thing.position = position

        return (success)

    def is_tile_empty(self, position):
        # Check if a given position exists within world's limits and is free.
        x, y = position
        if (0 <= x <= self.width - 1) and (0 <= y <= self.height - 1):
            result = self.things[x, y] == None
        else:
            result = False
        return result

    def find_free_tile(self):
        # Try to find a tile that is empty in the world.
        # Result of action: (True: success; False: fail).

        # First, try a random tile.
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        found = self.is_tile_empty([x, y])

        x0, y0 = x, y                   # Starting position to search from.
        success = True
        while not found and success:
            x = (x+1)%self.width        # Increment x not exceeding width
            if x == 0 :                 # When x is back to 0, increment y not exceeding height
                y = (y+1)%self.height
            if self.is_tile_empty([x, y]):     # Check "success" condition
                found = True
            elif (x, y) == (x0, y0):    # Failed if loop over the world is complete.
                success = False

        return (x, y), success

    def get_adjacent_empty_tiles(self, position):
        # Return a list with all adjacent empty tiles, respecting world's borders
        x0, y0 = position
        tiles = []
        for x_inc in (-1, 0, 1):
            for y_inc in (-1, 0, 1):
                if (x_inc, y_inc) != (0, 0):  # Skipping tile on which agent stands
                    if self.is_tile_empty([x0 + x_inc, y0 + y_inc]):
                        tiles.append((x0 + x_inc, y0 + y_inc))
                        
        return tiles

    def find_free_adjacent_tile(self, position):
        # TODO
        x0, y0 = position
        return False, position

    def step(self):
        # Run step over all "living" agents.
        for agent in filter(lambda a: a.energy > 0, self.agents):
            # Request action from agent based on world state.
            action = agent.choose_action(world = self)
            # Resolve results of trying to execute action.
            success, energy_delta = self.execute_action(agent, action)
            # Set new position, reward, other internal information.
            agent.update(action, success, energy_delta)

        # Update the world's info
        self.agents.sort(key = lambda x: x.energy, reverse=True)
        self.steps +=1

    def execute_action(self, agent, action):
        # Check if the action is feasible and execute it returning results.
        if action[0] == "None":
            pass
            success = True
            energy_delta = 0
        elif action[0] == "MOVE":
            success = self.move_to(agent,\
                x=agent.position[0]+action[1][0],\
                y=agent.position[1]+action[1][1])
            if success: energy_delta = agent.move_cost
            else:       energy_delta = 0 # TODO: Penalize collisions?
        else:
            # TODO: Handle unkown actions!
            success = True
            energy_delta = 0
            
        return success, energy_delta + agent.step_cost

    def is_end_loop(self):
        # Check if the world's loop has come to an end.
        if self.max_steps is None:
            end = False
        else:
            end = self.steps >= self.max_steps
        return (end)

    def time_to_ask(self):
        # Check if the step has come to ask user.
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



