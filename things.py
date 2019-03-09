###############################################################
# Agents 
# for "Lil' ASCII Lab" and its entities...

###############################################################
# IMPORT

# libraries
# (none)

# Modules
import ai
import ui

# Agent definition:
#   number of instances to place
#   type, i.e. its name
#   aspect: one single Unicode character (e.g. "𝝮")
#   color & intensity:  (see above)
#   initial position (or RND). If more than one instance, it will be ignored.
#   (energy-related settings:)
#       initial energy assigned at start
#       maximum energy the agent can acquire
#       bite power, amount of energy the agent can take with one bite
#       step_cost, i.e. energy consumption per step regardless of action
#   senses: the function translating the environment into input for an agent's mind.
#   mind: the cognitive function processing senses to output actions.
Agents_def = (
    (1, "wanderer", "⚉", ui.GREEN, ui.BRIGHT, [None, None], \
        (110, 110.5, 5, -0.01), None, ai.wanderer),
    (1, "Omi", "Ω", ui.BLUE, ui.BRIGHT, [None, None], \
        (100, 110, 5, -1), None, None),
    (2, "foe", "Д", ui.MAGENTA, ui.NORMAL, [None, None], \
        (100, 110, 10, -1), None, None),
    (3, "apple", "", ui.RED, ui.BRIGHT, [None, None], \
        (20, 20, 0, -0.001), None, None),
    (3, "star", "*", ui.YELLOW, ui.BRIGHT, [None, None], \
        (30, 30, 0, 0), None, None),
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
        self.senses = a_def[6]
        self.mind = a_def[7]
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
        # First, update agent's interpretation of the world (its current_state)
        self.current_state = self.interpret_state(world)
        # Now its "mind" is requested to choose an action
        self.chosen_action = self.run_policy(world, self.current_state)
        
        return self.chosen_action

    def interpret_state(self, world):
        # Extraction of the information available for the agent.
        # - Based on its 'senses'
        # - TBA: other inputs (e.g. messages...)

        # Default: Complete information, the whole world is visible.
        if self.senses == None:
            state = world

        return state

    def run_policy(self, world, state):
        # Policy function returning the action chosen by the agent based on state.
        # NOTE: 'world' is only passed in order to call auxiliary methods.

        # Default: No action
        if self.mind == None:
            action = None
        else:
            action = self.mind(self, world, state)

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
