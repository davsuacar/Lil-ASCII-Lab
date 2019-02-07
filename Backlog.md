# Backlog

## Front to integrate ncurses:

Detach draw() from class World -> different library?
Define methods for:

* Initialize screen
* Restore screen
* Encapsulate current "draw" method within a generic one

## AI

Implement dynamics of basic attributes: energy.
Implement dynamics of basic attributes: inventory.
Implement basic logic:

* Input = Status + Reward, from the World.
* Policy = hardcoded behaviours (random, herbivores, predators...)
* Actions = Move, Eat, No-action.

## Interface

HI:
Add messaging system at screen bottom.
Add tracking of 1 specific agent (energy, AI, etc.)
Integrate Unicode characters? (e.g. for blocks).

LO:
Implement basic animation for "aspect" (2 or 3 looping chars).
Implement window system with:

* Continuous refresh.
* Resize at start to world size.
* Clean at end.
