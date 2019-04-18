###############################################################
# AI
# for "Lil' ASCII Lab" and its entities...

###############################################################

import numpy as np
from numpy import unravel_index
import random
from collections import namedtuple

###############################################################
# CONSTANTS

# Names of actions:
NONE = "NONE"
MOVE = "MOVE"
EAT = "EAT"

# (x, y) deltas for all 8 possible adjacent tiles (excluding (0,0)).
XY_8_DELTAS = np.array(
    ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
)
XY_8_DELTAS_list = XY_8_DELTAS.tolist()  # Aux. list for "in" operations.
# XY_8_ICONS = ("◣", "◀", "◤", "▼", "▲", "◢", "▶", "◥")
XY_8_ICONS = ("↙", "←", "↖", "↓", "↑", "↘", "→", "↗")

OFF_BOARD = -1000  # Value signalling an "illegal" out-of-the-board tile.

# Action_def: definitions of possible actions.
# An action consists of:
# - a verb (e.g. MOVE, EAT).
# - some action-dependent arguments, expressed between brackets.

Action_def = namedtuple("Action_def", "arguments radius energy_ratio")

ACTIONS_DEF = dict(
    # PASSIVE action.
    NONE=Action_def(
        np.array([]),  # arguments: Not required.
        0,  # radius: local.
        0.0  # energy_ratio: 0x -> No energy consumption.
    ),
    # MOVING to adjacent relative coordinates.
    MOVE=Action_def(
        XY_8_DELTAS,  # arguments: ([x, y] delta) for a given [x0, y0].
        1,  # radius: 1 tile.
        1.0  # energy_ratio: 1x -> Unmodified ratio for 1-tile moves.
    ),

    # EATING energy from adjacent relative coordinates.
    EAT=Action_def(
        XY_8_DELTAS,  # arguments: ([x, y] delta) for a given [x0, y0].
        1,  # radius: 1 tile.
        0.0  # energy_ratio: 0x -> No energy consumption.
    ),
)

VOID_ACTION = [NONE, ACTIONS_DEF[NONE].arguments, ACTIONS_DEF[NONE].energy_ratio]

NO_PERCEPTION = None
NO_ACTION = None
NO_LEARNING = None


###############################################################
# Minds: Auxiliary functions
#
# Used by Perception and Action functions.

def obtain_possible_moves(world, position, moves_delta_list):
    '''
    :param world:
    :param position:
    :param moves_delta_list:
    :return: Return a list with the deltas from 'moves_delta_list' which if applied to given 'position', would land on an emptly tile in 'world'.
    '''

    possible_moves = [delta for delta in moves_delta_list
                      if world.tile_is_empty(position + delta)]
    return possible_moves


def obtain_possible_bites(world, position, moves_delta_list):
    '''
    :param world:
    :param position:
    :param moves_delta_list:
    :return: Return a list with the deltas from 'moves_delta_list' which, if biting to given 'position', would bite some agent in 'world'.
    '''

    possible_bites = [delta for delta in moves_delta_list
                      if world.tile_with_agent(position + delta)]
    return possible_bites


def get_energy_submap(world, position, radius=1):
    # Return:
    # energy_submap: a subset of the world's energy_map centered around
    # 'position' with the given radius.
    # submap_origin: the coordinates of bottome_left position of energy_submap.
    # map_origin: a tuple with the origin of 'energy_submap'.
    # Note: Central 'position' is signalled OFF_BOARD.

    x0, y0 = position

    # Obtain 'legal' subrectangle [world_x0, world_x1] x [world_y0, world_y1].
    submap_x0 = max(0, x0 - radius)
    submap_x1 = min(x0 + radius, world.width - 1)
    submap_y0 = max(0, y0 - radius)
    submap_y1 = min(y0 + radius, world.height - 1)
    # Get 'submap_origin'
    submap_origin = [submap_x0, submap_y0]

    # Copy subrectangle on energy_submap.
    energy_submap = np.copy(world.energy_map[submap_x0:submap_x1+1, submap_y0:submap_y1+1])

    # Mark central position as OFF_BOARD.
    x0_submap = x0 - submap_x0
    y0_submap = y0 - submap_y0
    energy_submap[x0_submap, y0_submap] = OFF_BOARD

    return energy_submap, submap_origin


def obtain_best_bite(world, position, radius=1):
    # Return a tuple with the move taking to the tile with highest energy
    # within some given 'radius' around 'position'.

    # Obtain submap around postion ant tuple with its origin.
    energy_submap, submap_origin = get_energy_submap(world, position, radius)

    # Obtain tuple with relative postion of highest value in submap.
    biggest = unravel_index(
        energy_submap.argmax(),
        energy_submap.shape)

    if energy_submap[biggest[0], biggest[1]] > 0:
        # Generate tuple leading to highest value.
        best_bite_delta = np.array([
            submap_origin[0] + biggest[0] - position[0],
            submap_origin[1] + biggest[1] - position[1]
        ])

    else:
        # Handle void result.
        best_bite_delta = None

    return best_bite_delta


###############################################################
# Minds: Perception
#
# A 'perception' function extracts from the world and the agent itself
# all the information an agent will need to make decisions based on its
# 'action' function.
#
# - Input:
#       - agent, the agent itself, for introspection of its state.
#       - world, the environment in which the agent is.
#
# - Output:
#       - state,  information in the shape the agent will be able to process.
#         NOTE: This implies that "perception"'s output state must match
#         "action"'s input state.


def no_info(agent, world=None):
    # Void perception function, the agent receives no information about world
    # or itself. This is useful for passive agents not actually doing anything,
    # e.g. some object or piece of food.

    return None


def full_info(agent, world=None):
    # Full perception and access to agent and world is granted.
    # This is useful to program 'hard-coded' AIs which directly access
    # all current available information.
    state = (agent, world)  # A tuple with both references.

    return state


###############################################################
# Minds: Action
#
# An 'action' function ('policy' in RL) selects an action at each step
# for the agent.
#
# - Input:
#       - agent, the agent itself, for introspection of its state
#       - world [used to query about empty tiles, etc.]. TODO: Eliminate need for 'world' arg.
#       - state, the current state of the agent.
#
# - Output: the action chosen, as a list:
#       - action_type, e.g. MOVE, FEED, NONE.
#       - action_arguments, e.g. [-1, 1], [].
#       - action_energy_ratio, the cost invested in the action,
#         as a multiplier of agent.move_cost, e.g. 1.0, 0.0, 4.0.

def passive(state=None):
    # Void action function, the agent does not interact with the world.
    # This is useful for passive agents not actually doing anything,
    # e.g. some object or piece of food.

    return ai.VOID_ACTION


def wanderer(state):
    # A hard-coded AI modelling these basic behaviours:
    # - Some inertia for time-consistent movements or eating actions.
    # - Capability to start moves on clear directions, though it can stumble on
    #   other objects later (out of inertia).
    # - Capability to eat from adjacent objects at times.

    agent, world = state  # Extract both complete objects from tuple.

    inertia_prob = 0.66  # Probability of repeating latest action.
    stopping_prob = 0.1  # Probability of stopping vs. doing something.
    biting_prob = 0.5  # Probability of biting an adjacent agent vs. moving.

    if random.uniform(0, 1) <= inertia_prob and agent.chosen_action_success:
        # REPEAT latest action.
        action = agent.chosen_action
    else:
        if random.uniform(0, 1) <= stopping_prob:
            # NONE: Stop for a while.
            action = VOID_ACTION
        else:
            # EAT: Check for close agents.
            possible_bites = obtain_possible_bites(world, agent.position, ACTIONS_DEF[EAT].arguments)
            if random.uniform(0, 1) <= biting_prob and len(possible_bites) > 0:
                # Choose a random bite.
                xy_delta = possible_bites[random.randint(0, len(possible_bites) - 1)]
                action = [EAT, xy_delta, ACTIONS_DEF[EAT].energy_ratio]
            else:
                # MOVE: Choose a random legal move.
                possible_moves = obtain_possible_moves(world, agent.position, ACTIONS_DEF[MOVE].arguments)
                if len(possible_moves) == 0:
                    action = VOID_ACTION
                else:
                    xy_delta = possible_moves[random.randint(0, len(possible_moves) - 1)]
                    action = [MOVE, xy_delta, ACTIONS_DEF[MOVE].energy_ratio]

    return action


def wanderer2(state):
    # A hard-coded AI modelling these basic behaviours:
    # - If hungry, try  best bite (highest energy) around.
    # - Otherwise, act as a regular 'wanderer'.

    agent, world = state  # Extract both complete objects.

    hunger_threshold = 0.5  # Energy ratio below which eating is prioritary.

    # Default action is to rest.
    action = VOID_ACTION

    # Check for hunger first.
    if agent.energy / agent.max_energy < hunger_threshold:
        # Hungry: try best bite.
        best_bite_delta = obtain_best_bite(world, agent.position, ACTIONS_DEF[EAT].radius)
        if best_bite_delta is not None:
            action = [EAT, best_bite_delta, ACTIONS_DEF[EAT].energy_ratio]

    if action == VOID_ACTION:
        action = wanderer(state)

    return action

###############################################################
# Minds: Learning
#
# A 'learning' function updates the policy of the agent
# after trying some action based on:
#
# - Input:
#       - (S_t): state interpretation, stored in self.current_state
#       - (A_t): action taken, stored in self.chosen_action
#       - (r_t): immediate reward, stored in self.current_energy_delta
#
# - Output:
#       - result: some quantification of the learning performed,
#         (bound to the learning algorithm).


def no_learning(state, action, reward):
    # Void learning function; the agent doesn't perform any modification
    # of its policy.
    # This is useful for 'hard-coded' non-Machine-Learning AIs.

    return None
