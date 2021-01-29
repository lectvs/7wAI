from routines.known_game_routine import run_known_game_routine
from game.deck import *
from game.wonders import *
from ai.random_ai import RandomAi
from ai.first_ai import FirstAi

# Runs a fixed, predetermined game locally.
# GAME: https://boardgamearena.com/gamereview?table=136822126
# Steps:
# - 1. Replace ai with the AI you want. Keep ai_i = 1
# - 2. Run `python fixed_game.py`
# - 3. Press enter to go to the next move.

ai = RandomAi()
ai_i = 1
wonders = [BABYLON_NIGHT(), HALIKARNASSOS_NIGHT(), EPHESOS_NIGHT()]

starting_hands = {
    1: [
        [ALTAR, MARKETPLACE, EAST_TRADING_POST, WEST_TRADING_POST, STOCKADE, GUARD_TOWER, SCRIPTORIM],
        [CLAY_POOL, ORE_VEIN, TIMBER_YARD, LOOM, BATHS, THEATER, APOTHECARY],
        [LUMBER_YARD, STONE_PIT, CLAY_PIT, GLASSWORKS, PRESS, BARRACKS, WORKSHOP]
    ],
    2: [
        [BRICKYARD, SAWMILL, PRESS, TEMPLE, COURTHOUSE, DISPENSARY, LIBRARY],
        [LOOM, FORUM, CARAVANSERY, VINEYARD, WALLS, STABLES, ARCHERY_RANGE],
        [QUARRY, FOUNDRY, GLASSWORKS, AQUEDUCT, STATUE, LABORATORY, SCHOOL]
    ],
    3: [
        [CRAFTSMENS_GUILD, GARDENS, PALACE, SENATE, OBSERVATORY, STUDY, UNIVERSITY],
        [BUILDERS_GUILD, PANTHEON, TOWN_HALL, LIGHTHOUSE, SIEGE_WORKSHOP, LODGE, ACADEMY],
        [SPIES_GUILD, SHIPOWNERS_GUILD, MAGISTRATES_GUILD, HAVEN, ARENA, ARSENAL, FORTIFICATIONS]
    ]
}

moves = {
    1: [
        [Selection(MARKETPLACE, 'play', None), Selection(TIMBER_YARD, 'play', Payment(0, 1, 0)), Selection(STONE_PIT, 'play', None)],
        [Selection(CLAY_PIT, 'play', Payment(0, 1, 0)), Selection(SCRIPTORIM, 'play', Payment(0, 0, 2)), Selection(BATHS, 'play', None)],
        [Selection(APOTHECARY, 'play', Payment(0, 0, 1)), Selection(WORKSHOP, 'throw', None), Selection(WEST_TRADING_POST, 'play', None)],
        [Selection(STOCKADE, 'play', None), Selection(CLAY_POOL, 'play', None), Selection(LUMBER_YARD, 'play', None)],
        [Selection(BARRACKS, 'play', None), Selection(GUARD_TOWER, 'play', None), Selection(ORE_VEIN, 'wonder', Payment(1, 0, 0))],
        [Selection(LOOM, 'throw', None), Selection(GLASSWORKS, 'play', None), Selection(ALTAR, 'play', None)]
    ],
    2: [
        [Selection(BRICKYARD, 'play', Payment(0, 1, 0)), Selection(CARAVANSERY, 'play', Payment(0, 0, 2)), Selection(AQUEDUCT, 'play', None)],
        [Selection(FORUM, 'play', None), Selection(SCHOOL, 'play', Payment(0, 0, 2)), Selection(DISPENSARY, 'wonder', Payment(1, 0, 0))],
        [Selection(QUARRY, 'play', Payment(0, 1, 0)), Selection(LIBRARY, 'play', None), Selection(VINEYARD, 'play', None)],
        [Selection(TEMPLE, 'play', None), Selection(STABLES, 'play', None), Selection(FOUNDRY, 'play', Payment(0, 1, 0))],
        [Selection(WALLS, 'play', Payment(2, 0, 0)), Selection(LABORATORY, 'play', Payment(0, 0, 2)), Selection(COURTHOUSE, 'wonder', Payment(2, 0, 0))],
        [Selection(STATUE, 'wonder', None), Selection(SAWMILL, 'wonder', None), Selection(ARCHERY_RANGE, 'play', Payment(1, 0, 0))],
        Selection(GLASSWORKS, 'throw', None),
        WORKSHOP
    ],
    3: [
        [Selection(PALACE, 'play', Payment(1, 0, 1)), Selection(ACADEMY, 'play', None), Selection(ARSENAL, 'play', Payment(3, 0, 0))],
        [Selection(FORTIFICATIONS, 'play', None), Selection(UNIVERSITY, 'play', None), Selection(PANTHEON, 'play', None)],
        [Selection(LODGE, 'play', Payment(1, 0, 0)), Selection(SPIES_GUILD, 'play', None), Selection(SENATE, 'play', Payment(1, 0, 0))],
        [Selection(GARDENS, 'play', None), Selection(SIEGE_WORKSHOP, 'play', None), Selection(ARENA, 'play', Payment(1, 0, 0))],
        [Selection(HAVEN, 'play', None), Selection(STUDY, 'play', None), Selection(BUILDERS_GUILD, 'play', Payment(4, 0, 4))],
        [Selection(TOWN_HALL, 'play', None), Selection(SHIPOWNERS_GUILD, 'wonder', Payment(0, 0, 2)), Selection(CRAFTSMENS_GUILD, 'play', Payment(1, 0, 0))],
        Selection(LIGHTHOUSE, 'play', None),
        MAGISTRATES_GUILD
    ]
}

run_known_game_routine(ai, ai_i, wonders, starting_hands, moves, verbose=True, pause_each_move=True)
