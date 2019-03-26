###############################################################
# AI
# for "Lil' ASCII Lab" and its entities...

###############################################################

import numpy as np
import random

###############################################################
# CONSTANTS

# Names of actions:
NONE = "NONE"
MOVE = "MOVE"
EAT = "EAT"

# (x, y) deltas for all 8 possible adjacent tiles.
XY_X1_DELTAS = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
XY_X1_ICONS = ("◣", "◀", "◤", "▼", "▲", "◢", "▶", "◥")

# Actions definition:
# An action consists of a verb and some arguments, expressed between brackets here.

ACTIONS_DEF = {
    NONE:  # PASSIVE action.
    (  # No arguments.
        [],  # Arguments: Not required.
        0.0  # Energy ratio: 0x -> No energy consumption.
    ),

    MOVE:  # MOVING to adjacent relative coordinates.
    (  # 2 arguments with 8 possible values (excluding (0,0)).
        np.array(  # [x, y] deltas for a given [x0, y0]
            XY_X1_DELTAS
        ),
        1.0  # Energy ratio: 1x -> Unmodified ratio for 1-tile moves.
    ),

    EAT:  # EATING energy from adjacent relative coordinates.
    (  # 2 arguments with 8 possible values (excluding (0,0)).
        np.array(  # [x, y] deltas for a given [x0, y0]
            XY_X1_DELTAS
        ),
        0.0  # Energy ratio: 0x -> No energy consumption.
    ),
}

VOID_ACTION = [NONE, ACTIONS_DEF[NONE][0], ACTIONS_DEF[NONE][1]]

NO_PERCEPTION = None
NO_ACTION = None
NO_LEARNING = None


###############################################################
# Minds: Auxiliary functions
#   Used by Perception and Action functions.

def obtain_possible_moves(world, position, moves_delta_list):
    '''
    :param world:
    :param position:
    :param moves_delta_list:
    :return: Return a list with the deltas from 'moves_delta_list' which if applied to given 'position', would land on an emptly tile in 'world'.
    '''

    possible_moves = [delta for delta in moves_delta_list if world.tile_is_empty(position + delta)]
    return possible_moves


def obtain_possible_bites(world, position, moves_delta_list):
    '''
    :param world:
    :param position:
    :param moves_delta_list:
    :return: Return a list with the deltas from 'moves_delta_list' which, if biting to given 'position', would bite some agent in 'world'.
    '''

    possible_bites = [delta for delta in moves_delta_list if world.tile_with_agent(position + delta)]
    return possible_bites


def best_possible_bite(world, position, moves_delta_list):
    '''
    :param world:
    :param position:
    :param moves_delta_list:
    :return: Return the delta from 'moves_delta_list' corresponding to the agent with higher energy in world. 
    '''

    possible_bites = [delta for delta in moves_delta_list if world.tile_with_agent(position + delta)]
    
    return possible_moves


###############################################################
# Minds: Perception
#

def default_perception(action, world=None):
    '''
    :param world:
    :return: Void Senses function, returning the world passed.
    '''

    return world


###############################################################
# Minds: Action
#
# A function ('policy' in RL) selects an action at each step for the agent.
#
# - Inputs:
#       - agent.
#       - world [used to query about empty tiles, etc.]. TODO: Eliminate need for 'world' arg.
#       - state, the current state of the agent.
#
# - Outputs: the action chosen, as a list:
#       - action_type, e.g. MOVE, FEED, NONE.
#       - action_arguments, e.g. [-1, 1], [].
#       - action_energy_ratio, the cost invested in the action,
#         as a multiplier of agent.move_cost, e.g. 1.0, 0.0, 4.0.


def wanderer(agent, world, state=None):
    '''
    :param agent: passed for agent's introspection of its state.
    :param world: only passed in order to call auxiliary methods.
    :return: It chooses random moves, stopping from time to time. Some parametrizable inertia gives continuity to successful moves.
    '''

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
            possible_bites = obtain_possible_bites(world, agent.position, ACTIONS_DEF[EAT][0])
            if random.uniform(0, 1) <= biting_prob and len(possible_bites) > 0:
                # Choose a random bite.
                xy_delta = possible_bites[random.randint(0, len(possible_bites) - 1)]
                action = [EAT, xy_delta, ACTIONS_DEF[EAT][1]]
            else:
                # MOVE: Choose a random legal move.
                possible_moves = obtain_possible_moves(world, agent.position, ACTIONS_DEF[MOVE][0])
                if len(possible_moves) == 0:
                    action = VOID_ACTION
                else:
                    xy_delta = possible_moves[random.randint(0, len(possible_moves) - 1)]
                    action = [MOVE, xy_delta, ACTIONS_DEF[MOVE][1]]

    return action


def wanderer2(agent, world, state=None):
    '''
    :param agent: passed for agent's introspection of its state.
    :param world: only passed in order to call auxiliary methods.
    :return: It chooses random moves, stopping from time to time. Some parametrizable inertia gives continuity to successful moves.
    '''

    hunger_threshold = 0.6  # Energy ratio below which eating is prioritary.

    # Default action is to rest.
    action = VOID_ACTION

    """
    # Check for hunger first.
    if agent.energy / agent.max_energy < hunger_threshold :
        possible_bites = obtain_possible_bites(world, agent.position, ACTIONS_DEF[EAT][0])
        if len(possible_bites) > 0
    """

    return action
