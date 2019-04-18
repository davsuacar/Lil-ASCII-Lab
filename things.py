###############################################################################
# Classess of Thing in an LAL 'World':
# Thing --- Tile
#        ├- Block
#        └- Agent
###############################################################################

import ai
import ui

###############################################################################
# THING:
# Settings defining any 'Thing' (Tile, Block or Agent) in the 'World':

Thing_settings_def = namedtuple("Thing_settings_def", [
    'name',  # Some descriptive text (e.g. "bug").
    'aspect',  # One single Unicode character (e.g. "⚉").
    'color',  # Its normal color (e.g. ui.CYAN). (See ui.py module).
    'intensity',  # Its normal intensity (e.g. ui.BRIGHT). (See ui.py module).
    'initial_position',  # Its initial position (or RND). If 'n_instances' > 1, it will be used for the first one only.
])

# Constants
RANDOM_POSITION = (None, None)

###############################################################################
# TILE:
# Settings defining a 'Tile':

pass  # Currently Tiles are defined through common "Thing_settings_def".

###############################################################################
# BLOCK:
# Settings defining a 'Block':

Block_def = namedtuple("Block_def", [
    'n_instances',  # Number of Blocks to place (e.g. 20).
    'thing_settings',  # Generic settings common to all Things (Tile, Block, Agent).
])

###############################################################################
# AGENT:
# Settings defining an 'Agent':

Agent_def = namedtuple("Agent_def", [
    'n_instances',  # Number of instances to place (e.g. 10).
    'thing_settings',  # Generic settings common to all Things (Tile, Block, Agent).
    'energy_settings',  # Energy-related settings (see 'Energy_settings_def').
    'ai_settings'  # Functions used for perception, action and learning.
    ])

Energy_settings_def = namedtuple("Energy_settings_def", [
    'initial_energy',  # Initial energy assigned at start.
    'maximum_energy',  # Maximum energy the agent can acquire.
    'bite_power',  # Amount of energy the agent can take with one bite.
    'step_cost',  # Energy consumed on each world step regardless of action chosen.
    'move_cost'  # Energy consumed for moving to an adjacent tile.
    'recycling_type'  # Dynamics ruling its energy losses and 'death'.
])

# Constants:
# Agents' recycling_settings: types of dynamics.
NON_RECHARGEABLE = None  # Regular loss; useless after 'death'.
RECHARGEABLE = 'Rechargeable'  # Regular loss; can be recharged after 'death'.
EVERLASTING = 'Everlasting'  # NO loss regardless of energy taken.
RESPAWNABLE = 'Respawnable'  # Regular loss; resurrected after death at random location.

#   Mind/perception:
#       The function translating the environment into input for an agent's mind.
#       It's not limited to the external world, and can include internal information (e.g. energy level).
#       If None, ai.default_senses() is assigned.
#   Mind/action:
#       The function processing perception to output actions.
#       If None, a NO_ACTION will always be assumed.
#   Mind/learning:
#       The function updating the acting policy after an action is executed.
#       In None, the learning step is simply skipped.
AI_settings_def = namedtuple("AI_settings_def", [
    'perception',  # World -> AI input.
    'action',  # AI input -> Action.
    'learning'  # Action, Reward -> New AI.
])

###############################################################################
# World's casting
# All things to populate this instance of 'World'.
###############################################################################

# Tiles definition:
# name, aspect, color, intensity, initial_position.
TILE_DEF = (
    Thing_settings_def("ground", "·", ui.BLUE, ui.NORMAL, RANDOM_POSITION)
)

# Block definition:
#   Number of instances (or None for RND, based on world's width and % of randomness).
#   Type, i.e. its name.
#   Aspect: " " for a generic full block (which will be doubled to fit world's spacing).
#           ONE single Unicode character, e.g. "#" (which will be doubled to fit world's spacing).
#           TWO Unicode characters for specific styles (e.g. "[]", "▛▜", "◢◣").
#   Color & intensity: (see ui.py module).
#   Position: (a tuple, currently ignored).

BLOCKS_DEF = (
    #   (None, "full-block", " ", ui.BLACK, ui.BRIGHT, RANDOM_POSITION),
    #   (10, "fence", "#", ui.WHITE, ui.BRIGHT, RANDOM_POSITION),
    Block_def(
        20,
        Thing_settings_def("block", "▢", ui.BLUE, ui.BRIGHT, RANDOM_POSITION)
    )
)

AGENTS_DEF = (
    # With real minds:
    Agent_def(
        1,
        Thing_settings_def("Omi", "Ω", ui.CYAN, ui.BRIGHT, RANDOM_POSITION),
        Energy_settings_def(100, 110, 5, -0.1, -0.5, RESPAWNABLE),
        AI_settings_def(ai.full_info, ai.wanderer2, ai.no_learning)
    ),
    Agent_def(
        10,
        Thing_settings_def("bug", "⚉", ui.GREEN, ui.BRIGHT, RANDOM_POSITION),
        Energy_settings_def(100, 110, 5, -0.1, -0.1, NON_RECHARGEABLE),
        AI_settings_def(ai.full_info, ai.wanderer, ai.no_learning)
    ),
    Agent_def(
        0,
        Thing_settings_def("killer", "Ѫ", ui.RED, ui.BRIGHT, RANDOM_POSITION),
        Energy_settings_def(100, 110, 5, -0.1, -0.1, NON_RECHARGEABLE),
        AI_settings_def(ai.full_info, ai.wanderer, ai.no_learning)
    ),
    Agent_def(
        0,
        Thing_settings_def(0, "foe", "Д", ui.MAGENTA, ui.BRIGHT, RANDOM_POSITION),
        Energy_settings_def(100, 110, 10, -0.1, -1, RESPAWNABLE),
        AI_settings_def(ai.full_info, ai.wanderer, ai.no_learning)
    ),
    
    # Mindeless:
    Agent_def(
        5,
        Thing_settings_def("energy", "♥", ui.RED, ui.NORMAL, RANDOM_POSITION),
        Energy_settings_def(50, 50, 0, -0.001, 0, RESPAWNABLE),
        AI_settings_def(None, None, None)
    ),
    Agent_def(
        1,
        Thing_settings_def("recharger", "*", ui.YELLOW, ui.BRIGHT, RANDOM_POSITION),
        Energy_settings_def(30, 30, 0, 0, 0, EVERLASTING),
        AI_settings_def(None, None, None)
    )
)

###############################################################################
# Classess of Thing in an LAL 'World':
# Thing --- Tile
#        ├- Block
#        └- Agent
###############################################################################


class Thing:
    # Root class containing the common attributes for all classes.
    def __init__(self, thing_def):
        self.name = thing_def.name  # Name of the thing.
        self.aspect = thing_def.aspect  # Text character to display.
        self.color = thing_def.color  # Color for the character.
        self.intensity = thing_def.intensity  # Intensity to apply.
        self.position = thing_def.initial_position  # Its position in the world.


class Tile(Thing):
    pass  # Use root class'.


class Block(Thing):
    num_blocks = 0

    # It passively occupies one tile, never moving.
    def __init__(self, thing_def):
        # Initialize inherited attributes.
        super().__init__(thing_def)
        # Update class variable.
        Block.num_blocks += 1


class Agent(Thing):
    # Default class for Agents.
    num_agents = 0

    def __init__(self, a_def, agent_suffix=None):
        # Initialize inherited and specific attributes.
        super().__init__(name=a_def[0], aspect=a_def[1], color=a_def[2], intensity=a_def[3], position=a_def[4])
        if agent_suffix is not None:
            self.name = "{}_{}".format(self.name, str(agent_suffix))
        self.energy = a_def[5][0]
        self.max_energy = a_def[5][1]
        self.bite_power = a_def[5][2]
        self.step_cost = a_def[5][3]
        self.move_cost = a_def[5][4]

        # Attributes for recycling.
        self.recycling = a_def[6]
        self.original_color = self.color
        self.original_intensity = self.intensity

        # Agent's AI:
        self.perception = a_def[7][0]
        self.action = a_def[7][1]
        self.learning = a_def[7][2]

        # Initialize internal variables.
        self.initialize_state()

        Agent.num_agents += 1

    def initialize_state(self):
        # Initialize current_state, current_energy_delta and chosen_action.
        self.steps = 0
        self.current_state = None
        self.current_energy_delta = 0
        self.chosen_action = ai.VOID_ACTION
        self.chosen_action_success = True
        self.learn_result = None

    def pre_step(self):
        # Reset agents' step variables before a step is run.
        self.current_energy_delta = 0

    def update_energy(self, delta):
        # Handle 'energy' updates, including 'recycling' cases.
        # Updates 'aspect' if needed.

        # ENERGY
        if self.recycling == EVERLASTING:
            # No change to agent's energy despite the delta.
            self.current_energy_delta = 0
            energy_used = delta
        else:
            # Keep within 0 and agent's max_energy.
            prev_energy = self.energy
            self.energy = max(min(self.energy + delta, self.max_energy), 0)
            energy_used = self.energy - prev_energy
            self.current_energy_delta += energy_used

            # ASPECT: Check for death condition:
            if self.energy <= 0:
                # Update aspect (RESPAWNEABLE condition handled by world).
                self.color, self.intensity = ui.DEAD_AGENT_COLOR

        return energy_used

    def choose_action(self, world):
        # First, update agent's interpretation of the world (its current_state).
        self.current_state = self.perception(agent=self, world=world)
        # Now its "acting mind" is requested to choose an action.
        self.chosen_action = self.action(self.current_state)

        return self.chosen_action

    def update_after_action(self, success):
        # Update internal state of agent after trying some action.

        # Update internal variables, aspect, etc.
        self.chosen_action_success = success
        # TODO: Update aspect (character(s) displayed, color...)?

        # Update policy (learning). TODO: Consider moving this to a post_step() method.
        self.learn_result = self.learning(
            self.current_state,
            self.chosen_action,
            self.current_energy_delta)

        # Now the 'step' is totally finished.
        self.steps += 1

    def post_step(self):
        # Actions on agent after a step is run.
        pass

    def respawn(self):
        # Restablish an agent back to its optimal state.
        self.energy = self.max_energy
        self.color = self.original_color
        self.intensity = self.original_intensity
        # Initialize internal variables.
        self.initialize_state()
