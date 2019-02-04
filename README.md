# *"Lil' ASCII Lab"*

by Alberto H

## About this project

"Lil' ASCII Lab" is a little playground on which single-character beings come to life driven by their AI.
Currently, agents running around will have simple, hard-coded behaviours. The long-term plan is to integrate Machine Learning-driven agents in.

## World rules

This is a tiled, rectangular world, consisting of:

* tiles
* blocks
* agents

A **'tile'** is just that, an empty place on which a block or agent can stand.

A **'block'** is the most basic entity: it just **passively** occupies one tile, never moving and preventing agents from moving on it.

An **'agent'** is a "living" entity. It can occupy a single tile, and perform specific actions on the world or other agents (but not on blocks). By doing this, it receives **immediate rewards** from the world.

A **'world'** is the setting on which a little universe takes life. This is how it works:

* time flows as a **loop of *synchronous* 'ticks' for all agents**.
* at **tick start**, all agents get their status updated (including possible rewards).
* **'during' the tick**, each agent decides the action(s) to perform, as a request to the world (e.g. a move).
* at **tick end**, the world resolves the consequences of all requested actions (actually execute the move, or bounce against block).
* now a new tick can start, so all status are updated, and so on...

This loops goes on till some final condition is reached or the maximal number of ticks has been executed, after which the world exits.

## Main loop pseudocode

(start)
initialize world with empty tiles and put blocks in
initialize agents and put them on the world

while (not finished)
    draw the world
    check conditions to go on
    tick start
        update status + rewards for agents
        request actions from agents (and user?)
        resolve results of actions from agents (and from user?)
        update the world (ticks only?)
    tick end

draw final state of the world
(end)

## World definition

* *name* of the world (e.g. "GridWorld").
* *width* in tiles (e.g. 30).
* *height* in tiles (e.g. 20).
* *empty_tile*, for empty tiles with no agents of blocks on (e.g. ".").
* *block_tile*, the aspect of the blocks in this world (e.g. "*").
* *n_blocks_rnd*, max. % of variation in # of blocks (e.g. 0.4).
* *max_ticks*, how long to run the world ('None' for infinite loop).
* *chk_ticks*, how often to ask user for quit/go-on ('None' = never ask).

## Agent definition

### Common to ALL agents

* Number of agents to put at world start (e.g. 2).
* Name describing the type of agent (e.g. "robot").
* Aspect for the agent as a single-character (e.g. "𝝮").
* Color settings for the agent.
* Initial position for each.

## Agent-specific: "Omi"

* Life (when 0, dead comes!)
* Reward (accumulated)
