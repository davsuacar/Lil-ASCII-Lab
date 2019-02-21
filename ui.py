###############################################################
# User Interface
# for "Lil' ASCII Lab"

###############################################################
# IMPORT

# Libraries
import numpy as np
import random
import curses
from curses import wrapper
import signal, os

# Modules
# (none)

###############################################################
#   SETTINGS

# Constants based on curses' 8 basic colors
BLACK   = curses.COLOR_BLACK
BLUE    = curses.COLOR_BLUE
CYAN    = curses.COLOR_CYAN
GREEN   = curses.COLOR_GREEN
MAGENTA = curses.COLOR_MAGENTA
RED     = curses.COLOR_RED
WHITE   = curses.COLOR_WHITE
YELLOW  = curses.COLOR_YELLOW

colors = (BLACK, BLUE, CYAN, GREEN, MAGENTA, RED, WHITE, YELLOW)
color_names = ("BLACK", "BLUE", "CYAN", "GREEN", "MAGENTA", "RED", "WHITE", "YELLOW")

NORMAL  = 0                 # No offset for normal colors (1..8)
BRIGHT  = 8                 # Offset to get brighter colors, assuming COLORS >= 16
MAX_COLORS = 16             # The number of predefined colors to try to use

# Output settings:
# Define how I/O will happen
IO_def = {
    "resize_term":  False,  # Flag to resize the actual terminal where program runs
    "spacing":      1,      # Number of 'spc' chars to concatenate at the right of every tile (for an even vert/horiz aspect ratio)
    "extend_block": False,  # Whether blocks must be replicated to avoid interstices (TBA: is this needed?)
    "min_width":    20,     # Minimum width for the text interface, regardless of board size
    "max_size":     100,    # Maximum size for width of height for the world
}

###############################################################
# CLASSES

class UI:
    def __init__(self, stdscr, world):
        # Register curses screen and world to represent. Initialize attributes.
        self.stdscr = stdscr
        self.world = world

        # Check IO settings
        self.resize_term = IO_def["resize_term"]
        self.spc_len = IO_def["spacing"] # Multiplier for tiles spacing
        self.spc_str = " " * self.spc_len     # doubling columns for esthetic reasons
        self.extend_block = IO_def["extend_block"]

        # Layout dimensions
        self.height = 1 + self.world.height + 1   # header + board + footer
        self.width = max(IO_def["min_width"], self.world.width * (1 + self.spc_len)) # Adapt to settings, with a minimum width

        # Resize?
        if self.resize_term: self.resize_terminal(self.height, self.width)
        
        # Initialize curses settings
        self.stdscr.nodelay(False)  # Enable waiting for user input stop
        curses.curs_set(2)          # Set cursor as 'very' visible

        # COLORS: check availability and initialize curses' pairs
        self.has_colors, self.color_pairs = self.init_all_pairs()

        # Create curses windows (extending width by N extra characters for safe addstr()...)
        N = 1 # number of extra characters on the right
        self.header = curses.newwin(1,                  self.width + N, 0, 0)
        self.board = curses.newwin(self.world.height,   self.width + N, 1, 0)
        self.footer = curses.newwin(1,                  self.width + N, self.world.height + 1, 0)
        self.footer.keypad(True) # footer will handle keyboard input, so enabling cursor keys or navigation keys

        # Fill in the background of all windows with black
        pair = self.pair(BLACK, BLACK)

        stdscr.bkgd(" ", pair)
        self.header.bkgd(" ", pair)
        self.board.bkgd(" ", pair)
        self.footer.bkgd(" ", pair)

        stdscr.refresh()

    def init_all_pairs(self):
        curses.use_default_colors() # Set default values for colors (including transparency color number -1).
        has_colors = curses.has_colors()    # Boolean: whether the terminal can display colors

        color_pairs = np.full((MAX_COLORS, MAX_COLORS), 0)
        if has_colors:
            pair = 1 # Skip pair 0 ("wired" to black and white)
            # Terminal has colors: initialize pairs for curses
            for fg in range(MAX_COLORS):         # colors ranging from 0 to 15
                for bg in range(MAX_COLORS):    # colors ranging from 0 to 15
                    if curses.COLORS >= 16:
                        # Full allocation of all 16x16 pair combinations
                        curses.init_pair(pair, fg, bg)
                        color_pairs[fg, bg] = pair
                        pair += 1
                    else:
                        # Restrict to 8x8 pair combinations within the 16x16 shape
                        if (fg <= 8 and bg <= 8):
                            # Allocate new basic pair
                            curses.init_pair(pair, fg, bg)
                            color_pairs[fg, bg] = pair
                            pair += 1
                        else:
                            # Reuse lower preallocated pairs
                            color_pairs[fg, bg] = color_pairs[max(fg, fg - 8), max(bg, bg - 8)]                    

        else:
            # Terminal has NO colors: leave ALL pairs as 0 (curses' default pair for fg/bg)
            pass

        return has_colors, color_pairs

    def pair(self, fg, bg):
        return curses.color_pair(self.color_pairs[fg, bg])

    def resize_terminal(self, rows, columns):
        # Xterm Control Sequences through “CSI” (“Control Sequence Introducer”)
        # Resize terminal
        os.system("printf '\e[8;{};{}t'".format(rows, columns))
    
    def say(self, text):
        # Print some text on footer area
        self.footer.clear()
        pair = self.pair(BLACK, WHITE)
        self.footer.addnstr(0, 0, text.ljust(self.width - 1), self.footer.getmaxyx()[1] - 1, pair)
        self.footer.refresh()

    def ask(self, question):
        # Ask user for input on footer zone
        curses.flushinp() # Throw away any typeahead not yet processed.
        self.footer.clear() # Clear footer window
        pair = self.pair(BLACK, WHITE)
        self.footer.addnstr(0, 0, question.ljust(self.width - 1), self.footer.getmaxyx()[1] - 1, pair)
        self.footer.refresh()
        answer = self.footer.getkey()
        return answer

    def draw(self):
        # Generate and display a full refresh of the world state using curses lib

        # Clear screen first
        self.stdscr.clear()

        # HEADER: Title on top
        title = " " + self.world.name + " "
        time = " " + str(self.world.steps) + " "
        fill = " " * max(0, self.width - len(title) - len(time))
        
        text = title + fill
        pair = self.pair(WHITE, BLUE + NORMAL)
        self.header.addnstr(0, 0, text, self.width - len(time), pair | curses.A_BOLD)
        pair = self.pair(WHITE, RED + BRIGHT)
        self.header.addstr(time, pair | curses.A_NORMAL)
        self.header.noutrefresh()

        # BOARD: Update world representation
        for y in range(self.world.height -1, -1, -1):
            x_screen = 0
            for x in range(self.world.width):
                thing = self.world.things[x, y]
                if thing == None:
                    # Emtpy TILE here
                    tile = self.world.ground[x, y]
                    text = tile.aspect + self.spc_str
                    pair = self.pair(tile.color + tile.intensity, self.world.bg_color + self.world.bg_intensity)
                    self.board.addstr(self.world.height - y - 1, x_screen, text, pair | curses.A_NORMAL)
                else:
                    # Some AGENT/BLOCK here
                    if thing in self.world.blocks:
                        # A BLOCK
                        if thing.aspect == " ": # Generic full block style
                            pair = self.pair(thing.color + thing.intensity, thing.color + thing.intensity)
                            t_aspect = " " * (1 + self.spc_len) # Blocks may be doubled
                        else:                   # Specific block style
                            pair = self.pair(thing.color + thing.intensity, self.world.bg_color + self.world.bg_intensity)
                            if len(thing.aspect) == 1:
                                t_aspect = thing.aspect * (1 + self.spc_len) # Blocks may be doubled
                            else:
                                t_aspect = thing.aspect[:self.spc_len + 1] # Use only the first characters
                    else:
                        # An AGENT
                        pair = self.pair(thing.color + thing.intensity, self.world.bg_color + self.world.bg_intensity)
                        t_aspect = thing.aspect + self.spc_str
                    # Display the agent/block
                    self.board.addstr(self.world.height - y - 1, x_screen, t_aspect, pair | curses.A_BOLD)
                x_screen += 1 + self.spc_len # X must follow specific spacing
        self.board.noutrefresh()

        # FOOTER: N/A for now
        self.say("(running...)")

        # Refresh screen
        curses.doupdate()

###############################################################
# MAIN PROGRAM: code for TESTING purposes only

def main(scr):
    scr.scrollok(True)  # Not really working, so limiting tests to terminal's height.

    # Call as main module generates a series of tests on the terminal.
    if not curses.has_colors():
        # Print basic b&w message
        scr.clear()
        scr.addstr(0,0, "This is a B&W terminal. Press to exit...", 0)
        scr.refresh()
        _ = scr.getkey()
    else:
        # Go for the colors
        curses.use_default_colors()     # Set default values for colors (including transparency color number -1).
        c_colors = curses.COLORS        # The full capacity
        n_colors = min(16, c_colors)    # Demo is limited to 16 colors
        color_pairs = np.full((n_colors, n_colors), 0)

        # Loop over possible pairs
        scr.clear()

        # Start reporting
        scr.addstr(0, 0, "This terminal can use {} colors. See some combinations:".format(c_colors), 0)

        pair = 1
        n_pairs = 0
        for fg in range(n_colors): # Loop over FG colors
            for bg in range(n_colors): # Loop over BG colors
                if c_colors >= 16:
                    curses.init_pair(pair, fg, bg)
                    color_pairs[fg, bg] = pair
                    pair += 1
                else:
                    if fg <= 8 and bg <= 8:
                        curses.init_pair(pair, fg, bg)
                        color_pairs[fg, bg] = pair
                        pair += 1
                    else:
                        color_pairs[fg, bg] = color_pair[max(fg, fg - 8), max(bg, bg - 8)]
                n_pairs += 1

        # Demo out some combinations
        max_y, _ = scr.getmaxyx()
        for y in range(1, max_y -1):
            pair = random.randint(1, n_pairs)
            scr.addstr(y, 0, "  Random fg&bg colors  ", curses.color_pair(pair))
            y += 1
        
        # Final message
        scr.addstr(y, 0, "Press to exit...", 0)
        scr.refresh()
        _ = scr.getkey()

if __name__ == '__main__':
    # Call as main module generates a series of tests on the terminal.
    print("ui.py is a module of Lil' ASCII Lab.")
    _ = input("Press to test some ncurses colors...")
    wrapper(main)
