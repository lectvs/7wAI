from game.deck import *
from game.base import *

from random import choice
from collections import namedtuple

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

AgeAiVar = namedtuple('AgeAiVar', ['default_value', 'mutation_profile'])


class AiVar:
    def __init__(self, default_arr, mutation_profile):
        self.ages = [
            AgeAiVar(default_arr[0], mutation_profile),
            AgeAiVar(default_arr[1], mutation_profile),
            AgeAiVar(default_arr[2], mutation_profile),
        ]

    def __str__(self):
        return f"1:{self.ages[0].default_value}, 2:{self.ages[1].default_value}, 3:{self.ages[2].default_value}"

    def get_age_value(self, age):
        agv = self.ages[age].default_value
        if isinstance(agv, str):
            return eval(agv, {"a1": self.ages[0].default_value, "a2": self.ages[1].default_value, "a3": self.ages[2].default_value})
        else:
            return agv


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
        "chain_ws": {
            "hammer":       AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "waterdrop":    AiVar([1.1, 1.1, 1.1], ['rare', 'normal', 0, 3]),
            "star":         AiVar([1.2, 1.2, 1.2], ['rare', 'normal', 0, 3]),
            "mask":         AiVar([1.1, 1.1, 1.1], ['rare', 'normal', 0, 3]),
            "camel":        AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "market":       AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "horseshoe":    AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "bowl":         AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "target":       AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "lamp":         AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "scales":       AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "book":         AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "lighthouse":   AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "barrel":       AiVar([0.9, 0.9, 0.9], ['rare', 'normal', 0, 3]),
            "castle":       AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "helmet":       AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "bolt":         AiVar([0.9, 0.9, 0.9], ['rare', 'normal', 0, 3]),
            "torch":        AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "saw":          AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "planets":      AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "temple":       AiVar([1.15, 1.15, 1.15], ['rare', 'normal', 0, 3]),
            "scroll":       AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "harp":         AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
            "feather":      AiVar([1, 1, 1], ['rare', 'normal', 0, 3]),
        },
        "military_sit_ws": {
            "down2+": AiVar([1, 1, 1],  ['normal', 'normal', 0, 3]),
            "down1":  AiVar([1, 1, 1],  ['normal', 'normal', 0, 3]),
            "tied":   AiVar([1, 1, 1],  ['normal', 'normal', 0, 3]),
            "up1":    AiVar([1, 1, 1],  ['normal', 'normal', 0, 3]),
            "up2+":   AiVar([1, 1, 1],  ['normal', 'normal', 0, 3])
        },

        # target resource amounts per age
        "wood_t":       AiVar([2.2, 3,  'a2'], ['rare', 'normal', 0, 3]),
        "ore_t":        AiVar([1,   3,  'a2'], ['rare', 'normal', 0, 3]),
        "clay_t":       AiVar([2.1, 3,  'a2'], ['rare', 'normal', 0, 3]),
        "stone_t":      AiVar([2,   4,  'a2'], ['rare', 'normal', 0, 4]),
        "loom_t":       AiVar([1.1, 1,     1], ['none', 'normal', 1, 1]),
        "press_t":      AiVar([1,   1,     1], ['none', 'normal', 1, 1]),
        "glass_t":      AiVar([1,   1,     1], ['none', 'normal', 1, 1]),

        "resource_c":   AiVar([2,   1.5,     1], ['normal', 'normal', 0, 3]),
        "points_c":     AiVar([0.5,   1,     1.5], ['normal', 'normal', 0, 3]),
        "coin_add_0_c": AiVar([0.5,   1,     1], ['normal', 'normal', 0, 3]),     # adding coin when at 0
        "coin_add_c":   AiVar([0.25,   0.25,     0.25], ['normal', 'normal', 0, 3]),
        "coin_spend_c":     AiVar([-0.25, -0.25, -0.25], ['normal', 'normal', -2, 3]),
        "coin_spend_0_c":   AiVar([-0.75, -0.75, -0.75], ['normal', 'normal', -2, 3]),
        "military_c":       AiVar([1,   1,     1], ['normal', 'normal', 0, 3]),
        "chain_c":          AiVar([1,   1,   '0'], ['normal', 'normal', 0, 3]),
    }
}


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
        else:
            dest[key] = expand_ai_vars(src[key], {}, age)
    return dest


def get_shield_w(shields_per_age, delta, military_sit_ws):
    if delta < (-shields_per_age):
        return military_sit_ws["down2+"]
    if delta < 0:
        return military_sit_ws["down1"]
    if delta > shields_per_age:
        return military_sit_ws["up2+"]
    if delta > 0:
        return military_sit_ws["up1"]
    return military_sit_ws["tied"]


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

            self.coefficients[board_name] = [
                expand_ai_vars(board, {}, 0),
                expand_ai_vars(board, {}, 1),
                expand_ai_vars(board, {}, 2)]

    def get_coefficients(self, wonder, ai_game):
        hash_name = f"{wonder.name}_{wonder.side}"

        if hash_name in self.coefficients:
            return self.coefficients[hash_name][ai_game.age - 1]
        return self.coefficients["#default"][ai_game.age - 1]

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
        chain_ws = coefficients["chain_ws"]
        military_sit_ws = coefficients["military_sit_ws"]

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
                sit_vars["chain_w"] += chain_ws[chain]

            if card.color == 'red':  # do military situation vars
                new_shields = wonder_next.get_shields()
                sit_vars["military_l_w"] += get_shield_w(shields_per_age, new_shields - left_shields, military_sit_ws)
                sit_vars["military_r_w"] += get_shield_w(shields_per_age, new_shields - right_shields, military_sit_ws)

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
