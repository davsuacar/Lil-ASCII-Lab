###############################################################
# AI 
# for "Lil' ASCII Lab" and its entities...

###############################################################
# IMPORT

# libraries
import random

# Modules
# (none)

###############################################################
# Minds: Auxiliary functions
#   Used by Senses and Policies.

###############################################################
# Minds: Senses
#   TBA

###############################################################
# Minds: Policies
#   

def wanderer(agent, world, state = None):
    # Choose a random move the first time or if not driven by inertia.
    # Otherwise, repeat latest action (still in attribure 'chosen_action')
    # NOTE: 'world' is only passed in order to call auxiliary methods.

    inertia_prob = 0.5 # probability of repeating latest action.

    if True or (random.uniform(0,1) > inertia_prob):
        possible_moves = world.get_adjacent_empty_tiles(agent.position[0], agent.position[1])
        if len(possible_moves) == 0:
            action = None
            action_arguments = []
        else:
            action = "MOVE"
            new_tile = possible_moves[random.randint(0, len(possible_moves) - 1)]
            action_arguments = [new_tile[0], new_tile[1]]
    else:
        action =            agent.chosen_action[0]
        action_arguments =  agent.chosen_action[1]

    return(action, action_arguments)
            
