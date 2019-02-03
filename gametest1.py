###############################################################
# IMPORT

# libraries
import numpy as np

# modules
import world2 as w

###############################################################
# MAIN PROGRAM

if __name__ == '__main__':
    
    # Create the world
    world = w.World(w.World_def, w.Tile_def, w.Block_def, w.Agents_def)
    
    # Game loop
    end_loop = False
    while not end_loop:
        # Display the world as it is now
        world.draw()

        # Check conditions to go on
        end_loop = world.is_end_loop()
        if (not end_loop) and (world.ticks % world.chk_ticks == 0):
            user_input = input("Keep going (y/n)? ")
            end_loop = (user_input != "Y" and user_input != "y")

        if not end_loop:
            # Evolve world by one tick
            world.tick()

    # Exit program
    print ("Bye!")