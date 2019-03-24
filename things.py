###############################################################
# Agents
# for "Lil' ASCII Lab" and its entities...

###############################################################

import ai
import ui

# Tiles definition:
# Type of tile, aspect, color, intensity, position (not specified here).
TILE_DEF = (
    ("tile", "·", ui.BLACK, ui.BRIGHT, [None, None])
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
    #   (None, "block", " ", ui.BLACK, ui.BRIGHT, [None, None]),
    #   (4, "block2", "▛▜", ui.BLUE, ui.NORMAL, [None, None]),
    #   (10, "fence", "#", ui.WHITE, ui.BRIGHT, [None, None]),
    (60, "stone", "▧", ui.BLACK, ui.BRIGHT, [None, None]),
)

# Agent definition:
#   Number of instances to place.
#   Name, some descriptive text.
#   Aspect: one single Unicode character (e.g. "𝝮").
#   Color & intensity:  (see above).
#   Initial position (or RND). If more than one instance, it will be ignored.
#
#   Energy-related settings:
#       Initial energy assigned at start.
#       Maximum energy the agent can acquire.
#       Bite power, amount of energy the agent can take with one bite.
#       Step_cost, i.e. energy consumed per world step regardless of action.
#       Move_cost, i.e. energy consumed for moving to an adjacent tile.
#   Senses:
#       The function translating the environment into input for an agent's mind.
#       If None, ai.default_senses() is assigned.
#   Mind:
#       The cognitive function processing senses to output actions.
#       If None, a NO_ACTION will always be assumed.

AGENTS_DEF = (
    (10, "buggy", "⚉", ui.GREEN, ui.BRIGHT, [None, None],
     (100, 110, 5, -0.1, -0.1), None, ai.wanderer),
    (1, "Omi", "Ω", ui.BLUE, ui.BRIGHT, [None, None],
     (100, 110, 5, -0.1, -0.5), None, ai.wanderer),
    (3, "killer", "Ж", ui.RED, ui.BRIGHT, [None, None],
     (100, 110, 100, -0.1, -1), None, ai.wanderer),
    (3, "foe", "Д", ui.MAGENTA, ui.BRIGHT, [None, None],
     (100, 110, 10, -0.1, -1), None, ai.wanderer),
    (5, "apple", "", ui.RED, ui.NORMAL, [None, None],
     (20, 20, 0, -0.001, 0), None, None),
    (5, "star", "*", ui.YELLOW, ui.BRIGHT, [None, None],
     (30, 30, 0, 0, 0), None, None),
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

        if a_def[6] is None:
            self.senses = ai.default_senses
        else:
            self.senses = a_def[6]
        self.mind = a_def[7]

        self.steps = 0
        # Initialize current_state, current_energy_delta and chosen_action.
        self.current_state = None
        self.current_energy_delta = 0
        self.chosen_action = ai.NO_ACTION
        self.chosen_action_success = True
        Agent.num_agents += 1

    def update_energy(self, delta):
        # Keep within 0 and agent's max_energy.
        prev_energy = self.energy
        self.energy = max(min(self.energy + delta, self.max_energy), 0)
        self.current_energy_delta = self.energy - prev_energy

        # Update aspect.
        if self.energy <= 0:
            # The agent is dead.
            self.color, self.intensity = ui.DEAD_AGENT_COLOR

        return self.current_energy_delta

    def choose_action(self, world):
        # First, update agent's interpretation of the world (its current_state).
        self.current_state = self.interpret_state(world)
        # Now its "mind" is requested to choose an action.
        self.chosen_action = self.run_policy(world, self.current_state)

        return self.chosen_action

    def interpret_state(self, world):
        # Extraction of the information available for the agent.
        # - Based on its 'senses'.
        # - TODO: other inputs (e.g. messages...).

        # Default: Complete information, the whole world is visible.
        if self.senses is None:
            state = world
        else:
            state = self.senses(self, world)

        return state

    def run_policy(self, world, state):
        # Policy function returning the action chosen by the agent based on state.
        # NOTE: 'world' is only passed in order to call auxiliary methods.

        # Default: No action.
        if self.mind is None:
            action = ai.NO_ACTION
        else:
            action = self.mind(self, world, state)

        return action

    def update(self, action, success, action_energy_delta):
        # Update state of agent after trying some action.

        # Update internal variables.
        _ = self.update_energy(action_energy_delta)
        self.chosen_action_success = success

        # TODO: Update aspect (character, color...)?

        # TODO: Update policy (learning) based on:
        #   self.current_state (S_t)
        #   self.chosen_action (A_t)
        #   self.current_energy_delta (r_t)

        # Now the 'step' is totally finished.
        self.steps += 1
