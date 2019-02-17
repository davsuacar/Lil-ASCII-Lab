# Backlog

## Interface

HI:
Add tracking of 1 specific agent (energy, AI, etc.)

LO:
Handle resize terminal without exiting.
Implement basic agent animation in "aspect" (2 or 3 looping chars).

## AI

HI:
Implement a basic random AI (e.g. random moves / still with RND inertia).
Implement dynamics of basic attributes: energy (initialization, consumption, death).
Implement dynamics of basic attributes: inventory.

LO:
Implement basic logic:

* Input = Status + Reward, from the World.
* Policy = hardcoded behaviours (random, herbivores, predators...)
* Actions = Move, Eat, No-action.

## Overall features

HI:
Implement synchronized steps (ticks), e.g. 12 fps, 24 fps.

LO:
Restrict maximum size of the world.
Extract all world & character config. to external yaml files.
Replicability: manage random seed at start (generate, store).
Add logging (using standard 'logging' module).
Add arguments to main program (module argparse).
Add tracking window (on the right/bottom?) (Use lib: matplotlib, pyqtgraph?)