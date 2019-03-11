###############################################################
# AI 
# for "Lil' ASCII Lab" and its entities...

###############################################################
# IMPORT

# libraries
import numpy as np
import random

# Modules
# (none)

###############################################################
#   SETTINGS

# Actions definition:
# An action consists of a verb and some arguments, expressed between brackets here.

Actions_def = {
    "None":             # Passive action.
    (
        [],             # Arguments: Not required.
        0               # Energy ratio: 0x -> No energy consumption.
    ),

    "MOVE":             # Moving to adjacent relative coordinates.
    (                   # 2 arguments with 8 possible values (excluding (0,0)).
        np.array(       # [x, y] deltas for a given [x0, y0]
            [[-1, -1],[-1, 0],[-1, 1],[0, -1],[0, 1],[1, -1],[1, 0],[1, 1]]
        ),
        1               # Energy ratio: 1x -> Unmodified ratio for 1-tile moves.
    ),
}

No_action = ["None", []]

###############################################################
# Minds: Auxiliary functions
#   Used by Senses and Policies.

def obtain_possible_moves(world, x0, y0, moves_delta_list):
    # Return a list with the deltas from 'moves_delta_list' which,
    # if applied ti [x0, y0], would land on an emptly tile in 'world'.
    possible_moves = [delta for delta in moves_delta_list if world.is_tile_empty([x0, y0] + delta)]
    return possible_moves

###############################################################
# Minds: Senses
#   TODO

###############################################################
# Minds: Policies
#   

def mindless(agent, world, state = None):
    # Void AI, always retuning 'No_action'.
    return(No_action)

def wanderer(agent, world, state = None):
    # It chooses random moves, stopping from time to time.
    # Some parametrizable inertia gives continuity to successful moves.
    # NOTE: 'world' is only passed in order to call auxiliary methods.

    inertia_prob = 0.75 # Probability of repeating latest action.
    stopping_prob = 0.1 # Probability to stop vs. moving around.

    if random.uniform(0,1) <= inertia_prob and agent.chosen_action_success:
        # Repeat latest action.
        action = agent.chosen_action
    else:
        if random.uniform(0,1) <= stopping_prob:
            # Stop for a while.
            action = No_action
        else:
            # Choose a random legal move.
            possible_moves = obtain_possible_moves( \
                world, agent.position[0], agent.position[1], Actions_def["MOVE"][0])

            if len(possible_moves) == 0:
                action = No_action
            else:
                xy_delta = possible_moves[random.randint(0, len(possible_moves) - 1)]
                action = ["MOVE", xy_delta]
    
    return(action)
            
