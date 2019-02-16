# Libraries
import numpy as np
import curses
from curses import wrapper
import signal, os

# Modules
import textcolors as colors

# Output settings:
# Define how I/O will happen
IO_def = {
    "resize_term":  False,  # Flag to resize the actual terminal where program runs
    "spacing":      1,      # Number of 'spc' chars to concatenate at the right of every tile
    "extend_block": False,  # Whether blocks must be replicated to avoid interstices
    "min_width":    20,     # Minimum width for the text interface, regardless of board size
    "max_size":     100,    # Maximum size for width of height for the world
}
# initc=\E]4;%p1%d;rgb\:%p2%{255}%*%{1000}%/%2.2X/%p3%{255}%*%{1000}%/%2.2X/%p4%{255}%*%{1000}%/%2.2X\E\\,

# Constants based on curses' 8 basic colors
BLACK   = curses.COLOR_BLACK
BLUE    = curses.COLOR_BLUE
CYAN    = curses.COLOR_CYAN
GREEN   = curses.COLOR_GREEN
MAGENTA = curses.COLOR_MAGENTA
RED     = curses.COLOR_RED
WHITE   = curses.COLOR_WHITE
YELLOW  = curses.COLOR_YELLOW

NORMAL  = 0                 # No offset for normal colors (1..8)
BRIGHT  = 8                 # Offset to get brighter colors assuming COLORS >= 16

MAX_COLORS = 16             # The number of predefined colors to try to use

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

        color_pairs = np.full((MAX_COLORS, MAX_COLORS + 1), 0)
        if has_colors:
            pair = 1 # Skip pair 0 ("wired" to white on black)
            # Terminal has colors: initialize pairs for curses
            for fg in range(MAX_COLORS):         # colors ranging from 0 to 7
                for bg in range(-1, MAX_COLORS):    # colors ranging from -1 to 7
                    if curses.COLORS >= 16:
                        # Full allocation of all 16x16 pair combinations
                        curses.init_pair(pair, fg, bg)
                        color_pairs[fg, bg] = pair
                        pair += 1
                    else:
                        # Restrict to 8x8 pair combinations within the 16x16 shape.
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
        self.footer.addnstr(0, 0, text, self.footer.getmaxyx()[1] - 1, pair)
        self.footer.refresh()

    def ask(self, question):
        # Ask user for input on footer zone
        self.footer.clear()
        pair = self.pair(BLACK, WHITE)
        #self.footer.addstr(0, 0, " "*self.width, pair)
        self.footer.addnstr(0, 0, question.ljust(self.width), self.footer.getmaxyx()[1] - 1, pair)
        self.footer.refresh()
        answer = self.footer.getkey()
        return answer

    def draw(self):
        # Generate and display a full refresh of the world state using curses lib

        # Clear screen first
        self.stdscr.clear()

        # HEADER: Title on top
        title = " " + self.world.name + " "
        time = " " + str(self.world.ticks) + " "
        fill = " " * max(0, self.width - len(title) - len(time))
        
        text = title + fill
        pair = self.pair(WHITE, BLUE + BRIGHT)
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
                    self.board.addstr(self.world.height - y - 1, x_screen, text, pair)
                else:
                    # Some AGENT/BLOCK here
                    if thing in self.world.blocks:                       
                        pair = self.pair(thing.color + thing.intensity, thing.color + thing.intensity)
                        t_aspect = thing.aspect * (1 + self.spc_len) # Blocks may be doubled
                    else:
                        pair = self.pair(thing.color + thing.intensity, self.world.bg_color + self.world.bg_intensity)
                        t_aspect = thing.aspect + self.spc_str       # An Agent
                    self.board.addstr(self.world.height - y - 1, x_screen, t_aspect, pair | curses.A_BOLD)
                x_screen += 1 + self.spc_len
        self.board.noutrefresh()

        # FOOTER: N/A for now
        self.say("(placeholder)")

        # Refresh screen
        curses.doupdate()

# MAIN: code for testing purposes only

def main(scr):
    """
    init_color(color_number, r, g, b)
    """
    curses.use_default_colors() # Set default values for colors (including transparency color number -1).
    scr.clear()

    curses.init_pair(1, WHITE, BLACK)

    scr.addstr(0, 0, "Testing ncurses, pair 1: ", 1)
    scr.addstr(1, 0, "COLORS: " + str(curses.COLORS) + ", PAIRS: " + str(curses.COLOR_PAIRS), 1)
    scr.addstr(2, 0, "can_change_color(): " + str(curses.can_change_color()), 1)

    r, g, b = curses.color_content(BLACK + BRIGHT)
    scr.addstr(3, 0, "{} BLACK = {}, {}, {}".format(BLACK, r, g, b), 1)
    r, g, b = curses.color_content(WHITE + BRIGHT)
    scr.addstr(4, 0, "{} WHITE = {}, {}, {}".format(WHITE, r, g, b), 1)
    r, g, b = curses.color_content(BLUE + BRIGHT)
    scr.addstr(5, 0, "{} BLUE = {}, {}, {}".format(BLUE, r, g, b), 1)
    r, g, b = curses.color_content(CYAN + BRIGHT)
    scr.addstr(6, 0, "{} CYAN = {}, {}, {}".format(CYAN, r, g, b), 1)
    r, g, b = curses.color_content(GREEN + BRIGHT)
    scr.addstr(7, 0, "{} GREEN = {}, {}, {}".format(GREEN, r, g, b), 1)
    r, g, b = curses.color_content(MAGENTA + BRIGHT)
    scr.addstr(8, 0, "{} MAGENTA = {}, {}, {}".format(MAGENTA, r, g, b), 1)
    r, g, b = curses.color_content(RED + BRIGHT)
    scr.addstr(9, 0, "{} RED = {}, {}, {}".format(RED, r, g, b), 1)
    r, g, b = curses.color_content(YELLOW + BRIGHT)
    scr.addstr(10, 0, "{} YELLOW = {}, {}, {}".format(YELLOW, r, g, b), 1)

    scr.refresh()
    _ = scr.getkey()


if __name__ == '__main__':
    # Call main module
    print("Tests with ncurses...")
    wrapper(main)

