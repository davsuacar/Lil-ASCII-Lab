# Libraries
import curses
from curses import wrapper
import signal, os

# Modules
import textcolors as colors

# Output settings:
# Define how I/O will happen
IO_def = {
    "resize_term":  False,   # Flag to resize the actual terminal where program runs
    "use_curses":   False,  # Flag to use curses lib or plain text on the terminal
    "color":        True,   # True for colors, False for B&G
    "spacing":      1,      # Number of 'spc' chars to concatenate at the right of every tile
    "extend_block": False,  # Whether blocks must be replicated to avoid interstices
}

def initialize_ui(world, clear = True):
    if IO_def["resize_term"]:
        # Firstly, resize and clean the terminal to fit the world
        height = world.height + 2   # title + screen + message ticker
        width = world.width * 2     # doubling columns for esthetic reasons
        resize_terminal(height, width)

    # If requested, clear screen and scrollback buffer
    if clear: clear_terminal()

def resize_terminal(rows, columns):
    # Xterm Control Sequences through “CSI” (“Control Sequence Introducer”)
    # Resize terminal
    os.system("printf '\e[8;{};{}t'".format(rows, columns))

def clear_terminal():
    if (IO_def["use_curses"]):
        # curses initialization
        print("not implemented.")
        exit(1)
    else:
        # Clear terminal and scrollback buffer
        # Xterm Control Sequences through “CSI” (“Control Sequence Introducer”)
        os.system('clear')
        os.system("printf '\e[3J'")

def draw(world):
    # Check settings first
    spc_len = IO_def["spacing"] # Multiplier for tiles spacing
    spc_str = " " * spc_len
    extend_block = IO_def["extend_block"]

    if (IO_def["use_curses"]):
        # Draw the world using curses lib
        print("not implemented.")
        exit(1)
    else:
        # Draw the world using plain text on terminal

        # Clear screen and scrollback buffer
        clear_terminal()

        # Title on top
        title = " " + world.name + " "
        time = " " + str(world.ticks) + " "
        fill = " " * max(0, ((1+spc_len) * world.width - len(title) - len(time) - spc_len))
        title = colors.colorize_bg(title, 'white', 'normal', 'blue', 'normal', 'no-bold')
        time = colors.colorize_bg(time, 'white', 'normal', 'red')
        fill = colors.colorize_bg(fill, 'white', 'normal', 'blue')
        header = title + fill + time
        print(header)

        # Now the board: loop over rows from top down to bottom
        if IO_def["color"]:
            # COLOR version
            for y in range(world.height - 1, -1, -1):
                line = ""
                for x in range (world.width):
                    thing = world.things[x, y]
                    if thing == None:
                        # Empty tile
                        tile = world.ground[x, y]
                        line += colors.colorize_bg(tile.aspect + spc_str, \
                                tile.color, tile.intensity, world.bg_color, world.bg_intensity)
                    else:
                        # Some Agent/BLock on it. TBA: customize 'bold' as agent's attrib
                        if (thing in world.blocks and extend_block):
                            t_aspect = thing.aspect * (1 + spc_len) # Blocks may be doubled
                        else:
                            t_aspect = thing.aspect + spc_str       # Agents
                        line += colors.colorize_bg(t_aspect, \
                                thing.color, thing.intensity, world.bg_color, world.bg_intensity, 'bold')
                print(line)

        else:
            # MONOCHROME version
            for y in range(world.height - 1, -1, -1):
                line = ""
                for x in range (world.width):
                    thing = world.things[x, y]
                    if thing == None:
                        # Empty tile
                        line += world.ground[x, y].aspect + spc_str
                    else:
                        # Some Agent/Block on it
                        line += thing.aspect + spc_str
                print(line)
