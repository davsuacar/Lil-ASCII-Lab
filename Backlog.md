# Backlog

## Interface

HI:
-

LO:
Implement basic agent animation in "aspect" (2 or 3 looping chars).
Handle resize terminal without exiting.
Detect when resizing the terminal would exceed screen dimensions.
Implement graphic orientation signalling on agents to show orientation (e.g. a blinking arrow [▲ ▶ ▼ ◀] on one adyacent tile).

## AI

HI:
Implement a basic random AI (e.g. random moves / still, with RND inertia).
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
Allow Fast-Forward execution (off-clock).
Allow Pause, Stop, Play, FF (at different speeds: x1, x2, ...).
In Fast-Forward mode, consider skipping frames drawing?

LO:
Restrict maximum size of the world.
Extract all world & character config. to external yaml files.
Add logging (using standard 'logging' module).
Add arguments to main program (module argparse).

# Features
Implement dynamics of basic attributes: energy (initialization, consumption, death).
Add ncurses terminal support for b&w, 8 or 16 colors.
Implement synchronized steps, e.g. 12 fps, 24 fps.
Reproducibility: manage random seed at start (generate, store).

UI:
Handle sizes not fitting on terminal:
Overall UI:
- excessive board width
- excessive board height
- insuficient space for board + tracker

Add "Lil' ASCI Lab" logo to tracker.

Check Board for:
- Long world names
- Long "LIVE/PAUSED" strings?
- Long ask()/say() arguments
Check Tracker for:
- Long main character name
- Long number of steps
- long placeholder
