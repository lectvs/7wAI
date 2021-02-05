from routines.ai_local_game_routine import run_ai_local_game_routine
from ai.scott_ai import ScottAi
from game.known_game import *
from game.ai_game import *
from game.deck import *
from game.wonders import *
import time
import sys
import json
import os.path
from random import shuffle, choice

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

ais = [ScottAi(), ScottAi(), ScottAi()]
num_deck_sets_to_use = 50
num_games_per_run = 50
all_wonders = get_all_wonders()

player_count = len(ais)
wonders = []
deck_sets = []

if len(sys.argv) == 1:
    print("Usage: python local_ai_trainer.py cmd")
    print("where cmd is one of the following:")
    print(f"  train - uses the {COEF_TRAIN_FILE} file to start training")
    print(f"  show_training_results - shows the progress of the training")
    exit(0)


def run_command():
    cmd = sys.argv[1]
    if cmd == 'promote_coefs':
        promote_coefs()
    elif cmd == 'mutate':
        run_mutate()
    elif cmd == 'show_training_results':
        show_training_results()
    elif cmd == 'show_coefficients':
        show_coefficients()
    elif cmd == 'train':
        run_training()


def create_wonders_and_hands():
    global wonders, deck_sets
    wonders.clear()

    for i in range(0, player_count):
        wonders.append(all_wonders[i])

    # rotate to train next set
    all_wonders.append(all_wonders.pop(0))
    # to train a specific wonder:
    # wonders = [EPHESOS_DAY(), OLYMPIA_NIGHT(), RHODOS_DAY()])
    #     GIZA_DAY, GIZA_NIGHT, EPHESOS_DAY, EPHESOS_NIGHT,RHODOS_DAY, RHODOS_NIGHT, ALEXANDRIA_DAY, ALEXANDRIA_NIGHT
    #     OLYMPIA_DAY, OLYMPIA_NIGHT, BABYLON_DAY, BABYLON_NIGHT, HALIKARNASSOS_DAY, HALIKARNASSOS_NIGHT
    wonders[0] = BABYLON_NIGHT()

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


def promote_coefs():
    ai = ais[0]
    if not os.path.isfile(COEF_TRAIN_FILE):
        print(CRED + f"{COEF_TRAIN_FILE} does not exist!" + CEND)
    else:
        with open(COEF_TRAIN_FILE) as json_file:
            coefficients = json.load(json_file)
            for i, (board_name, v) in enumerate(coefficients.items()):
                coefficients[board_name]["player_4"] = coefficients[board_name]["player_5"].copy()
        with open(COEF_TRAIN_FILE, "w") as outfile:
            json.dump(coefficients, outfile)

def run_mutate():
    ai = ais[0]
    if os.path.isfile(COEF_TRAIN_FILE):
        ai.read_coefficients(COEF_TRAIN_FILE)
    elif os.path.isfile(COEF_BASE_FILE):
        ai.read_coefficients(COEF_BASE_FILE)

    parent = ai.copy_coefficients()
    new_coefs = ai.mutate_coefficients("Giza_Day", 4)
    ai.show_mutations("Giza_Day", 4, parent, new_coefs)
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

    # print(f"{run_index} pts: {points}, finish: {finish_place}")

    if run_stats:
        run_stats.run_count += 1
        run_stats.finish_sum += finish_place
        run_stats.points_sum += points
        if finish_place == 1:
            run_stats.victories += 1


def perform_run():
    rs = RunStats()
    for run_index in range(0, num_games_per_run):
        run_game(run_index, rs)
        time.sleep(0.2)  # keep from overheating

    return rs


# we assume run_counts are the same so we don't have to do all the averaging math
def was_run_better(rs, last_rs):
    if rs.victories > last_rs.victories:
        return True
    elif rs.victories == last_rs.victories:
        if rs.finish_sum < last_rs.finish_sum:
            return True
        elif rs.finish_sum == last_rs.finish_sum:
            if rs.points_sum > last_rs.points_sum:
                return True

    return False


def show_training_results():
    ai = ais[0]
    baseline = ai.copy_coefficients()
    if os.path.isfile(COEF_TRAIN_FILE):
        ai.read_coefficients(COEF_TRAIN_FILE)
    elif os.path.isfile(COEF_BASE_FILE):
        ai.read_coefficients(COEF_BASE_FILE)

    nowline = ai.copy_coefficients()

    # ai.show_all_mutations(baseline, nowline)
    ai.show_all_mutation_generations(nowline)


def extract_coef_values(board, key):
    vals = []
    for pc in range(3,6):
        pc_vals = []
        for age in range(0,3):
            val = board[f"player_{pc}"][age][key]
            if key == 'generation':
                pc_vals.append(f"{val}".ljust(5))
            elif val < 0:
                pc_vals.append("{:.2f}".format(val))
            else:
                pc_vals.append("{:.3f}".format(val))
        vals.append(pc_vals)
    return vals


def show_coefficients():
    ai = ais[0]
    if os.path.isfile(COEF_TRAIN_FILE):
        ai.read_coefficients(COEF_TRAIN_FILE)
    elif os.path.isfile(COEF_BASE_FILE):
        ai.read_coefficients(COEF_BASE_FILE)

    nowline = ai.copy_coefficients()
    def_values = nowline["#default"]
    coef_keys = [k for i, (k, v) in enumerate(def_values["player_3"][0].items())]

    # path looks like #default.player_3[age_no].science_w
    for i, (board_name, v) in enumerate(nowline.items()):
        if board_name != '#default':
            board_coefs = nowline[board_name]
            print(f"\n\n{board_name} coefficients")
            print(f"                                3 players            4 players            5+ players   ")
            print(f"                             age1  age2  age3     age1  age2  age3     age1  age2  age3")

            for key in coef_keys:
                all_coefs = extract_coef_values(board_coefs, key)
                all_p3_coefs = all_coefs[0]
                all_p4_coefs = all_coefs[1]
                all_p5_coefs = all_coefs[2]
                line = f"    {key.ljust(24)} {' '.join(all_p3_coefs)}    {' '.join(all_p4_coefs)}    {' '.join(all_p5_coefs)}"
                print(line)


def run_training():
    while True:
        run_training_on_board()


def run_training_on_board():
    if os.path.isfile(COEF_BASE_FILE):
        print(f"Loading {COEF_BASE_FILE} as starting generation")
        for ai_init in ais:
            ai_init.read_coefficients(COEF_BASE_FILE)
    if os.path.isfile(COEF_TRAIN_FILE):
        print(f"Loading {COEF_TRAIN_FILE} as training generation")
        ais[0].read_coefficients(COEF_TRAIN_FILE)

    last_run_stats = None
    last_run_coefficients = None
    mutations_to_try = []

    create_wonders_and_hands()
    board_name = f"{wonders[0].name}_{wonders[0].side}"

    print(f"Training {player_count} players on ({','.join([f'{m.name}_{m.side}' for m in wonders])})")
    iteration = 0

    # outer loop picks new cards and new wonders to keep it fresh
    while iteration < 50:
        rs = perform_run()

        if not last_run_stats:
            last_run_stats = rs
            last_run_coefficients = ais[0].copy_coefficients()
            mutations_to_try.append(ais[0].mutate_coefficients(board_name, player_count))
            mutations_to_try.append(ais[0].mutate_coefficients_huge(board_name, player_count))
            print(f"[{time.strftime('%H:%M:%S')}-{iteration}] Baseline set, rs({rs})")
        elif was_run_better(rs, last_run_stats):
            last_run_stats = rs
            last_run_coefficients = ais[0].copy_coefficients()
            ais[0].write_coefficients(COEF_TRAIN_FILE)
            print(f"[{time.strftime('%H:%M:%S')}-{iteration}] New alpha found, rs({rs})")
            mutations_to_try.append(ais[0].mutate_coefficients(board_name, player_count))  # random mutation
            mutations_to_try.append(ais[0].mutate_coefficients_huge(board_name, player_count))  # random mutation
            mutations_to_try.append(ais[0].remutate_coefficients(board_name, player_count, last_run_coefficients))  # mutate similar to original mutation
            mutations_to_try.append(last_run_coefficients)  # give the original a second shot as well
        else:
            print(f"[{time.strftime('%H:%M:%S')}-{iteration}] still looking, rs({rs}), lrs({last_run_stats})")

        if len(mutations_to_try) == 0:
            mutations_to_try.append(ais[0].mutate_coefficients(board_name, player_count))
            mutations_to_try.append(ais[0].mutate_coefficients_huge(board_name, player_count))

        new_coefs = mutations_to_try.pop(0)
        ais[0].restore_coefficients(new_coefs)

        iteration += 1
        time.sleep(2)  # keep from overheating


run_command()
