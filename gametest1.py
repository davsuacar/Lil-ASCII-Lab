###############################################################
# IMPORT

# libraries
import numpy as np
from curses import wrapper
import time

# modules
import world2 as w
import ui

###############################################################
# MAIN PROGRAM

def main_loop(stdscr, world):
    # Initialize UI
    u_i = ui.UI(stdscr, world)

    # Main world loop
    end_loop = False
    while not end_loop:
        # Display the world as it is now
        u_i.draw()

        # Check conditions to go on
        end_loop = world.is_end_loop()  # Check max #ticks
        if not end_loop:
            # Check user if required
            if (world.time_to_ask()):
                user_input = u_i.ask("Continue? (y/n) ")
                end_loop = (user_input.lower() != "y")
            # Evolve world by one regular tick
            t_start = time.time()
            world.tick()
            t_end = time.time()
            time.sleep(world.spf - (t_end - t_start))

    # Exit program
    _ = u_i.ask("Bye! (Press to exit)")

if __name__ == '__main__':
    # Main program
    print("Starting Lil' ASCII Lab...")
    
    # Create the world and start "wrapped" environment.
    world = w.World(w.World_def, w.Tile_def, w.Block_def, w.Agents_def)
    wrapper(main_loop, world)