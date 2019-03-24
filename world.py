###############################################################
# The world
# for "Lil' ASCII Lab" and its entities...

###############################################################

import numpy as np
import random
import time

import things
import ui

# World definition:

WORLD_DEF = {
    "name": "Random Blox",
    "width": 20,  # x from 0 to width - 1
    "height": 15,  # y from 0 to height - 1
    "bg_color": ui.BLACK,  # background color (see ui.py module).
    "bg_intensity": ui.NORMAL,  # background intensity (NORMAL or BRIGHT).
    "n_blocks_rnd": 0.4,  # % of +/- randomness in number of blocks [0, 1]
    "max_steps": None,  # How long to run the world ('None' for infinite loop).
    "fps": None,  # Frames-Per-Second, i.e. number of steps run per second.
    "random_seed": None,  # Seed for reproducible runs (None for random).
}

# Simulation definition:
# Theses are the settings provided to the world:
Simulation_def = (
    WORLD_DEF,  # Some specific world definition.
    things.TILE_DEF,  # The tiles it will contain.
    things.BLOCKS_DEF,  # The blocks to put in it.
    things.AGENTS_DEF,  # The agents who will live in it.
)

# Constants:
WORLD_DEFAULT_FPS = 60  # Fall-back world speed (in frames-per-second).
WORLD_DEFAULT_SPF = 1 / WORLD_DEFAULT_FPS  # (the same in seconds-per-frame).

###############################################################


class World:
    # A tiled, rectangular setting on which a little universe takes life.
    def __init__(self, Simulation_def):
        # Create a world from the definitions given.
        w_def = Simulation_def[0]
        t_def = Simulation_def[1]
        b_def = Simulation_def[2]
        a_def = Simulation_def[3]

        # Assign values from w_def.
        self.name = w_def["name"]
        self.width = w_def["width"]
        self.height = w_def["height"]
        self.bg_color = w_def["bg_color"]
        self.bg_intensity = w_def["bg_intensity"]
        self.n_blocks_rnd = w_def["n_blocks_rnd"]
        self.max_steps = w_def["max_steps"]
        # Time and speed settings.
        self.initialize_fps(w_def["fps"])

        self.paused = False
        self.creation_time = time.time

        # Initialize world: randomness, steps and list of 'things' on it.
        seed = w_def["random_seed"]
        if seed is None:
            seed = time.time()
        self.random_seed = seed
        random.seed(seed)

        self.steps = 0
        self.things = np.full((self.width, self.height), None)  # Create grid for agents and blocks.

        # Put TILES on the ground.
        self.ground = np.full((self.width, self.height), None)  # Fill in the basis of the world.
        for x in range(self.width):
            for y in range(self.height):
                # Create tile (position set in t_def[4] is ignored).
                tile = things.Tile(t_def[0], t_def[1], t_def[2], t_def[3], [x, y])
                self.ground[x, y] = tile

                # Put AGENTS in the world.
        self.agents = []  # List of all types of agent in the world.
        self.tracked_agent = None  # The agent to track during simulation.
        for a in a_def:  # Loop over the types of agent defined.
            single_instance = a[0] == 1
            for i in range(a[0]):  # Create the # of instances specified.
                # Create agent as defined.
                if single_instance:
                    agent_suffix = None
                else:
                    agent_suffix = i
                agent = things.Agent(a[1:], agent_suffix)
                # Put agent in the world on requested position, relocating on colisions (on failure, Agent is ignored).
                _ = self.place_at(agent, agent.position, relocate=True)
                self.agents.append(agent)
                if self.tracked_agent is None:
                    self.tracked_agent = agent

        # Put in some BLOCKS, quantity based on width,
        self.blocks = []
        for b in b_def:  # List of all types of block in the world.
            if (b[0] is None):  # Unspecified number of blocks.
                n_random_blocks = (self.width * self.n_blocks_rnd) // 1  # abs. max variation.
                n_random_blocks = self.width + random.randint(-n_random_blocks, n_random_blocks)
            else:  # Specified # of blocks.
                n_random_blocks = b[0]

            n = 0
            while n < n_random_blocks:
                block = things.Block(b[1], b[2], b[3], b[4], b[5])
                _ = self.place_at(block)  # Put in random position if possible (fail condition ignored).
                self.blocks.append(block)
                n += 1

    def initialize_fps(self, fps):
        # fps, spf is the current world speed (frames-per-second, seconds-per-frame).
        # original_fps, original_spf keeps the original setting.
        # previous_fps remembers latest fps speed before going 'full-speed',
        # or establishes WORLD_DEFAULT_FPS when starting af 'full-speed'.

        self.fps = fps
        if fps is None:
            self.spf = None
            self.previous_fps = WORLD_DEFAULT_FPS

        else:
            self.spf = 1 / fps
            self.previous_fps = fps

        self.original_fps = self.fps
        self.original_spf = self.spf

    def update_fps(self, fps_factor):
        if fps_factor is None:
            # 'None' means 'go full-speed'.
            if self.fps is None:
                # Already at full-speed; no action needed.
                pass
            else:
                # Update needed.
                self.previous_fps = self.fps
                self.fps = None
                self.spf = None
        else:
            # Check current fps.
            if self.fps is None:
                # Slow down from 'full-speed' to previous fps/spf.
                self.fps = self.previous_fps
            else:
                # Simply apply factor to fps.
                self.fps *= fps_factor
            # Update spf.
            self.spf = 1 / self.fps

    def seconds_run(self):
        # Return the number of seconds run in world's time based on spf(seconds per frame).
        # Assumptions:
        # - Since speed can vary at user's request, original_spf is assumed.
        # - And if original_fps was None, WORLD_DEFAULT_SPF us assumed.

        if self.original_spf is not None:
            referential_spf = self.original_spf
        else:
            referential_spf = WORLD_DEFAULT_SPF

        return (self.steps * referential_spf) // 1

    def place_at(self, thing, position=[None, None], relocate=False):
        # If position is not defined, find a random free place and move the Thing there.
        # If position is defined,
        #       if not occupied, move a Thing to position;
        #       if occupied, relocate randomly if allowed by 'relocate', or fail otherwise.
        # Result of action: (True: success; False: fail).
        if position == [None, None]:
            # position not defined; try to find a random one.
            position, success = self.find_free_tile()
        else:
            # position is defined; check if it is empty.
            if self.tile_is_empty(position):
                # position is empty: success!
                success = True
            elif relocate:
                # position is occupied, try to relocate as requested.
                position, success = self.find_free_tile()
            else:
                # position is occupied and no relocation requested; FAIL.
                success = False

        if success:
            # The move is possible, relocate Thing.
            if thing.position[0] is not None and thing.position[1] is not None:
                # The Thing was already in the world; clear out old place.
                self.things[thing.position[0], thing.position[1]] = None
            self.things[position[0], position[1]] = thing
            thing.position = position

        return success

    def tile_is_empty(self, position):
        # Check if a given position exists within world's limits and is free.
        x, y = position
        if (0 <= x <= self.width - 1) and (0 <= y <= self.height - 1):
            result = self.things[x, y] is None
        else:
            result = False
        return result

    def tile_with_agent(self, position):
        # Check if a given position exists within world's limits and has an agent on it.
        x, y = position
        if (0 <= x <= self.width - 1) and (0 <= y <= self.height - 1):
            result = isinstance(self.things[x, y], things.Agent)
        else:
            result = False
        return result

    def find_free_tile(self):
        # Try to find a tile that is empty in the world.
        # Result of action: (True: success; False: fail).

        # First, try a random tile.
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        found = self.tile_is_empty([x, y])

        x0, y0 = x, y  # Starting position to search from.
        success = True
        while not found and success:
            x = (x + 1) % self.width  # Increment x not exceeding width
            if x == 0:  # When x is back to 0, increment y not exceeding height
                y = (y + 1) % self.height
            if self.tile_is_empty([x, y]):  # Check "success" condition
                found = True
            elif (x, y) == (x0, y0):  # Failed if loop over the world is complete.
                success = False

        return [x, y], success

    def get_adjacent_empty_tiles(self, position):
        # Return a list with all adjacent empty tiles, respecting world's borders
        x0, y0 = position
        tiles = []
        for x_inc in (-1, 0, 1):
            for y_inc in (-1, 0, 1):
                if (x_inc, y_inc) != (0, 0):  # Skipping tile on which agent stands
                    if self.tile_is_empty([x0 + x_inc, y0 + y_inc]):
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
            action = agent.choose_action(world=self)
            # Try to execute action.
            success, energy_delta = self.execute_action(agent, action)
            # Set new position, reward, other internal information.
            agent.update(action, success, energy_delta)

        # Update the world's info
        self.agents.sort(key=lambda x: x.energy, reverse=True)
        self.steps += 1

    def execute_action(self, agent, action):
        # Check if the action is feasible and execute it returning results.
        action_type, action_arguments, action_energy_ratio = action
        # Calculate energy cost IF action is actually made.
        action_delta = agent.move_cost * action_energy_ratio

        if action_delta > agent.energy:
            # Not enough energy for the move.
            success = False
            action_delta = 0

        elif action_type == "None":
            # Rest action
            success = True

        elif action_type == "MOVE":
            # Check destination tile is free.
            success = self.place_at(agent,
                                    [agent.position[0] + action_arguments[0],
                                     agent.position[1] + action_arguments[1]]
                                    )
            if not success:
                action_delta = 0
                # TODO: Penalize collisions through energy_delta?

        elif action_type == "FEED":
            prey = self.things[agent.position[0] + action_arguments[0],
                               agent.position[1] + action_arguments[1]]
            if prey is not None:
                # Take energy from prey (limited by prey's energy).
                energy_taken = prey.update_energy(-agent.bite_power)
                action_delta += - energy_taken
                success = action_delta > 0
            else:
                success = False
                action_delta = 0

        else:
            raise Exception('Invalid action type passed: {}.'.format(action_type))

        energy_delta = action_delta + agent.step_cost
        return success, energy_delta

    def is_end_loop(self):
        # Check if the world's loop has come to an end.
        if self.max_steps is None:
            end = False
        else:
            end = self.steps >= self.max_steps

        return end

    def process_key_stroke(self, key):
        # Process user's keyboard input:
        #   - Left / right key to control simulation speed.
        #   - Space to pause simulation.
        #   - Tab to change tracked_agent.

        if key == -1:  # No key pressed.
            pass
        elif key in [ui.KEY_LEFT, ui.KEY_SLEFT]:  # Slow down speed.
            self.update_fps(fps_factor=0.5)
        elif key in [ui.KEY_RIGHT, ui.KEY_SRIGHT]:  # Faster speed.
            self.update_fps(fps_factor=2.0)
        elif key in [ui.KEY_UP]:  # Go full speed!
            self.update_fps(fps_factor=None)
        elif key == ord(' '):  # Pause the world.
            self.paused = True
        elif key == ord('\t'):  # Track a different agent.
            initial_idx = idx = self.agents.index(self.tracked_agent)
            next_agent = None
            end_search = False
            while not end_search:
                # Pick next index, and its corresponding agent.
                if idx == len(self.agents) - 1:
                    idx = 0
                else:
                    idx += 1
                next_agent = self.agents[idx]
                # Check if valid, or if full cycle is complete.
                if (next_agent.mind is not None and next_agent.energy > 0) or idx == initial_idx:
                    end_search = True
            self.tracked_agent = next_agent


###############################################################
# MAIN PROGRAM
# (code for TESTING purposes only.)

if __name__ == '__main__':
    print("world.py is a module of Lil' ASCII Lab and has no real main module.")
    _ = input("Press to exit...")
