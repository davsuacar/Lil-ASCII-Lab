# Backlog

## Interface

HI:
Add tracking window (on the right/bottom?) (Use lib: matplotlib, pyqtgraph?).
Add tracking of 1 specific agent (energy, AI, etc.)

LO:
Handle world sizes not fitting on terminal.
Handle resize terminal without exiting.
Implement basic agent animation in "aspect" (2 or 3 looping chars).
Implement graphic orientation signalling on agents to show orientation (e.g. a blinking arrow [▲ ▶ ▼ ◀] on one adyacent tile).
Configurable BG color for the window (now it's all black)?

## AI

HI:
Implement a basic random AI (e.g. random moves / still with RND inertia).
Implement dynamics of basic attributes: energy (initialization, consumption, death).
Implement dynamics of basic attributes: inventory.

LO:
Implement basic logic:

* Input = Status + Reward, from the World.
* Policy = hardcoded behaviours (random, herbivores, predators...).
* Actions = Move, Eat, No-action.

## World Dynamics

TO BE DEFINED
Action Space(s): discrete / continuous
Timing: Sim-turned vs. turn-based.
State: Complete / incomplete information for agents.


## Overall features

HI:
-

LO:
Restrict maximum size of the world.
Extract all world & character config. to external yaml files.
Add logging (using standard 'logging' module).
Add arguments to main program (module argparse).



# Features
ncurses terminal support for b&w, 8 or 16 colors.
Implement synchronized steps, e.g. 12 fps, 24 fps.
Reproducibility: manage random seed at start (generate, store).

