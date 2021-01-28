from game.base import *
from game.deck import *
from game.wonders import *
from random import choice

def get_effects_from_selection(ai_game, selection):
    if selection.action == 'play':
        return selection.card.effects
    if selection.action == 'wonder':
        return ai_game.get_ai_info().wonder.get_next_free_stage().effects
    return []

def score_multi(ai_game, selection):
    score = 0
    for effect in get_effects_from_selection(ai_game, selection):
        if effect.type == 'multi_resource' and len(effect.subtype.split('/')) == 2:
            score += 1
    return score

def score_grey(ai_game, selection):
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    if wonder.name + wonder.side in ['BabylonDay', 'BabylonNight', 'HalikarnassosNight']:
        return 0
    score = 0
    effects = get_effects_from_selection(ai_game, selection)
    if len(effects) == 1 and effects[0].type == 'resource' and effects[0].subtype in ['glass', 'loom', 'press']:
        score += 1
    return score

def score_chain(ai_game, selection):
    if selection.action != 'play':
        return 0
    score = len(selection.card.chains)
    return score

def score_unlock_wonder_stage(ai_game, selection):
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    hand = ai_game.get_ai_hand()
    future_wonder_stages = wonder.stages[wonder.stages_built:]
    score = 0
    for stage in future_wonder_stages:
        old_payment = wonder.get_min_gold_payment(ai_game.wonders, hand, Selection(None, 'wonder', None))
        new_payment = wonder.with_simulated_selection(ai_game.wonders, selection).get_min_gold_payment(ai_game.wonders, hand, Selection(None, 'wonder', None))
        if not old_payment and new_payment:
            score += 1
    return score

def score_cheapen_wonder_stage(ai_game, selection):
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    future_wonder_stages = wonder.stages[wonder.stages_built:]

    resources_produced_without_card = wonder.get_all_resources_produced()
    resources_produced_with_card = wonder.with_simulated_selection(ai_game.wonders, selection).get_all_resources_produced()

    grey_mod = 0.5 if wonder.has_effect('marketplace', '') else 1
    brown_mod = 0.5 if wonder.has_effect('tradingpost', 'neg') or wonder.has_effect('tradingpost', 'pos') else 1

    score = 0
    score_mult = 1
    for stage in future_wonder_stages:
        resources_needed = stage.cost.resources
        for r in ALL_RESOURCES:
            rneeded = sum(1 for rn in resources_needed if rn == r)
            rprod_without_card = sum(1 for rn in resources_produced_without_card if rn == r)
            rprod_with_card = sum(1 for rn in resources_produced_with_card if rn == r)
            benefit = max(min(rprod_with_card, rneeded) - rprod_without_card, 0)
            tpost_mult = grey_mod if r in GREY_RESOURCES else brown_mod
            score += score_mult * tpost_mult * benefit
        score_mult = score_mult/(1 + score_mult)  # 1 -> 1/2 -> 1/3 -> ...
    return score

def score_unlock_future_cards(ai_game, selection):
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    hand = ai_game.get_ai_hand()
    score = 0
    for age in [1, 2, 3]:
        if age < ai_game.age: continue
        score_mult = {0: 1, 1: 1, 2: 0.5}[age - ai_game.age]
        for future_card in get_cards_for_players_age(len(ai_game.wonders), age):
            old_payment = wonder.get_min_gold_payment(ai_game.wonders, hand, Selection(future_card, 'play', None))
            new_payment = wonder.with_simulated_selection(ai_game.wonders, selection).get_min_gold_payment(ai_game.wonders, hand, Selection(future_card, 'play', None))
            if not old_payment and new_payment:
                score += score_mult
    return score

def score_cheapen_future_cards(ai_game, selection):
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()

    resources_produced_without_card = wonder.get_all_resources_produced()
    resources_produced_with_card = wonder.with_simulated_selection(ai_game.wonders, selection).get_all_resources_produced()

    grey_mod = 0.5 if wonder.has_effect('marketplace', '') else 1
    brown_mod = 0.5 if wonder.has_effect('tradingpost', 'neg') or wonder.has_effect('tradingpost', 'pos') else 1

    score = 0
    for age in [1, 2, 3]:
        if age < ai_game.age: continue
        score_mult = {0: 1, 1: 1, 2: 0.5}[age - ai_game.age]
        for future_card in get_cards_for_players_age(len(ai_game.wonders), age):
            resources_needed = future_card.cost.resources
            for r in ALL_RESOURCES:
                rneeded = sum(1 for rn in resources_needed if rn == r)
                rprod_without_card = sum(1 for rn in resources_produced_without_card if rn == r)
                rprod_with_card = sum(1 for rn in resources_produced_with_card if rn == r)
                benefit = max(min(rprod_with_card, rneeded) - rprod_without_card, 0)
                tpost_mult = grey_mod if r in GREY_RESOURCES else brown_mod
                score += score_mult * tpost_mult * benefit
    return score

def score_points(ai_game, selection):
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    payment = selection.payment or Payment(0, 0, 0)
    cards_left = len(ai_game.get_ai_hand())
    old_points = wonder.compute_points_total(ai_game.wonders)
    new_points = wonder.with_simulated_selection(ai_game.wonders, selection).compute_points_total(ai_game.wonders)
    points = new_points - old_points
    # Points removed from cost
    points -= payment.total()/3
    for effect in get_effects_from_selection(ai_game, selection):
        # Points from gold
        if effect.type == 'gold':
            points += effect.amount/3
        # Additional projected points from guilds
        if cards_left > 4 and effect.type == 'points_for_cards' and effect.subtype in ['blue', 'yellow', 'green', 'red']:
            points += 1
        if cards_left > 4 and effect.type == 'points_for_stages':
            points += 1
        if effect.type == 'points_for_self_cards' and effect.subtype == 'purple':
            points += 1  # Count itself
            if cards_left > 4: 
                points += 0.5
        # Decorators Guild fix
        if effect.type == 'points_for_finished_wonder' and points <= 0:
            points += 3
    return points

def score_shields(ai_game, selection):
    if all(effect.type != 'shields' for effect in get_effects_from_selection(ai_game, selection)):
        return 0
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    old_shields = wonder.get_shields()
    new_shields = wonder.with_simulated_selection(ai_game.wonders, selection).get_shields()

    shields_per_age = ai_game.age

    score = 0
    if old_shields > neg_neighbor.get_shields() + shields_per_age:
        score += 0  # >2 military cards away
    elif new_shields > neg_neighbor.get_shields() + shields_per_age:
        score += 0.7  # 1 military card away
    elif new_shields > neg_neighbor.get_shields():
        score += 1  # 0 cards away (already winning)
    elif new_shields > neg_neighbor.get_shields() - shields_per_age:
        score += 0.2  # Losing, but 1 card away
    if old_shields > pos_neighbor.get_shields() + shields_per_age:
        score += 0
    elif new_shields > pos_neighbor.get_shields() + shields_per_age:
        score += 0.7
    elif new_shields > pos_neighbor.get_shields():
        score += 1
    elif new_shields > pos_neighbor.get_shields() - shields_per_age:
        score += 0.2
    return score

def score_nonstandard_effects_as_points(ai_game, selection):
    points = 0
    for effect in get_effects_from_selection(ai_game, selection):
        if effect.type == 'free_build_first_color':
            points += 5 if ai_game.age < 3 else 2
        elif effect.type == 'free_build_alpha':
            points += 1 if ai_game.age < 3 else 0
        elif effect.type == 'free_build_omega':
            points += 2 if ai_game.age < 3 else 1
        elif effect.type == 'play_last_card':
            points += {1: 4, 2: 5, 3: 6}[ai_game.age]
    return points

def score_play_from_discard_as_points(ai_game, selection):
    points = 0
    for effect in get_effects_from_selection(ai_game, selection):
        if effect.type != 'build_from_discard':
            continue
        discard_age = ai_game.age
        if len(ai_game.get_ai_hand()) > 2:
            discard_age -= 1
            points -= 1
        points_for_age = {0: -100, 1: 2, 2: 4, 3: 6}[discard_age]
        points += points_for_age
    return points

def score_science(ai_game, selection):
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    if (wonder.name + wonder.side) not in ['BabylonDay', 'BabylonNight', 'HalikarnassosNight']:
        return 0
    points = 0
    for effect in get_effects_from_selection(ai_game, selection):
        if effect.type in ['science', 'multi_science']:
            points += 1
    return points

def score_wonder_off_age(ai_game, selection):
    if selection.action != 'wonder':
        return 0
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    wonder_num = wonder.stages_built + 1
    wonders_left = len(wonder.stages) - wonder.stages_built

    score = 0
    if ai_game.age == 1 and wonder_num > 1:  # Don't build ahead in age 1
        score -= 3
    if ai_game.age == 2 and wonders_left == 1:  # Don't build last wonder in age 2
        score -= 4
    if ai_game.age == 2 and wonder_num == 1:  # Build first wonder in age 2
        score += 2
    if ai_game.age == 2 and len(ai_game.get_ai_hand()) == 2 and len(wonder.stages) > 2 and wonder_num == 2:  # Build second wonder at end of age 2
        score += 2
    return score

def score_wonder_during_age(ai_game, selection):
    if selection.action != 'wonder':
        return 0
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    wonder_num = wonder.stages_built + 1
    num_cards_in_hand = len(ai_game.get_ai_hand())

    if num_cards_in_hand > 5:
        return 3
    if num_cards_in_hand > 3:
        return 2
    if num_cards_in_hand > 2:
        return 1
    return 0

def score_gold_gain(ai_game, selection):
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    old_gold = wonder.gold
    new_gold = wonder.with_simulated_selection(ai_game.wonders, selection).gold
    gold_gain = new_gold - old_gold
    num_cards_in_hand = len(ai_game.get_ai_hand())

    if ai_game.age == 3 and num_cards_in_hand <= 4:
        return 0

    score = gold_gain
    if score > 6:
        score += 1
    if score > 8:
        score += 1
        
    return score

def score_gold_after_play(ai_game, selection):
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    num_cards_in_hand = len(ai_game.get_ai_hand())
    gold_after_play = wonder.with_simulated_selection(ai_game.wonders, selection).gold

    bad_gold_threshold = {1: 0, 2: 0, 3: 4}[ai_game.age]
    bad_gold_threshold_last_hand = {1: 2, 2: 4, 3: 0}[ai_game.age]

    if gold_after_play - wonder.gold > 0:
        return 0

    score = 0
    if num_cards_in_hand <= 2:
        if wonder.gold < bad_gold_threshold_last_hand:
            score += 1
    else:
        if gold_after_play < bad_gold_threshold:
            score += 1
        
    return score

def score_marketplace_greys(ai_game, selection):
    if all(e.type != 'marketplace' for e in get_effects_from_selection(ai_game, selection)):
        return 0
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    neg_pr, _ = neg_neighbor.get_purchasable_resources()
    pos_pr, _ = pos_neighbor.get_purchasable_resources()
    score = 0
    for grey in ['press', 'glass', 'loom']:
        if grey in neg_pr or grey in pos_pr:
            score += 1
            continue
    return score

def score_tradingpost_browns(ai_game, selection):
    wonder, neg_neighbor, pos_neighbor = ai_game.get_ai_info()
    effects = get_effects_from_selection(ai_game, selection)
    pr, pmr = None, None
    if any(e.type == 'tradingpost' and e.subtype == 'neg' for e in effects):
        pr, pmr = neg_neighbor.get_purchasable_resources()
    if any(e.type == 'tradingpost' and e.subtype == 'pos' for e in effects):
        pr, pmr = pos_neighbor.get_purchasable_resources()
    if not pr or not pmr:
        return 0
    score = len([r for r in pr if r not in GREY_RESOURCES]) + 2*len(pmr)
    return score

def get_score_distribution(ai_game, selection):
    weights = {
        1: {
            'multi': 50,
            'grey': -25,
            'chain': 0.25,
            'unlock_wonder_stage': 6,
            'cheapen_wonder_stage': 4,
            'unlock_future_cards': 4,
            'cheapen_future_cards': 0.25,
            'points': 1,
            'shields': 2,
            'science': 2.25,
            'wonder_off_age': 1,
            'wonder_during_age': -0.33,
            'gold_gain': 0.33,
            'gold_after_play': -3,
            'marketplace_greys': 2.5,
            'tradingpost_browns': 1,
        },
        2: {
            'grey': -3.33,
            'chain': 0.17,
            'unlock_wonder_stage': 7,
            'cheapen_wonder_stage': 3.33,
            'unlock_future_cards': 1.33,
            'cheapen_future_cards': 0.15,
            'points': 1,
            'shields': 5,
            'science': 3.17,
            'wonder_off_age': 1,
            'wonder_during_age': -0.33,
            'gold_gain': 0.17,
            'gold_after_play': -2.4,
        },
        3: {
            'points': 1,
            'shields': 4,
            'wonder_during_age': -1.1,
            'gold_gain': 0.1,
            'gold_after_play': -2,
        }
    }

    age = ai_game.age
    wonder = ai_game.get_ai_info().wonder

    score = {
        'multi': weights[age].get('multi', 0) * score_multi(ai_game, selection),
        'grey': weights[age].get('grey', 0) * score_grey(ai_game, selection),
        'chain': weights[age].get('chain', 0) * score_chain(ai_game, selection),
        'unlock_wonder_stage': weights[age].get('unlock_wonder_stage', 0) * score_unlock_wonder_stage(ai_game, selection),
        'unlock_wonder_stage': weights[age].get('unlock_wonder_stage', 0) * score_unlock_wonder_stage(ai_game, selection),
        'cheapen_wonder_stage': weights[age].get('cheapen_wonder_stage', 0) * score_cheapen_wonder_stage(ai_game, selection),
        'unlock_future_cards': weights[age].get('unlock_future_cards', 0) * score_unlock_future_cards(ai_game, selection),
        'cheapen_future_cards': weights[age].get('cheapen_future_cards', 0) * score_cheapen_future_cards(ai_game, selection),
        'points': weights[age].get('points', 0) * score_points(ai_game, selection),
        'shields': weights[age].get('shields', 0) * score_shields(ai_game, selection),
        'nonstandard_effect': weights[age].get('points', 0) * score_nonstandard_effects_as_points(ai_game, selection),  # Use points weight
        'play_from_discard': weights[age].get('points', 0) * score_play_from_discard_as_points(ai_game, selection),  # Use points weight
        'science': weights[age].get('science', 0) * score_science(ai_game, selection),
        'wonder_off_age': weights[age].get('wonder_off_age', 0) * score_wonder_off_age(ai_game, selection),
        'wonder_during_age': weights[age].get('wonder_during_age', 0) * score_wonder_during_age(ai_game, selection),
        'gold_gain': weights[age].get('gold_gain', 0) * score_gold_gain(ai_game, selection),
        'gold_after_play': weights[age].get('gold_after_play', 0) * score_gold_after_play(ai_game, selection),
        'marketplace_greys': weights[age].get('marketplace_greys', 0) * score_marketplace_greys(ai_game, selection),
        'tradingpost_browns': weights[age].get('tradingpost_browns', 0) * score_tradingpost_browns(ai_game, selection),
    }
    return score

class FirstAi:
    def get_selection(self, ai_game, cards):
        ai_info = ai_game.get_ai_info()
        possible_moves = ai_info.wonder.get_all_possible_moves(ai_game.wonders, cards)

        move = self.choose_pick_scores_reasons(ai_game, possible_moves)
        
        if move.action == 'wonder':
            if len(cards) == 2 and any(e.type == 'build_from_discard' for e in ai_info.wonder.get_next_free_stage().effects):
                bury_card = next((card for card in cards if card in ai_info.wonder.played_cards), None)
                if not bury_card:
                    bury_card = min(cards, key=lambda card: sum(get_score_distribution(ai_game, Selection(card, 'play', None)).values()))
            else:
                bury_card = choice(cards)
            move = Selection(bury_card, move.action, move.payment)
        elif move.action == 'throw':
            if ai_info.wonder.get_next_free_stage() and any(e.type == 'build_from_discard' for e in ai_info.wonder.get_next_free_stage().effects):
                possible_cards = [card for card in cards if card not in ai_info.wonder.played_cards]
                bury_card = max(possible_cards, key=lambda card: sum(get_score_distribution(ai_game, Selection(card, 'play', None)).values()))
            else:
                bury_card = choice(cards)
            move = Selection(choice(cards), move.action, move.payment)

        print('AI wants to:', move)

        return move
    
    def get_build_card_from_discard(self, ai_game, cards):
        ai_info = ai_game.get_ai_info()
        possible_cards = [card for card in cards if card not in ai_info.wonder.played_cards]

        possible_moves = [Selection(card, 'play', None) for card in possible_cards]

        move = self.choose_pick_scores_reasons(ai_game, possible_moves)
        card = move.card
        
        print('AI wants play from discard:', card.name)

        return card

    def choose_pick_scores_reasons(self, ai_game, possible_moves):
        possible_moves_scores = [(move, get_score_distribution(ai_game, move)) for move in possible_moves]
        possible_moves_scores.sort(key=lambda ms: sum(ms[1].values()), reverse=True)
        print([f'{ms[0]} ({sum(ms[1].values())})' for ms in possible_moves_scores])
        
        for m in possible_moves_scores:
            score_distr = m[1]
            reasons = sorted([(s, score_distr[s]) for s in score_distr if score_distr[s] != 0], key=lambda s: s[1], reverse=True)
            print('Reasons to', m[0], ':', ', '.join(f'{r[0]}: {r[1]}' for r in reasons))
        
        return possible_moves_scores[0][0]
    