from routines.ai_local_game_routine import run_ai_local_game_routine
from ai.scott_ai import ScottAi
from game.known_game import *
from game.ai_game import *
from game.deck import *
from game.wonders import *
import time
import sys
import os.path
from random import shuffle, sample

COEF_BASE_FILE = "coef_base.json"
COEF_TRAIN_FILE = "coef_train.json"

# time.strftime("%H:%M:%S")
DeckSet = namedtuple('DeckSet', ['deck1', 'deck2', 'deck3'])


class RunStats:
    def __init__(self):
        self.run_count = 0
        self.victories = 0
        self.finish_sum = 0
        self.points_sum = 0

    def __str__(self):
        avg_f = self.finish_sum / self.run_count if self.run_count > 0 else 0
        avg_p = self.points_sum / self.run_count if self.run_count > 0 else 0
        return f"r: {self.run_count}, v: {self.victories}, pts: {'{:.2f}'.format(avg_p)}, finish: {'{:.2f}'.format(avg_f)}"


CRED = '\033[91m'
CEND = '\033[0m'

ais = [ScottAi(), ScottAi(), ScottAi(), ScottAi(), ScottAi()]
num_deck_sets_to_use = 50
num_games_per_run = 10

player_count = len(ais)
wonders = []
deck_sets = []

if len(sys.argv) == 1:
    print("Usage: python local_ai_trainer.py cmd")
    print("where cmd is one of the following:")
    print(f"  make_base_coef - makes the {COEF_BASE_FILE} file with starting coefficients")
    exit(0)

def prepare_for_run():
    global wonders, deck_sets
    wonders = get_random_wonders(player_count)
    deck_sets = []
    for i in range(num_deck_sets_to_use):
        deck1 = get_cards_for_players_age(player_count, 1)
        deck2 = get_cards_for_players_age(player_count, 2)
        deck3 = get_cards_for_players_age(player_count, 3)
        guilds, deck3 = deck3[:10], deck3[10:]
        shuffle(guilds)
        deck3 = guilds[:player_count + 2] + deck3

        shuffle(deck1)
        shuffle(deck2)
        shuffle(deck3)
        deck_sets.append(DeckSet(deck1, deck2, deck3))


def build_starting_hands(run_index):
    deck_index = run_index % num_deck_sets_to_use
    deck_set = deck_sets[run_index % num_deck_sets_to_use]

    return {
        1: [deck_set.deck1[7 * i:7 * (i + 1)] for i in range(player_count)],
        2: [deck_set.deck2[7 * i:7 * (i + 1)] for i in range(player_count)],
        3: [deck_set.deck3[7 * i:7 * (i + 1)] for i in range(player_count)],
    }


def run_command():
    cmd = sys.argv[1]
    if cmd == 'make_base_coef':
        make_base_coef_file()
    elif cmd == 'mutate':
        run_mutate()
    elif cmd == 'train':
        run_training()


def make_base_coef_file():
    if os.path.isfile(COEF_BASE_FILE):
        print(CRED + f"{COEF_BASE_FILE} already exists!" + CEND)
    else:
        ai = ScottAi()
        ai.write_coefficients(COEF_BASE_FILE)
        print(f"{COEF_BASE_FILE} written")

def run_mutate():
    ai = ais[0]
    if os.path.isfile(COEF_TRAIN_FILE):
        ai.read_coefficients(COEF_TRAIN_FILE)
    elif os.path.isfile(COEF_BASE_FILE):
        ai.read_coefficients(COEF_BASE_FILE)

    parent = ai.copy_coefficients()
    ai.mutate_coefficients("Giza_Day", 4)
    ai.show_mutations("Giza_Day", 4, parent)
    # ai.remutate_coefficients("Giza_Day", 4, parent)


def run_game(run_index, run_stats):
    starting_hands = build_starting_hands(run_index)

    for w in wonders:
        w.reset()

    game = run_ai_local_game_routine(ais, wonders, starting_hands, silent=True, verbose=False, pause_each_move=False)
    wonder = game.wonders[0]
    points = wonder.compute_points_total(game.wonders)
    finish_place = 1
    for w in game.wonders:
        comp = w.compute_points_total(game.wonders)
        if comp > points:
            finish_place += 1

    print(f"{run_index} pts: {points}, finish: {finish_place}")

    if run_stats:
        run_stats.run_count += 1
        run_stats.finish_sum += finish_place
        run_stats.points_sum += points
        if finish_place == 1:
            run_stats.victories += 1


def run_training():
    if os.path.isfile(COEF_BASE_FILE):
        print(f"Loading {COEF_BASE_FILE} as starting generation")
        for ai_init in ais:
            ai_init.read_coefficients(COEF_BASE_FILE)
    if os.path.isfile(COEF_TRAIN_FILE):
        print(f"Loading {COEF_TRAIN_FILE} as training generation")
        ais[0].read_coefficients(COEF_TRAIN_FILE)

    # outer loop picks new cards and new wonders to keep it fresh
    while True:
        prepare_for_run()
        rs = RunStats()
        start = time.perf_counter()
        for run_index in range(0, num_games_per_run):
            run_game(run_index, rs)
            time.sleep(0.0005)  # keep from overheating

    print(rs)
    print(time.perf_counter() - start, " time")





run_command()
