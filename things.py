###############################################################
# Agents
# for "Lil' ASCII Lab" and its entities...

###############################################################

import ai
import ui

# Constants
RANDOM_POSITION = (None, None)

NON_RECHARGEABLE = None
RECHARGEABLE = 'Rechargeable'  # TODO: Implement agent 2 agent energy donation.
EVERLASTING = 'Everlasting'
RESPAWNABLE = 'Respawnable'

# Tiles definition:
# Type of tile, aspect, color, intensity, position (not specified here).
TILE_DEF = (
    ("ground", "·", ui.BLUE, ui.NORMAL, RANDOM_POSITION)
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
    (60, "block", "▢", ui.BLUE, ui.BRIGHT, RANDOM_POSITION),
)

# Agent definition:
#   Number of instances to place (e.g. 10).
#   Name, some descriptive text (e.g. "bug").
#   Aspect: one single Unicode character (e.g. "⚉").
#   Color & intensity:  (see ui.py module).
#   Initial position (or RND). If more than one instance, it will be ignored.
#
#   Energy-related settings:
#       Initial energy assigned at start.
#       Maximum energy the agent can acquire.
#       Bite power, amount of energy the agent can take with one bite.
#       Step_cost, i.e. energy consumed on each world step regardless of action chosen.
#       Move_cost, i.e. energy consumed for moving to an adjacent tile.
#
#   Recycling settings:
#       'None':         regular loss; useless after death.
#       'Rechargeable': regular loss; can be recharged after 'death'.
#       'Everlasting':  NO loss regardless of energy taken.
#           
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

AGENTS_DEF = (
    # Real minds:
    (10, "bug", "⚉", ui.GREEN, ui.BRIGHT, RANDOM_POSITION,
     (100, 110, 5, -0.1, -0.1), NON_RECHARGEABLE,
     (ai.full_info, ai.wanderer, ai.no_learning)),

    (4, "Omi", "Ω", ui.CYAN, ui.BRIGHT, RANDOM_POSITION,
     (100, 110, 5, -0.1, -0.5), RESPAWNABLE,
     (ai.full_info, ai.wanderer, ai.no_learning)),

    (3, "killer", "Ѫ", ui.RED, ui.BRIGHT, RANDOM_POSITION,
     (100, 110, 100, -0.1, -1), NON_RECHARGEABLE,
     (ai.full_info, ai.wanderer, ai.no_learning)),

    (4, "foe", "Д", ui.MAGENTA, ui.BRIGHT, RANDOM_POSITION,
     (100, 110, 10, -0.1, -1), RESPAWNABLE,
     (ai.full_info, ai.wanderer, ai.no_learning)),

    # Mindless:
    (5, "energy", "♥", ui.RED, ui.NORMAL, RANDOM_POSITION,
     (50, 50, 0, -0.001, 0), RESPAWNABLE,
     (None, None, None)),

    (1, "recharger", "*", ui.YELLOW, ui.BRIGHT, RANDOM_POSITION,
     (30, 30, 0, 0, 0), EVERLASTING,
     (None, None, None)),
)


###############################################################
# CLASSES
# Thing --- Tile
#        |- Block
#        |- Agent

class Thing:
    # Root class containing the common attributes for all classes.
    def __init__(self, name, aspect, color, intensity, position):
        self.name = name  # Name of the thing.
        self.aspect = aspect  # Text character to display.
        self.color = color  # Color for the character.
        self.intensity = intensity  # Intensity to apply.
        self.position = position  # Its position in the world.


class Tile(Thing):
    pass


class Block(Thing):
    num_blocks = 0

    # It passively occupies one tile, never moving.
    def __init__(self, name, aspect, color, intensity, position):
        # Initialize inherited attributes.
        super().__init__(name, aspect, color, intensity, position)
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

    def update_energy(self, delta):
        # Handle 'energy' updates, including 'recycling' cases.
        # Updates 'aspect' if needed.

        if self.recycling == EVERLASTING:
            # No change to agent's energy despite the delta.
            self.current_energy_delta = 0
            energy_used = delta
        else:
            # Keep within 0 and agent's max_energy.
            prev_energy = self.energy
            self.energy = max(min(self.energy + delta, self.max_energy), 0)
            self.current_energy_delta = self.energy - prev_energy
            energy_used = self.current_energy_delta

            # Check for death condition:
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

    def update(self, success, action_energy_delta):  # Drop arg. action_energy_delta
        # Update internal state of agent after trying some action.

        # Update internal variables, aspect, etc.
        _ = self.update_energy(action_energy_delta)  # TODO: Move to world's execute_action()
        self.chosen_action_success = success
        # TODO: Update aspect (character(s) displayed, color...)?

        # Update policy (learning).
        self.learn_result = self.learning(
            self.current_state,
            self.chosen_action,
            self.current_energy_delta)

        # Now the 'step' is totally finished.
        self.steps += 1

    def respawn(self):
        # Restablish an agent back to its optimal state.
        self.energy = self.max_energy
        self.color = self.original_color
        self.intensity = self.original_intensity
        # Initialize internal variables.
        self.initialize_state()
