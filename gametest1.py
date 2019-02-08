###############################################################
# IMPORT

# libraries
import numpy as np

# modules
import world2 as w
import ui

###############################################################
# MAIN PROGRAM

if __name__ == '__main__':
    
    # Create the world
    world = w.World(w.World_def, w.Tile_def, w.Block_def, w.Agents_def)
    #Initialize UI
    ui.initialize_ui(world)
    
    # Game loop
    end_loop = False
    while not end_loop:
        # Display the world as it is now
        ui.draw(world)

        # Check conditions to go on
        end_loop = world.is_end_loop()  # Max #ticks?
        if not end_loop:
            # Check user if required
            if (world.time_to_ask()):
                user_input = input("Keep going (y/n)? ")
                end_loop = (user_input != "Y" and user_input != "y")
            # Evolve world by one tick
            world.tick()

    # Exit program
    print ("Bye!")