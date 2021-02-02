from ai.random_ai import RandomAi
from ai.scott_ai import ScottAi
from game.known_game import *
from game.ai_game import *
from game.deck import *
from game.wonders import *
import os

if os.name == 'nt':
    import msvcrt
    def getch():
        ch = msvcrt.getch().decode()
        if ch == '\x03':
            raise KeyboardInterrupt
        return ch

else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if ch == '\x03':
            raise KeyboardInterrupt
        return ch

# Runs a local game where AIs make all the decisions.
# Steps:
# - 1. Adjust ais, wonders, and starting_hands below to your liking.
# - 2. Run `python debug_local_ai.py`
# - 3. Press enter to go to the next move.

ais = [RandomAi(), RandomAi(), ScottAi()]
debug_stops = [2]  # one or more indexes in the above array
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


# Helper to print/pause the routine.
def print_pause(game, pause_each_move):
    print()
    print(game)
    if pause_each_move:
        input()
    else:
        print()


# Runs a full local game using the input AIs and starting hands. Optional parameter to pause on each move.
verbose = True
pause_each_move = True
game = KnownGame(wonders, True)
ai_games = [AiGame(i) for i in range(len(ais))]

for stop in debug_stops:
    ai_games[stop].debuggingMode = 'terse'

for age in [1, 2, 3]:
    game.initialize_age(age, starting_hands[age])
    for i in range(len(ais)):
        ai_games[i].initialize(age, game.wonders, game.hands[i])

    while game.age_initialized:
        moves = []

        print('\n--> Round Start')
        for i in range(len(ais)):
            ai = ais[i]
            aig = ai_games[i]
            wonder = aig.get_ai_wonder()
            ai_move = ai.get_selection(aig, aig.get_ai_hand())
            if not aig.debuggingMode == '':
                while True:
                    print(f"[{wonder.name}_{wonder.side}] wants to play: {ai_move}\n\ng) go\ny) Show reasoning")
                    ch = getch()
                    if ch == 'y':
                        aig.debuggingMode = 'verbose'
                        ai_move = ai.get_selection(aig, aig.get_ai_hand())
                        aig.debuggingMode = 'terse'
                    elif ch == 'q':
                        raise KeyboardInterrupt
                    else:
                        break
            else:
                print(f"{wonder.name}_{wonder.side} wants to play: {ai_move}")

            moves.append(ai_move)

        print('--> Decisions made\n')
        game.execute_turn(moves)

        if game.wait_for_last_card_play:
            if verbose: print_pause(game, pause_each_move)
            for i in range(len(wonders)):
                ai_games[i].pre_last_card_play(wonders, game.hands[i])
            for i in range(len(wonders)):
                if not wonders[i].has_effect('play_last_card'):
                    continue
                selection = ais[i].get_selection(ai_games[i], ai_games[i].get_ai_hand())
                game.execute_last_card_turn(selection)
                break

        if game.wait_for_discard_play:
            if verbose: print_pause(game, pause_each_move)
            for i in range(len(wonders)):
                if not wonders[i].has_effect('build_from_discard'):
                    continue
                card = ais[i].get_build_card_from_discard(ai_games[i], game.discard_pile)
                game.execute_discard_turn(card)
                break

        for i in range(len(ais)):
            ai_games[i].post_move(game.wonders, moves, game.hands[i])

print()
print('Final situation:')
print()
print(game)
print()


