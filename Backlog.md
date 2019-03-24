# Backlog

## AI

HI:

* ...

LO:

* Implement dynamics of basic attributes: inventory.
* Implement basic logic:
  * Input = Status + Reward, from the World.
  * Policy = hardcoded behaviours (random, herbivores, predators...).
  * Actions = Move, Eat, No-action.

Perception (inputs):

* Senses: Visual limitation (full world, subsection around agent, opacity of blocks...).
* Other senses: (environment conditions, e.g. smell, lightness, rain, temperature...).
* Messages from other agents.

## UI - User Interface

HI:

* ...

LO:

* Tracker (aesthetics): Review tracker's layout (split sub-areas?).
* Add tracking feature: World.highlighted_agents. ALL: make agents more visible with highlighted BG?, TRACKED: only the tracked one; None: Current implementation.
* Add color to logo at program exit.
* Implement basic agent animation in "aspect" (2 or 3 looping chars).
* Handle resize terminal without exiting.
* Detect when resizing the terminal would exceed screen dimensions.
* Implement graphic orientation signalling on agents to show orientation (e.g. a blinking arrow [▲ ▶ ▼ ◀] on one adyacent tile).
* Tracking: Maintain agents' heatmaps (where they've been around).

## World Dynamics

HI:

* Implement advanced energy dynamics: a) fixed resources granting INSTANT recharge; b) mobile resources that: b.1) can be picked, carried and dropped; b.2) can be consumed, granting DELAYED recharge.
* Consider agents' ability (yes/no) to "resurrect" if granted new energy.
* Decouple UI / AI refresh rates, e.g. one AI step every 5 UI steps.

LO:

* Improve world generation with patterns of blocks.
* Consider creating "hole" blocks, causing instant death.

TO BE DEFINED:

* Action Space(s): discrete / continuous [DONE]
* Timing: Sim-turned (not turn-based). [DONE]
* State: Complete / incomplete information for agents. [DONE]

## Overall features

HI:

* Allow Pause, Stop, Play, FF (at different speeds: x1, x2, ...).
* In Fast-Forward mode, consider skipping frames drawing?

LO:

* Extract strings with program name, version, etc ("Lil' ASCII Lab"...). from code.
* Restrict maximum size of the world.
* Extract all world & character config. to external yaml files.
* Add logging (using standard 'logging' module).
* Add arguments to main program (module argparse).


# Available Features (add to README.md)

AI:

* Implement a basic random AI (e.g. random moves / still, with RND inertia).
* Implement "EAT" action.

World dynamics:

* Implement dynamics of basic attributes: energy (initialization, consumption, death).
* Define dynamics at death. Once energy is 0, AI is no longer active.
* Implement synchronized steps, e.g. 12 fps, 24 fps.
* Reproducibility: manage random seed at start (generate, store).
* Allow Fast-Forward execution (off-clock).

UI:

* Tracker: Show current world speed (at fps, full-speed).
* Tracker: Tab selects only living agents with some mind.
* Tracker: Show agents with minds only (not mindless "resources").
* Add key controls:
  * Left / right key to control simulation speed.
  * Up key for full speed.
  * Space to pause simulation.
  * Tab to change tracked_agent.
* Tracker: Show AI identifiers = Mind + Senses.
* Tracker: Highlight tracked agent on the right (with "▶")
* Tracker: Differentiate agents' names.
* Tracker/World: Energy deltas displayed as number with red/green color.
* Tracker: Signal failed "FEED" actions.
* Tracker/World: Signal agent's about to die (blinking?).
* World: Differentiate tracked agent with surrounding highlights.
* World: Highlight when energy's won with a better BG, e.g. agent's color NORMAL.
* World: Change dead agents' color to grey, and no longer blinking on screen.
* Add ncurses terminal support for b&w, 8 or 16 colors.
* Handle sizes not fitting on terminal:
* Overall UI:
  * excessive board width
  * excessive board height
  * insufficient space for board + tracker

Add "Lil' ASCI Lab" logo to tracker.

Check Board for:

* Long world names
* Long "LIVE/PAUSED" strings?
* Long ask()/say() arguments

Check Tracker for:

* Long main character name
* Long number of steps
* long placeholder
