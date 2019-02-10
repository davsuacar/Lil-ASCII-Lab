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
    "color":        True,   # True for colors, False for B&G. TBA: Check if necessary??
    "spacing":      1,      # Number of 'spc' chars to concatenate at the right of every tile
    "extend_block": False,  # Whether blocks must be replicated to avoid interstices
}

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
        self.width = self.world.width * (1 + self.spc_len) # 

        # Resize?
        if self.resize_term: self.resize_terminal(self.height, self.width)
        
        # Initialize curses settings
        self.stdscr.nodelay(False)   # Enable waiting for user input stop

        # Create curses windows (extending width 1 extra character for safe addstr()...)
        self.header = curses.newwin(1, self.width + 1, 0, 0)
        self.board = curses.newwin(self.world.height, self.width + 1, 1, 0)
        self.footer = curses.newwin(1, self.width + 1, self.world.height + 1, 0)

    def resize_terminal(self, rows, columns):
        # Xterm Control Sequences through “CSI” (“Control Sequence Introducer”)
        # Resize terminal
        os.system("printf '\e[8;{};{}t'".format(rows, columns))

    def say(self, text):
        # Display a certain text at the footer
        text = text[:self.world.width - 1]   # Truncate excess of text
        self.footer.clear()
        self.footer.addnstr(0, 0, text, self.footer.getmaxyx()[1] - 1)
        #getmaxyx
        self.footer.refresh()
        _ = self.stdscr.getkey()

    def ask(self, question):
        # Ask user for input on footer zone
        self.footer.clear()
        self.footer.addnstr(0, 0, question, self.footer.getmaxyx()[1] - 1)
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
        fill = " " * max(0, ((1+self.spc_len) * self.world.width - len(title) - len(time) - self.spc_len))
        text = title + fill + time
        self.header.addnstr(0, 0, text, self.header.getmaxyx()[1] - 1)
        self.header.noutrefresh()

        # BOARD: Update world representation
        for y in range(self.world.height -1, -1, -1):
            line =""
            for x in range(self.world.width):
                thing = self.world.things[x, y]
                if thing == None:
                    # Empty tile here
                    tile = self.world.ground[x, y]
                    line += tile.aspect + self.spc_str
                else:
                    # Some Agent/Block here
                    if (thing in self.world.blocks and self.extend_block):
                        t_aspect = thing.aspect * (1 + self.spc_len) # Blocks may be doubled
                    else:
                        t_aspect = thing.aspect + self.spc_str        # an Agent
                    line += t_aspect

            self.board.addnstr(self.world.height - y - 1, 0, line, self.board.getmaxyx()[1] - 1)
        self.board.noutrefresh()

        # FOOTER: N/A for now
        text = "(footer placeholder)"
        self.footer.addnstr(0, 0, text, self.footer.getmaxyx()[1] - 1)
        self.footer.noutrefresh()

        # Refresh screen
        curses.doupdate()
