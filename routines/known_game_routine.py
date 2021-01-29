from game.base import *
from game.known_game import *
from game.ai_game import *
from game.deck import *
from game.wonders import *

# Runs a full predetermined game locally using the input starting hands and moves. Optional parameter to pause on each move.
# The input AI will provide its opinion on which move to make on each move, but this has no effect on the actual move performed.
def run_known_game_routine(ai, ai_i, wonders, starting_hands, moves, pause_each_move=False):
    game = KnownGame(wonders)
    ai_game = AiGame(ai_i)

    for age in [1, 2, 3]:
        game.initialize_age(age, starting_hands[age])
        ai_game.initialize(age, game.wonders, game.hands[ai_i])

        last_real_move = None
        for move in moves[age]:
            print()
            print(ai_game)
            print()
            wonder = ai_game.get_ai_wonder()
            if not game.wait_for_last_card_play and game.wait_for_discard_play and wonder.name == 'Halikarnassos':
                ai.get_build_card_from_discard(ai_game, game.discard_pile)
            elif game.wait_for_last_card_play and wonder.name == 'Babylon':
                ai.get_selection(ai_game, game.hands[ai_i])
            elif not game.wait_for_discard_play and not game.wait_for_last_card_play:
                ai.get_selection(ai_game, game.hands[ai_i])
            if pause_each_move:
                input()
            else:
                print()
            if type(move) is list:
                game.execute_turn(move)
                last_real_move = move
                if not game.wait_for_last_card_play and not game.wait_for_discard_play:
                    ai_game.post_move(game.wonders, move, game.hands[ai_i])
            elif type(move) is Selection:
                game.execute_last_card_turn(move)
                if not game.wait_for_discard_play:
                    ai_game.post_move(game.wonders, move, game.hands[ai_i])
            elif type(move) is Card:
                game.execute_discard_turn(move)
                ai_game.post_move(game.wonders, last_real_move, game.hands[ai_i])

    print()
    print(ai_game)
    print()
    return game