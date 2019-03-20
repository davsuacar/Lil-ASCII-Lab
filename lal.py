###############################################################
# Lil' ASCII Lab
# Main world simulation loop

###############################################################
# IMPORT

# libraries
from curses import wrapper
import time
import argparse

# modules
import world as w
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
        end_loop = world.is_end_loop()  # Check max #steps
        if not end_loop:
            # Check user if required
            if (world.time_to_ask()):
                user_input = u_i.ask("Continue? (y/n) ")
                end_loop = (user_input.lower() != "y")
            # Evolve world by one time-fixed step
            if not end_loop:
                t_start = time.time()
                world.step()
                t_end = time.time()
                time.sleep(world.spf - (t_end - t_start))

    # Exit program
    _ = u_i.ask("Bye! (Press to exit)")

if __name__ == '__main__':
    # Main program
    print("Lil' ASCII Lab")
    print("{:<20}{}".format("- Started:", time.ctime()))

    # Create the world and start "wrapped" environment.
    world = w.World(w.Simulation_def)
    wrapper(main_loop, world)

    # Quit program
    print("{:<20}{}".format("- Steps run:", world.steps))
    print("{:<20}{}".format("- Random seed used:", world.random_seed))
