from routines.ai_local_game_routine import run_ai_local_game_routine
from game.deck import *
from game.wonders import *
from ai.random_ai import RandomAi
from ai.first_ai import FirstAi
from random import shuffle, sample

ais = [FirstAi(), FirstAi(), FirstAi(), FirstAi(), FirstAi(), FirstAi(), FirstAi()]
PLAYERS = len(ais)

best_game = None

for _ in range(50):
    wonders = get_random_wonders(PLAYERS)

    deck1 = get_cards_for_players_age(PLAYERS, 1)
    deck2 = get_cards_for_players_age(PLAYERS, 2)
    deck3 = get_cards_for_players_age(PLAYERS, 3)
    guilds, deck3 = deck3[:10], deck3[10:]
    shuffle(guilds)
    deck3 = guilds[:PLAYERS+2] + deck3

    shuffle(deck1)
    shuffle(deck2)
    shuffle(deck3)

    starting_hands = {
        1: [deck1[7*i:7*(i+1)] for i in range(PLAYERS)],
        2: [deck2[7*i:7*(i+1)] for i in range(PLAYERS)],
        3: [deck3[7*i:7*(i+1)] for i in range(PLAYERS)],
    }

    game = run_ai_local_game_routine(ais, wonders, starting_hands, pause_each_move=False)

    if not best_game or game.get_total_score() > best_game.get_total_score():
        best_game = game

    print("Best game:")
    print(best_game)