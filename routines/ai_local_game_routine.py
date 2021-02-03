from game.base import *
from game.known_game import *
from game.ai_game import *
from game.deck import *
from game.wonders import *

# Helper to print/pause the routine.
def print_pause(game, pause_each_move):
    print()
    print(game)
    if pause_each_move:
        input()
    else:
        print()

# Runs a full local game using the input AIs and starting hands. Optional parameter to pause on each move.
def run_ai_local_game_routine(ais, wonders, starting_hands, silent=False, verbose=True, pause_each_move=False):
    game = KnownGame(wonders, verbose)
    ai_games = [AiGame(i) for i in range(len(ais))]

    for age in [1, 2, 3]:
        game.initialize_age(age, starting_hands[age])
        for i in range(len(ais)):
            ai_games[i].initialize(age, game.wonders, game.hands[i])

        while game.age_initialized:
            if verbose: print_pause(game, pause_each_move)
            move = [ais[i].get_selection(ai_games[i], ai_games[i].get_ai_hand()) for i in range(len(ais))]
            game.execute_turn(move)
            
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
                ai_games[i].post_move(game.wonders, move, game.hands[i])

    if not silent:
        print()
        print('Final situation:')
        print()
        print(game)
        print()

    return game
