from routines.ai_local_game_routine import run_ai_local_game_routine
from game.deck import *
from game.wonders import *
from ai.random_ai import RandomAi
from ai.scott_ai import ScottAi

# Runs a local game where AIs make all the decisions.
# Steps:
# - 1. Adjust ais, wonders, and starting_hands below to your liking.
# - 2. Run `python local_game.py`
# - 3. Press enter to go to the next move.

ais = [RandomAi(), RandomAi(), ScottAi(show_selections=True, verbose=True)]
wonders = [RHODOS_NIGHT(), HALIKARNASSOS_DAY(), BABYLON_NIGHT()]

starting_hands = {
    1: [
        [LUMBER_YARD, ORE_VEIN, TIMBER_YARD, GLASSWORKS, PRESS, ALTAR, MARKETPLACE],
        [CLAY_POOL, CLAY_PIT, EAST_TRADING_POST, WEST_TRADING_POST, STOCKADE, BARRACKS, APOTHECARY],
        [STONE_PIT, LOOM, BATHS, THEATER, GUARD_TOWER, WORKSHOP, SCRIPTORIM]
    ],
    2: [
        [BRICKYARD, FORUM, VINEYARD, AQUEDUCT, DISPENSARY, LIBRARY, SCHOOL],
        [SAWMILL, LOOM, GLASSWORKS, STATUE, CARAVANSERY, WALLS, LABORATORY],
        [FOUNDRY, QUARRY, PRESS, TEMPLE, COURTHOUSE, STABLES, ARCHERY_RANGE]
    ],
    3: [
        [WORKERS_GUILD, SHIPOWNERS_GUILD, LIGHTHOUSE, ARENA, TOWN_HALL, ACADEMY, STUDY],
        [CRAFTSMENS_GUILD, GARDENS, PALACE, FORTIFICATIONS, SIEGE_WORKSHOP, LODGE, UNIVERSITY],
        [PHILOSOPHERS_GUILD, MAGISTRATES_GUILD, SENATE, PANTHEON, HAVEN, ARSENAL, OBSERVATORY]
    ]
}

run_ai_local_game_routine(ais, wonders, starting_hands, verbose=True, pause_each_move=True)
