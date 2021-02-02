from routines.known_game_routine import run_known_game_routine
from game.deck import *
from game.wonders import *
from ai.random_ai import RandomAi
from ai.scott_ai import ScottAi

# Runs a fixed, predetermined game locally.
# GAME: https://boardgamearena.com/gamereview?table=135447213
# Steps:
# - 1. Replace ai with the AI you want. Keep ai_i = 1
# - 2. Run `python fixed_game.py`
# - 3. Press enter to go to the next move.

ai = ScottAi(show_selections=True, verbose=True)
ai_i = 1
wonders = [RHODOS_NIGHT(), ALEXANDRIA_NIGHT(), EPHESOS_NIGHT()]

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

moves = {
    1: [
        [Selection(TIMBER_YARD, 'play', Payment(0, 1, 0)), Selection(CLAY_PIT, 'play', Payment(0, 1, 0)), Selection(STONE_PIT, 'play', None)],
        [Selection(BATHS, 'play', None), Selection(ALTAR, 'play', None), Selection(EAST_TRADING_POST, 'play', None)],
        [Selection(BARRACKS, 'play', None), Selection(WORKSHOP, 'play', None), Selection(MARKETPLACE, 'play', None)],
        [Selection(LUMBER_YARD, 'play', None), Selection(CLAY_POOL, 'play', None), Selection(SCRIPTORIM, 'play', None)],
        [Selection(THEATER, 'play', None), Selection(ORE_VEIN, 'play', None), Selection(STOCKADE, 'play', Payment(0, 0, 1))],
        [Selection(WEST_TRADING_POST, 'play', None), Selection(GUARD_TOWER, 'play', None), Selection(GLASSWORKS, 'wonder', Payment(0, 0, 1))]
    ],
    2: [
        [Selection(FORUM, 'play', None), Selection(CARAVANSERY, 'wonder', None), Selection(FOUNDRY, 'play', Payment(0, 1, 0))],
        [Selection(LABORATORY, 'throw', None), Selection(QUARRY, 'wonder', None), Selection(LIBRARY, 'play', None)],
        [Selection(ARCHERY_RANGE, 'play', None), Selection(SCHOOL, 'play', None), Selection(LOOM, 'play', None)],
        [Selection(AQUEDUCT, 'play', None), Selection(SAWMILL, 'play', Payment(0, 1, 0)), Selection(STABLES, 'play', Payment(2, 0, 1))],
        [Selection(STATUE, 'play', Payment(1, 0, 0)), Selection(TEMPLE, 'play', None), Selection(VINEYARD, 'play', None)],
        [Selection(PRESS, 'play', None), Selection(DISPENSARY, 'play', None), Selection(WALLS, 'wonder', Payment(0, 0, 2))],
    ],
    3: [
        [Selection(TOWN_HALL, 'play', Payment(1, 0, 0)), Selection(PALACE, 'play', Payment(0, 0, 2)), Selection(SENATE, 'play', None)],
        [Selection(ARSENAL, 'play', None), Selection(SHIPOWNERS_GUILD, 'play', None), Selection(FORTIFICATIONS, 'play', Payment(2, 0, 1))],
        [Selection(GARDENS, 'play', None), Selection(MAGISTRATES_GUILD, 'play', Payment(0, 0, 2)), Selection(LIGHTHOUSE, 'play', Payment(1, 0, 0))],
        [Selection(WORKERS_GUILD, 'play', Payment(1, 0, 2)), Selection(CRAFTSMENS_GUILD, 'play', Payment(0, 0, 2)), Selection(PANTHEON, 'play', Payment(5, 0, 0))],
        [Selection(HAVEN, 'play', None), Selection(ARENA, 'play', None), Selection(UNIVERSITY, 'play', None)],
        [Selection(SIEGE_WORKSHOP, 'throw', None), Selection(PHILOSOPHERS_GUILD, 'wonder', Payment(2, 0, 0)), Selection(STUDY, 'wonder', None)],
    ]
}

run_known_game_routine(ai, ai_i, wonders, starting_hands, moves, verbose=True, pause_each_move=True)
