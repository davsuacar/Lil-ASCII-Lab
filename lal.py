###############################################################
# Lil' ASCII Lab
# Main world simulation loop.

###############################################################

from curses import wrapper
import time

import world as w
import ui


def main_loop(stdscr, world):
    '''
    :param stdscr: standard screen created by curses' wrapper.
    :param world: the world on which the simulation will run.
    :return: (nothing).
    '''

    # Initialize UI.
    u_i = ui.UI(stdscr, world)

    # Main world loop.
    end_loop = False
    while not end_loop:
        # Display the world as it is now.
        user_break = u_i.draw()

        # Check conditions to go on.
        end_loop = user_break or world.is_end_loop()
        if not end_loop:
            # Evolve world by one time-fixed step.
            t_start = time.time()
            world.step()
            t_end = time.time()
            time.sleep(world.spf - (t_end - t_start))

    # Exit program.
    _ = u_i.ask("Bye! (Press to exit)")

if __name__ == '__main__':
    # Main program.
    print("Lil' ASCII Lab v0.1")
    print("{:<20}{}".format("- Started:", time.ctime()))

    # Create the world and start "wrapped" environment.
    world = w.World(w.Simulation_def)
    wrapper(main_loop, world)

    # Quit program.
    print("{:<20}{}".format("- Steps run:", world.steps))
    print("{:<20}{}".format("- Random seed used:", world.random_seed))
