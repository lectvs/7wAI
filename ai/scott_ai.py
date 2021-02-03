from game.wonders import *
from game.base import *
import json
import os
import copy

from random import choice, randint, uniform, shuffle
from collections import namedtuple

ALL_WONDERS = [
    GIZA_DAY, GIZA_NIGHT,
    EPHESOS_DAY, EPHESOS_NIGHT,
    RHODOS_DAY, RHODOS_NIGHT,
    ALEXANDRIA_DAY, ALEXANDRIA_NIGHT,
    OLYMPIA_DAY, OLYMPIA_NIGHT,
    BABYLON_DAY, BABYLON_NIGHT,
    HALIKARNASSOS_DAY, HALIKARNASSOS_NIGHT
]
# Use this as a template to construct your AI!
# Currently this AI greedily picks the card/wonder that gives it the most points.
#
# Most of the structs used are defined in game/base.py
#
# Some useful methods:
# - AI's wonder                         : ai_game.get_ai_wonder() -> Wonder
# - AI's hand                           : ai_game.get_ai_hand() -> Card[]
# - All wonders                         : ai_game.wonders -> Wonder[]
# - All hands                           : ai_game.hands -> Card[][]
# - Current age                         : ai_game.age -> number
# - All cards in age deck               : get_cards_for_players_age(player_count, age) -> Card[]
# - All possible moves                  : wonder.get_all_possible_selections(wonders, hand) -> Selection[]
# - Validate selection                  : wonder.validate_selection(wonders, hand, selection) -> (bool, string)
# - Get Payment with min total          : wonder.get_min_gold_payment(wonders, hand, selection) -> Payment
# - Get all Payment options             : wonder.get_all_payment_plans(wonders, hand, selection) -> Payment[]
# - New wonder with selection performed : wonder.with_simulated_selection(wonders, selection) -> Wonder
# - Total points                        : wonder.compute_points_total() -> number
# - Check if wonder has an effect       : wonder.has_effect(effect_type[, effect_subtype]) -> bool
# - All resources                       : wonder.get_resources() -> (string[], string[])
# - All purchasable resources           : wonder.get_purchasable_resources() -> (string[], string[])
# - Full list of resources produced     : wonder.get_all_resources_produced() -> string[]
# - All cards of a color                : wonder.get_cards_by_color(color) -> Card[]
# - Latest-build stage                  : wonder.get_last_built_stage() -> WonderStage
# - Next free stage                     : wonder.get_next_free_stage() -> WonderStage
# - Total shield count                  : wonder.get_shields() -> number
# - Has a specific chain                : wonder.has_chain(chain) -> bool

AgeAiVar = namedtuple('AgeAiVar', ['age', 'default_value', 'mutation_profile'])


class AiVar:
    def __init__(self, default_arr, mutation_profile):
        self.ages = [
            AgeAiVar(1, default_arr[0], mutation_profile),
            AgeAiVar(2, default_arr[1], mutation_profile),
            AgeAiVar(3, default_arr[2], mutation_profile),
        ]

    def __str__(self):
        return f"1:{self.ages[0].default_value}, 2:{self.ages[1].default_value}, 3:{self.ages[2].default_value}"

    def get_age_value(self, age):
        agv = self.ages[age].default_value
        if isinstance(agv, str):
            return eval(agv, {"a1": self.ages[0].default_value, "a2": self.ages[1].default_value, "a3": self.ages[2].default_value})
        else:
            return agv

    def clamp_value(self, value):
        min_allowed = self.ages[0].mutation_profile[2]
        max_allowed = self.ages[0].mutation_profile[3]

        return min(max_allowed, max(min_allowed, value))

    def mutate_from(self, curr_value):
        # slow is 4% while normal is 10%
        min_allowed = self.ages[0].mutation_profile[2]
        max_allowed = self.ages[0].mutation_profile[3]
        max_delta = 0.04 if self.ages[0].mutation_profile[1] == 'slow' else 0.1
        max_change = max_delta * (max_allowed - min_allowed)
        low = max(min_allowed, curr_value - max_change)
        high = min(max_allowed, curr_value + max_change)

        return uniform(low, high)


# mutability
MUTABILITY_NONE = 0
MUTABILITY_RARE = 1
MUTABILITY_LOW = 25
MUTABILITY_MED = 500
MUTABILITY_HIGH = 1000

MUTATE_SIZE_NONE = 0
MUTATE_SIZE_TINY = 0.05
MUTATE_SIZE_SMALL = 0.1
MUTATE_SIZE_BIG = 0.2

CardSituation = namedtuple('CardSituation', ['card', 'action', 'sit_vars', 'score'])


class CardSituation(CardSituation):
    def __repr__(self):
        card = f" {self.card.name}" if self.card else ''
        score = "[{:.3f}]".format(self.score).ljust(10)
        if self.sit_vars['can_play'] == 0:
            return f"N/A        {self.action} {card}"
        return f"{score} {self.action} {card}"

    def make_selection(self):
        if self.action == 'wonder':
            return Selection(self.card, self.action, self.sit_vars["bury_stage_payment"])
        else:
            return Selection(self.card, self.action, self.sit_vars["play_payment"])

# AI coefficients for each board/side
wonder_coefficients = {
    "#default": {
        "generation": 0,
        # declares importance of burying stage for each age
        "stage1_w":     AiVar([1,   2,     3], ['rare', 'normal', 0, 3]),
        "stage2_w":     AiVar([0.5, 1,     2], ['rare', 'normal', 0, 2]),
        "stage3_w":     AiVar([0.1, 0.1,   1], ['rare', 'normal', 0, 3]),
        "stage4_w":     AiVar([0.1, 0.1,   1], ['rare', 'normal', 0, 3]),
        "military_l_w": AiVar([1,   1,     1], ['normal', 'normal', 0, 3]),
        "military_r_w": AiVar([1,   1,     1], ['normal', 'normal', 0, 3]),
        "science_w":    AiVar([1,   1,     1], ['rare', 'normal', 0, 3]),
        "blue_w":       AiVar([1,   1,     1], ['rare', 'normal', 0, 3]),
        "unlock_stage_w":   AiVar([1, 1,   1], ['normal', 'normal', 0, 3]),
        "cheapen_brown_w":  AiVar([1, 1, 1],   ['normal', 'normal', 0, 3]),
        "cheapen_gray_w":   AiVar([1, 1, 1],   ['normal', 'normal', 0, 3]),
        "chain_ws_hammer":       AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_waterdrop":    AiVar([1.1, 1.1, 1.1], ['normal', 'normal', 0, 3]),
        "chain_ws_star":         AiVar([1.2, 1.2, 1.2], ['normal', 'normal', 0, 3]),
        "chain_ws_mask":         AiVar([1.1, 1.1, 1.1], ['normal', 'normal', 0, 3]),
        "chain_ws_camel":        AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_market":       AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_horseshoe":    AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_bowl":         AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_target":       AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_lamp":         AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_scales":       AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_book":         AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_lighthouse":   AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_barrel":       AiVar([0.9, 0.9, 0.9], ['normal', 'normal', 0, 3]),
        "chain_ws_castle":       AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_helmet":       AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_bolt":         AiVar([0.9, 0.9, 0.9], ['normal', 'normal', 0, 3]),
        "chain_ws_torch":        AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_saw":          AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_planets":      AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_temple":       AiVar([1.15, 1.15, 1.15], ['normal', 'normal', 0, 3]),
        "chain_ws_scroll":       AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_harp":         AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "chain_ws_feather":      AiVar([1, 1, 1], ['normal', 'normal', 0, 3]),
        "military_sit_ws_down2+": AiVar([1, 1, 1],  ['normal', 'normal', 0, 3]),
        "military_sit_ws_down1":  AiVar([1, 1, 1],  ['normal', 'normal', 0, 3]),
        "military_sit_ws_tied":   AiVar([1, 1, 1],  ['normal', 'normal', 0, 3]),
        "military_sit_ws_up1":    AiVar([1, 1, 1],  ['normal', 'normal', 0, 3]),
        "military_sit_ws_up2+":   AiVar([1, 1, 1],  ['normal', 'normal', 0, 3]),

        # target resource amounts per age
        "wood_t":           AiVar([2.2, 3,  'a2'], ['rare', 'normal', 0, 3]),
        "ore_t":            AiVar([1,   3,  'a2'], ['rare', 'normal', 0, 3]),
        "clay_t":           AiVar([2.1, 3,  'a2'], ['rare', 'normal', 0, 3]),
        "stone_t":          AiVar([2,   4,  'a2'], ['rare', 'normal', 0, 4]),
        "loom_t":           AiVar([1.1, 1,     1], ['none', 'normal', 1, 1]),
        "press_t":          AiVar([1,   1,     1], ['none', 'normal', 1, 1]),
        "glass_t":          AiVar([1,   1,     1], ['none', 'normal', 1, 1]),

        "resource_c":       AiVar([2,   1.5,     1], ['normal', 'normal', 0, 3]),
        "points_c":         AiVar([0.5,   1,     1.5], ['normal', 'normal', 0, 3]),
        "coin_add_0_c":     AiVar([0.5,   1,     1], ['normal', 'normal', 0, 3]),     # adding coin when at 0
        "coin_add_c":       AiVar([0.25,   0.25,     0.25], ['normal', 'normal', 0, 3]),
        "coin_spend_c":     AiVar([-0.25, -0.25, -0.25], ['normal', 'normal', -2, 3]),
        "coin_spend_0_c":   AiVar([-0.75, -0.75, -0.75], ['normal', 'normal', -2, 3]),
        "military_c":       AiVar([1,   1,     1], ['normal', 'normal', 0, 3]),
        "chain_c":          AiVar([1,   1,   '0'], ['normal', 'normal', 0, 3]),
    }
}

MutateGene = namedtuple('MutateGene', ['name', 'pick_weight', 'age', 'ai_var'])
mutate_genes = []
max_pick_weight = 0

for i, (k, v) in enumerate(wonder_coefficients["#default"].items()):
    if isinstance(v, AiVar):
        for age in v.ages:
            if not isinstance(age.default_value, str) and age.mutation_profile[0] != 'none':
                pick_weight = 10  # assume rare
                if age.mutation_profile[0] == 'normal':
                    pick_weight = 100

                max_pick_weight += pick_weight
                mutate_genes.append(MutateGene(k, max_pick_weight, age.age, v))


# Compute the point gain of the move.
def points_for_selection(wonders, wonder, selection):
    old_points = wonder.compute_points_total(wonders)
    new_points = wonder.with_simulated_selection(wonders, selection).compute_points_total(wonders)
    return new_points - old_points


def does_unlock_wonder_stage(ai_game, cards, wonder, wonder_next):
    wonders = ai_game.wonders
    future_wonder_stages = wonder.stages[wonder.stages_built:]
    score = 0
    for stage in future_wonder_stages:
        old_payment = wonder.get_min_gold_payment(wonders, cards, Selection(None, 'wonder', None))
        new_payment = wonder_next.get_min_gold_payment(wonders, cards, Selection(None, 'wonder', None))
        if not old_payment and new_payment:
            score += 1
    return True if score > 0 else False


def expand_ai_vars(src, dest, age):
    for key in src:
        if isinstance(src[key], AiVar):
            dest[key] = src[key].get_age_value(age)
        elif isinstance(src[key], int) or isinstance(src[key], str):
            dest[key] = src[key]
        else:
            dest[key] = expand_ai_vars(src[key], {}, age)
    return dest


def get_shield_w(shields_per_age, delta, coefficients):
    if delta < (-shields_per_age):
        return coefficients["military_sit_ws_down2+"]
    if delta < 0:
        return coefficients["military_sit_ws_down1"]
    if delta > shields_per_age:
        return coefficients["military_sit_ws_up2+"]
    if delta > 0:
        return coefficients["military_sit_ws_up1"]
    return coefficients["military_sit_ws_tied"]


def calc_score_from_sit_vars(coefficients, sit_vars):
    total = 0
    if not sit_vars["can_play"]:
        return 0
    total += sit_vars["resource_add_w"] * coefficients["resource_c"]
    total += sit_vars["points_add"] * coefficients["points_c"]
    if sit_vars["coin_add_w"] != 0:
        if sit_vars["coin_start"] == 0:
            total += sit_vars["coin_add_w"] * coefficients["coin_add_0_c"]
        else:
            total += sit_vars["coin_add_w"] * coefficients["coin_add_c"]

    if sit_vars["coin_spend_w"] != 0:
        if sit_vars["coin_start"] == sit_vars["coin_spend_w"]:
            total += sit_vars["coin_spend_w"] * coefficients["coin_spend_0_c"]
        else:
            total += sit_vars["coin_spend_w"] * coefficients["coin_spend_c"]

    total += sit_vars["military_l_w"] * coefficients["military_c"]
    total += sit_vars["military_r_w"] * coefficients["military_c"]
    total += sit_vars["chain_w"] * coefficients["chain_c"]
    total += sit_vars["science_w"]
    total += sit_vars["cheapen_w"]
    total += sit_vars["unlock_stage_w"]
    total += sit_vars["bury_stage_w"]

    # print(f"score: {total}\n    {sit_vars}\n    {coefficients}\n####")
    return total


def format_factor(lbl1, val1, lbl2, val2):
    total = "[{:.3f}]".format(val1 * val2).ljust(10)
    part1 = f"{total} {lbl1}: {'[{:.3f}]'.format(val1)}"
    if lbl2:
        return f"{part1.ljust(40)} {lbl2}: {'[{:.3f}]'.format(val2)}"
    else:
        return part1


def show_details_of_sit_vars_calc(coefficients, sit_vars):
    pad = '        '
    print(f'{pad}{format_factor("resource_add_w", sit_vars["resource_add_w"], "resource_c", coefficients["resource_c"])}')
    print(f'{pad}{format_factor("points_add", sit_vars["points_add"], "points_c", coefficients["points_c"])}')
    if sit_vars["coin_add_w"] != 0:
        if sit_vars["coin_start"] == 0:
            print(f'{pad}{format_factor("coin_add_w", sit_vars["coin_add_w"], "coin_add_0_c", coefficients["coin_add_0_c"])}')
        else:
            print(f'{pad}{format_factor("coin_add_w", sit_vars["coin_add_w"], "coin_add_c", coefficients["coin_add_c"])}')

    if sit_vars["coin_spend_w"] != 0:
        if sit_vars["coin_start"] == sit_vars["coin_spend_w"]:
            print(f'{pad}{format_factor("coin_spend_w", sit_vars["coin_spend_w"], "coin_spend_0_c", coefficients["coin_spend_0_c"])}')
        else:
            print(f'{pad}{format_factor("coin_spend_w", sit_vars["coin_spend_w"], "coin_spend_c", coefficients["coin_spend_c"])}')

    print(f'{pad}{format_factor("military_l_w", sit_vars["military_l_w"], "military_c", coefficients["military_c"])}')
    print(f'{pad}{format_factor("military_r_w", sit_vars["military_r_w"], "military_c", coefficients["military_c"])}')
    print(f'{pad}{format_factor("chain_w", sit_vars["chain_w"], "chain_w", coefficients["chain_c"])}')
    print(f'{pad}{format_factor("science_w", sit_vars["science_w"], None, 1)}')
    print(f'{pad}{format_factor("cheapen_w", sit_vars["cheapen_w"], None, 1)}')
    print(f'{pad}{format_factor("unlock_stage_w", sit_vars["unlock_stage_w"], None, 1)}')
    print(f'{pad}{format_factor("bury_stage_w", sit_vars["bury_stage_w"], None, 1)}')


def calculate_resource_progress(wonder, coefficients):
    have = {"wood": 0, "ore": 0, "stone": 0, "clay": 0, "loom": 0, "press": 0, "glass": 0}

    resources, multi_resources = wonder.get_resources()
    for res in resources:
        have[res] += 1
    for mres in multi_resources:
        for res in mres:
            have[res] += 0.6

    total_need = 0
    total_have = 0
    for res in ["wood", "ore", "clay", "stone", "loom", "press", "glass"]:
        need = coefficients[f"{res}_t"]
        total_need += need
        if have[res] >= need:
            total_have += need
        else:
            total_have += have[res]

    return {"total_have": total_have, "total_need": total_need}


def calc_before_after_sit_vars(wonders, coefficients, wonder_before, wonder_after, sit_vars):
    sit_vars["points_add"] = max(0, wonder_after.compute_points_total(wonders) - wonder_before.compute_points_total(wonders))
    sit_vars["coin_add_w"] = max(0, wonder_after.gold - wonder_before.gold)
    sit_vars["coin_spend_w"] = max(0, wonder_before.gold - wonder_after.gold)

    # now figure out resource impact and do something with multi_resources
    progress = calculate_resource_progress(wonder_before, coefficients)
    progress_next = calculate_resource_progress(wonder_after, coefficients)
    if progress_next["total_have"] > progress["total_have"]:
        sit_vars["resource_add_w"] = progress_next["total_have"] - progress["total_have"]


def create_sit_vars():
    return {
        "resource_add_w": 0,
        "points_add": 0,
        "coin_start": 0,
        "coin_add_w": 0,
        "coin_spend_w": 0,
        "military_l_w": 0,
        "military_r_w": 0,
        "science_w": 0,
        "cheapen_w": 0,
        "bury_stage_w": 0,
        "unlock_stage_w": 0,
        "chain_w": 0,
        "can_play": True,
        "play_payment": None,
        "bury_stage_payment": None
    }


class ScottAi:
    def __init__(self, show_selections=False, verbose=False):
        self.show_selections = show_selections
        self.verbose = verbose
        self.coefficients = {}
        for board_name in wonder_coefficients:
            board = wonder_coefficients[board_name]

            card_coefs = [
                expand_ai_vars(board, {}, 0),
                expand_ai_vars(board, {}, 1),
                expand_ai_vars(board, {}, 2)]
            self.coefficients[board_name] = {
                "player_3": card_coefs,
                "player_4": copy.deepcopy(card_coefs),
                "player_5": copy.deepcopy(card_coefs)
            }

        for wonder_class in ALL_WONDERS:
            wonder = wonder_class()
            hash_name = f"{wonder.name}_{wonder.side}"
            if hash_name not in self.coefficients:
                self.coefficients[hash_name] = copy.deepcopy(self.coefficients["#default"])

    def get_coefficients(self, wonder, ai_game):
        hash_name = f"{wonder.name}_{wonder.side}"
        player_count = f"player_{min(5, max(3, len(ai_game.wonders)))}"

        if hash_name in self.coefficients:
            return self.coefficients[hash_name][player_count][ai_game.age - 1]
        return self.coefficients["#default"][player_count][ai_game.age - 1]

    # when burying, deprive enemies of their cards
    def get_best_bury_card(self, ai_game, cards):
        return cards[0]

    def calc_all_sit_vars(self, ai_game, cards):
        wonder = ai_game.get_ai_wonder()
        wonders = ai_game.wonders
        next_stage = wonder.get_next_free_stage()
        bury_stage_payment = None
        situations = []

        right_neighbor, left_neighbor = wonder.get_neighbors(wonders)
        # passing_to = ai_game.get_pass_to_neighbor()
        coefficients = self.get_coefficients(wonder, ai_game)

        if next_stage:
            bury_stage_payment = wonder.get_min_gold_payment(wonders, cards, Selection(None, 'wonder', None))

            # can we afford to bury?
            if not (bury_stage_payment and wonder.validate_selection(wonders, cards, Selection(None, 'wonder', bury_stage_payment))[0]):
                bury_stage_payment = None
            else:
                wonder_bury_stage = wonder.with_simulated_selection(ai_game.wonders, Selection(None, 'wonder', bury_stage_payment))
                sit_vars = create_sit_vars()
                sit_vars["coin_start"] = wonder.gold
                sit_vars["play_payment"] = bury_stage_payment
                sit_vars["bury_stage_payment"] = bury_stage_payment
                sit_vars["bury_stage_w"] = coefficients[f"stage{next_stage.stage_number}_w"]

                calc_before_after_sit_vars(wonders, coefficients, wonder, wonder_bury_stage, sit_vars)
                situations.append(CardSituation(self.get_best_bury_card(ai_game, cards), 'wonder', sit_vars, calc_score_from_sit_vars(coefficients, sit_vars)))

        sit_vars = create_sit_vars()
        sit_vars["coin_start"] = wonder.gold
        sit_vars["points_add"] = 1
        sit_vars["coin_add_w"] = 3
        situations.append(CardSituation(self.get_best_bury_card(ai_game, cards), 'throw', sit_vars, calc_score_from_sit_vars(coefficients, sit_vars)))

        left_shields = left_neighbor.get_shields()
        right_shields = right_neighbor.get_shields()
        shields_per_age = ai_game.age

        for card in cards:
            payment = wonder.get_min_gold_payment(wonders, cards, Selection(card, 'play', None))
            selection = Selection(card, 'play', payment)
            can_play = 0

            if payment and wonder.validate_selection(wonders, cards, selection)[0]:
                can_play = 1

            wonder_next = wonder.with_simulated_selection(ai_game.wonders, selection)

            sit_vars = create_sit_vars()
            sit_vars["coin_start"] = wonder.gold
            sit_vars["can_play"] = can_play
            sit_vars["play_payment"] = payment
            sit_vars["bury_stage_payment"] = bury_stage_payment

            if not can_play:
                situations.append(CardSituation(card, 'play', sit_vars, calc_score_from_sit_vars(coefficients, sit_vars)))
                continue

            calc_before_after_sit_vars(wonders, coefficients, wonder, wonder_next, sit_vars)
            for chain in card.chains:
                sit_vars["chain_w"] += coefficients[f"chain_ws_{chain}"]

            if card.color == 'red':  # do military situation vars
                new_shields = wonder_next.get_shields()
                sit_vars["military_l_w"] += get_shield_w(shields_per_age, new_shields - left_shields, coefficients)
                sit_vars["military_r_w"] += get_shield_w(shields_per_age, new_shields - right_shields, coefficients)

            if card.color == 'green':  # do science
                sit_vars["science_w"] = coefficients["science_w"]

            for effect in card.effects:
                if effect.type == "tradingpost":
                    sit_vars["cheapen_w"] = coefficients["cheapen_brown_w"]
                elif effect.type == "marketplace":
                    sit_vars["cheapen_w"] = coefficients["cheapen_gray_w"]

            if does_unlock_wonder_stage(ai_game, cards, wonder, wonder_next):
                sit_vars["unlock_stage_w"] = coefficients["unlock_stage_w"]

            situations.append(CardSituation(card, 'play', sit_vars, calc_score_from_sit_vars(coefficients, sit_vars)))

        return situations

    # Required method. Return a Selection representing the move the AI will make.
    def get_selection(self, ai_game, cards):
        wonder = ai_game.get_ai_wonder()
        wonders = ai_game.wonders
        neighbors = wonder.get_neighbors(wonders)
        passing_to = ai_game.get_pass_to_neighbor()
        coefficients = self.get_coefficients(wonder, ai_game)

        situations = self.calc_all_sit_vars(ai_game, cards)
        situations.sort(key=lambda situation: situation.score, reverse=True)
        best_selection = situations[0].make_selection()


        # # Get all possible moves as Selections. All selections will come pre-filled with the lowest valid gold payment.
        # possible_selections = wonder.get_all_possible_selections(ai_game.wonders, cards)
        #
        # # Select the move that gives the highest points.
        # possible_selections.sort(key=lambda selection: points_for_selection(wonders, wonder, selection), reverse=True)
        # best_selection = possible_selections[0]
        #
        # # If the move is to build a wonder stage or throw, randomly choose a card from the hand to use.
        # if best_selection.action in ['wonder', 'throw']:
        #     best_selection = Selection(choice(cards), best_selection.action, best_selection.payment)

        if ai_game.debuggingMode != '':
            print(f"{wonder.name}_{wonder.side} analysis:")
            for i in range(len(situations)):
                sit = situations[i]
                print(f"    {sit}")
                if ai_game.debuggingMode == 'verbose' and sit.sit_vars['can_play'] != 0:
                    show_details_of_sit_vars_calc(coefficients, sit.sit_vars)

        return best_selection

    # Required method. Return a Card representing the card the AI will play from the discard pile.
    # noinspection PyMethodMayBeStatic
    def get_build_card_from_discard(self, ai_game, cards):
        wonder = ai_game.get_ai_wonder()

        # Get all possible Cards to play.
        possible_cards = [card for card in cards if card not in wonder.played_cards]
        # print('Possible discard cards:', [card.name for card in possible_cards])

        # Returning None skips the discard play.
        if len(possible_cards) == 0:
            return None

        # Select the card that gives the highest points.
        possible_cards.sort(key=lambda card: points_for_selection(ai_game.wonders, wonder, Selection(card, 'play', None)), reverse=True)
        best_card = possible_cards[0]

        if ai_game.debuggingMode != '':
            print(f"{wonder.name}_{wonder.side} wants to play from discard: {best_card.name}")

        return best_card

    # Required method. Return 'Day' or 'Night' to choose your wonder side.
    # Provided is a list of all wonder names, in turn order. Your wonder is always index 0 in this list.
    # noinspection PyMethodMayBeStatic
    def get_wonder_side(self, wonder_names):
        my_wonder_name = wonder_names[0]
        # neg_neighbor_wonder_name = wonder_names[-1]
        # pos_neighbor_wonder_name = wonder_names[1]

        # Example: always play Night side on Alexandria and Ephesos, Day otherwise.
        if my_wonder_name in ['Alexandria', 'Ephesos']:
            return 'Night'
        return 'Day'

    def write_coefficients(self, file):
        with open(file, "w") as outfile:
            json.dump(self.coefficients, outfile)

    def read_coefficients(self, file):
        if os.path.isfile(file):
            with open(file) as json_file:
                self.coefficients = json.load(json_file)

    def copy_coefficients(self):
        return copy.deepcopy(self.coefficients)

    def restore_coefficients(self, coefficients):
        self.coefficients = copy.deepcopy(coefficients)

    def pick_mutate_genes(self):
        genes = []
        indexes = [randint(0, max_pick_weight) for _ in range(25)]
        indexes.sort()

        for gene in mutate_genes:
            idx = indexes[0] if len(indexes) > 0 else 999999999999
            if gene.pick_weight > idx:
                genes.append(gene)
                while len(indexes) > 0 and indexes[0] < gene.pick_weight:
                    indexes.pop(0)

        shuffle(genes)
        return genes

    # MutateGene = namedtuple('MutateGene', ['name', 'pick_weight', 'age', 'ai_var'])
    def remutate_coefficients(self, board_name, player_count, parent_coefficients):
        pc_hash = f"player_{min(5, max(3, player_count))}"
        coef_base = self.coefficients[board_name][pc_hash]

        for gene in mutate_genes:
            old_val = parent_coefficients[board_name][pc_hash][gene.age-1][gene.name]
            new_val = coef_base[gene.age-1][gene.name]
            if old_val != new_val:
                next_val = gene.ai_var.clamp_value(new_val + (new_val - old_val))
                coef_base[gene.age-1][gene.name] = next_val
                # print(f"remutating {gene.name}[{gene.age}]: {new_val} -> {next_val}")

    def mutate_coefficients(self, board_name, player_count):
        pc_hash = f"player_{min(5, max(3, player_count))}"
        mutations = randint(1, 4)
        tries = 0
        genes = self.pick_mutate_genes()
        coef_base = self.coefficients[board_name][pc_hash]

        while mutations > 0 and len(genes) > 0:
            mutate_gene = genes.pop(0)
            old = coef_base[mutate_gene.age-1][mutate_gene.name]
            new = mutate_gene.ai_var.mutate_from(old)
            coef_base[mutate_gene.age-1][mutate_gene.name] = new
            # print(f"mutating {mutate_gene.name}[{mutate_gene.age}]: {old} -> {new}")
            mutations -= 1

    def show_mutations(self, board_name, player_count, parent_coefficients):
        CRED = '\033[91m'
        CEND = '\033[0m'
        pc_hash = f"player_{min(5, max(3, player_count))}"
        coef_base = self.coefficients[board_name][pc_hash]

        for gene in mutate_genes:
            old_val = parent_coefficients[board_name][pc_hash][gene.age-1][gene.name]
            new_val = coef_base[gene.age-1][gene.name]
            if old_val != new_val:
                print(CRED + f"Mutated {gene.name}[{gene.age}]: {old_val} -> {new_val}" + CEND)

