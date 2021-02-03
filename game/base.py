from collections import namedtuple

# Resource lists
BROWN_RESOURCES = ['wood', 'ore', 'clay', 'stone']
GREY_RESOURCES = ['glass', 'press', 'loom']
ALL_RESOURCES = BROWN_RESOURCES + GREY_RESOURCES

# The cost of a card or wonder stage.
# - gold: the pure gold cost of the card (e.g. Timber Yard costs 1 gold)
# - resources: a list of resources required (e.g. ["wood", "wood", "ore"])
# - chain: the chain used to build this card for free
Cost = namedtuple('Cost', ['gold', 'resources', 'chain'])

# An effect provided by a card or wonder stage.
# - type: the type of the effect (e.g. Vineyard has the "gold_for_cards" type)
# - subtype: a further specification of the effect type (e.g. Vineyard has the "brown" subtype to indicate it only applies to brown cards)
# - amount: the amount of the effect, if applicable (e.g. a 4-point blue card would have amount=4)
Effect = namedtuple('Effect', ['type', 'subtype', 'amount'])

# A card.
# - name: the name of the card (e.g. "Archery Range")
# - color: the color of the card ("brown", "grey", "red", "green", "blue", "yellow", "purple")
# - cost: the Cost of the card
# - effects: a list of Effects provided by the card
# - chains: a list of chains provided by the card for future use (e.g. "hammer")
Card = namedtuple('Card', ['name', 'color', 'cost', 'effects', 'chains'])

# A wonder stage.
# - stage_number: the number of the stage (e.g. the second stage of a wonder has stage_number=2)
# - cost: the Cost of the stage
# - effects: a list of Effects provided by the stage
WonderStage = namedtuple('WonderStage', ['stage_number', 'cost', 'effects'])

# Convenience method to define a cost by parameters instead of a resource list.
def cost(gold=0, wood=0, ore=0, clay=0, stone=0, press=0, loom=0, glass=0, chain=None):
    resources = []
    resources.extend('wood' for _ in range(wood))
    resources.extend('ore' for _ in range(ore))
    resources.extend('clay' for _ in range(clay))
    resources.extend('stone' for _ in range(stone))
    resources.extend('press' for _ in range(press))
    resources.extend('loom' for _ in range(loom))
    resources.extend('glass' for _ in range(glass))
    return Cost(gold, resources, chain)

# Represents a payment, split by amount to be paid to the negative neighbor, bank, and positive neighbor.
# - payment.total() returns the sum total gold paid.
Payment = namedtuple('Payment', ['neg', 'bank', 'pos'])
class Payment(Payment):
    def total(self):
        return self.neg + self.bank + self.pos
    def __repr__(self):
        return f"<{self.neg}, {self.bank}, {self.pos}>"

# Represents a selection to be played by a player during a turn.
# - card: the card selected. can be None if unknown
# - action: the action to be performed
#     - "play" plays the card
#     - "wonder" buries the card in the next free wonder stage
#     - "throw" discards the card for 3 gold
# - payment: the payment needed to play the card. note: None is equivalent to Payment(0, 0, 0)
Selection = namedtuple('Selection', ['card', 'action', 'payment'])
class Selection(Selection):
    def __repr__(self):
        card = f" {self.card.name}" if self.card else ''
        gold_cost = self.payment.total() if self.payment else 0
        payment = f" for {gold_cost} gold" if gold_cost > 0 else ''
        if self.action == 'play':
            return f"Play{card}" + payment
        elif self.action == 'wonder':
            return f"Bury{card} to build a wonder stage" + payment
        elif self.action == 'throw':
            return f"Throw{card} for 3 gold"
        return 'ERROR'

# Represents a wonder board in the game and everything attached to it.
# - name: the name of the wonder (e.g. "Giza")
# - side: the side of the wonder ("Day", "Night")
# - starting_effects: effects the wonder starts with (e.g. Giza starts with 1 stone)
# - stages: list of WonderStages of this wonder
# - stages_built: number of stages currently built by this wonder
# - gold: wonder's current gold
# - military tokens: list of this wonder's current military token amounts (e.g. [-1, -1, 3, 5])
# - played_cards: list of all Cards played by this wonders
class Wonder:
    def __init__(self, name, side, starting_gold, starting_effects, stages):
        self.name = name
        self.side = side
        self.starting_effects = starting_effects
        self.starting_gold = starting_gold
        self.stages = stages
        self.stages_built = 0

        self.gold = starting_gold
        self.military_tokens = []
        self.played_cards = []

    def reset(self):
        self.stages_built = 0

        self.gold = self.starting_gold
        self.military_tokens = []
        self.played_cards = []

    # Returns a new Wonder with the specified selection played and all immediate effects applied.
    def with_simulated_selection(self, wonders, selection):
        new_wonder = Wonder(self.name, self.side, self.gold, self.starting_effects, self.stages)
        new_wonder.stages_built = self.stages_built
        new_wonder.military_tokens = self.military_tokens[:]
        new_wonder.played_cards = self.played_cards[:]

        new_wonder.play_selection(wonders, selection, apply_immediate_effects=True)
        return new_wonder

    # Plays the selection on this wonder.
    def play_selection(self, wonders, selection, apply_immediate_effects):
        if selection.action == 'play':
            if selection.payment:
                self.gold -= selection.payment.total()
            self.played_cards.append(selection.card)
            if apply_immediate_effects:
                self.apply_immediate_effects(wonders, selection.card.effects)
        if selection.action == 'wonder':
            if selection.payment:
                self.gold -= selection.payment.total()
            self.stages_built += 1
            if apply_immediate_effects:
                self.apply_immediate_effects(wonders, self.get_last_built_stage().effects)
        if selection.action == 'throw':
            self.gold += 3

    # Applies all immediate effects (e.g. gold from playing Vineyard).
    def apply_immediate_effects(self, wonders, effects):
        neg_neighbor, pos_neighbor = self.get_neighbors(wonders)
        for effect in effects:
            if effect.type == 'gold':
                self.gold += effect.amount
            elif effect.type == 'gold_for_cards':
                gold_per_card = {'brown': 1, 'grey': 2}[effect.subtype]
                num_cards = len(neg_neighbor.get_cards_by_color(effect.subtype)) + len(self.get_cards_by_color(effect.subtype)) + len(pos_neighbor.get_cards_by_color(effect.subtype))
                total_gold = gold_per_card * num_cards
                self.gold += total_gold
            elif effect.type == 'gold_and_points_for_cards':
                gold_per_card = {'brown': 1, 'grey': 2, 'yellow': 1, 'red': 3}[effect.subtype]
                total_gold = gold_per_card * len(self.get_cards_by_color(effect.subtype))
                self.gold += total_gold
            elif effect.type == 'gold_and_points_for_stages':
                total_gold = 3 * self.stages_built
                self.gold += total_gold
    
    # Returns a tuple of Wonders for this wonder's (negative_neighbor, positive_neighbor).
    def get_neighbors(self, wonders):
        i = -1
        for j in range(len(wonders)):
            if wonders[j].name == self.name and wonders[j].side == self.side:
                i = j
                break
        if i < 0:
            raise Exception(f'Wonder {self.name} is not in: {wonders}')
        return (wonders[(i-1) % len(wonders)], wonders[(i+1) % len(wonders)])

    # Returns all effects present in this wonder (starting effects and effects from cards and stages).
    def all_effects(self):
        yield from self.starting_effects
        yield from (effect for stage in self.stages[:self.stages_built] for effect in stage.effects)
        yield from (effect for card in self.played_cards for effect in card.effects)
    
    # Returns True iff the wonder has an effect with the specified type (and optionally subtype).
    def has_effect(self, type, subtype=None):
        return any(effect.type == type and (subtype is None or effect.subtype == subtype) for effect in self.all_effects())
    
    # Returns (resources, multi_resources), with:
    # - resources: all single resources produced (e.g. with Loom and Foundry, resources=["loom", "ore", "ore"])
    # - multi_resources: all multi-resources produced, as lists of their resources (e.g. with Clay Pit and Forum, multi_resources=[["clay", "ore"], ["loom", "press", "glass"]])
    def get_resources(self):
        resources = []
        multi_resources = []
        for effect in self.all_effects():
            if effect.type == 'resource':
                resources.extend(effect.subtype for _ in range(effect.amount))
            if effect.type == 'multi_resource':
                multi_resources.extend(effect.subtype.split('/') for _ in range(effect.amount))
            if effect.type == 'multi_resource_unpurchasable':
                multi_resources.extend(effect.subtype.split('/') for _ in range(effect.amount))
        return (resources, multi_resources)
    
    # Same result as get_resources method, but limited to only resources/multi-resources purchasable by neighbors.
    def get_purchasable_resources(self):
        resources = []
        multi_resources = []
        for effect in self.all_effects():
            if effect.type == 'resource':
                resources.extend(effect.subtype for _ in range(effect.amount))
            if effect.type == 'multi_resource':
                multi_resources.extend(effect.subtype.split('/') for _ in range(effect.amount))
        return (resources, multi_resources)
    
    # Returns a list of all resources produced, treating multi-resources as separate resources (e.g. with Loom and Clay Pit, this returns ["loom", "clay", "ore"])
    def get_all_resources_produced(self):
        resources, multi_resources = self.get_resources()
        for mr in multi_resources:
            resources.extend(mr)
        return resources
    
    # Returns all cards of the given color.
    def get_cards_by_color(self, color):
        return [card for card in self.played_cards if card.color == color]

    # Returns the last built stage (e.g. if the wonder has build TWO stages, returns the SECOND stage)
    # Returns None if no stages are built.
    def get_last_built_stage(self):
        if self.stages_built <= 0:
            return None
        return self.stages[self.stages_built-1]

    # Returns the next stage to build (e.g. if the wonder has build TWO stages, returns the THIRD stage)
    # Returns None if all stages are built.
    def get_next_free_stage(self):
        if self.stages_built >= len(self.stages):
            return None
        return self.stages[self.stages_built]
    
    # Gets the total number of shields in this wonder.
    def get_shields(self):
        shields = 0
        for effect in self.all_effects():
            if effect.type == 'shields':
                shields += effect.amount
        return shields
    
    # Returns True iff this wonder has the given chain on one of its played cards.
    def has_chain(self, chain):
        return any(chain in card.chains for card in self.played_cards)
    
    # Returns (science, multi_science), with:
    # - science: dict counts of each science symbol present
    # - multi_science: list of lists of science symbols produced by multi_science cards (e.g. Scientists Guild gives ["gear", "compass", "tablet"])
    def get_science(self):
        science = {'gear': 0, 'compass': 0, 'tablet': 0}
        multi_science = []
        for effect in self.all_effects():
            if effect.type == 'science':
                science[effect.subtype] += effect.amount
            elif effect.type == 'multi_science':
                multi_science.append(effect.subtype.split('/'))
        return (science, multi_science)
    
    # Computes the current total number of points for this wonder.
    def compute_points_total(self, wonders):
        return sum(self.compute_points_distribution(wonders).values())
    
    # Computes a string representation of the points distribution.
    # Format: military/gold/raw-points/science/yellow/guild/total
    def get_points_str(self, wonders):
        distr = self.compute_points_distribution(wonders)
        return f"m{distr.get('military', 0)}/c{distr.get('gold', 0)}/b{distr.get('points', 0)}/s{distr.get('science', 0)}/y{distr.get('yellow', 0)}/g{distr.get('guild', 0)}/T:{sum(distr.values())}"

    # Computes the point distribution (as a dict) for points from all sources.
    def compute_points_distribution(self, wonders):
        neg_neighbor, pos_neighbor = self.get_neighbors(wonders)
        points = {'points': 0, 'military': 0, 'gold': 0, 'science': 0, 'yellow': 0, 'guild': 0}
        for effect in self.all_effects():
            if effect.type == 'points':
                points['points'] += effect.amount
            elif effect.type == 'gold_and_points_for_cards':
                points_per_card = {'brown': 1, 'grey': 2, 'yellow': 1, 'red': 1}[effect.subtype]
                points['yellow'] += points_per_card * len(self.get_cards_by_color(effect.subtype))
            elif effect.type == 'gold_and_points_for_stages':
                points['yellow'] += 1 * self.stages_built
            elif effect.type == 'points_for_cards':
                points_per_card = {'brown': 1, 'grey': 2, 'blue': 1, 'yellow': 1, 'red': 1, 'green': 1}[effect.subtype]
                num_cards = len(neg_neighbor.get_cards_by_color(effect.subtype)) + len(pos_neighbor.get_cards_by_color(effect.subtype))
                points['guild'] += points_per_card * num_cards
            elif effect.type == 'points_for_stages':
                num_stages = neg_neighbor.stages_built + self.stages_built + pos_neighbor.stages_built
                points['guild'] += 1 * num_stages
            elif effect.type == 'points_for_finished_wonder':
                if self.stages_built == len(self.stages):
                    points['guild'] += 7
            elif effect.type == 'points_for_self_cards':
                points['guild'] += 1 * len(self.get_cards_by_color(effect.subtype))
        points['military'] += sum(self.military_tokens)
        points['gold'] += self.gold // 3
        points['science'] += self.compute_science_points()
        return points
    
    # Computes the number of points from science.
    def compute_science_points(self):
        science, multi_science = self.get_science()
        return max(self.science_points_for(science, multi_science))
    
    # Helper for compute_science_points
    def science_points_for(self, science, multi_science):
        if not multi_science:
            yield science['gear']**2 + science['compass']**2 + science['tablet']**2 + 7 * min(science[s] for s in science)
            return
        ms = multi_science[0]
        for s in ms:
            science[s] += 1
            yield from self.science_points_for(science, multi_science[1:])
            science[s] -= 1

    # Returns a list of Selections for all possible moves from the given hand.
    # Will include building a wonder stage (if possible) and discarding, but the Selection's card will be None.
    def get_all_possible_selections(self, wonders, hand):
        result = []
        for card in hand:
            payment = self.get_min_gold_payment(wonders, hand, Selection(card, 'play', None))
            selection = Selection(card, 'play', payment)
            if payment and self.validate_selection(wonders, hand, selection)[0]:
                result.append(selection)
        stage = self.get_next_free_stage()
        if stage:
            payment = self.get_min_gold_payment(wonders, hand, Selection(None, 'wonder', None))
            selection = Selection(None, 'wonder', payment)
            if payment and self.validate_selection(wonders, hand, selection)[0]:
                result.append(selection)
        result.append(Selection(None, 'throw', None))
        return result
    
    # Validates the selection. Returns (True, _) if selection is valid, and (False, error) if invalid.
    def validate_selection(self, wonders, hand, selection):
        if selection.card and selection.card not in hand:
            return (False, f"Selection made for a card not in hand: {selection.card.name}")
        if selection.action == 'play':
            if any(selection.card.name == card.name for card in self.played_cards):
                return (False, f"Selection made for a card already played in wonder: {selection.card.name}")
            return self.validate_purchase(wonders, hand, selection)
        if selection.action == 'wonder':
            if not self.get_next_free_stage():
                return (False, f"Selection made to build a wonder stage when all stages are already built")
            return self.validate_purchase(wonders, hand, selection)
        # Otherwise, action == 'throw', which is always valid
        return (True, None)
    
    # Helper for validate_selection
    def validate_purchase(self, wonders, hand, selection):
        payment = selection.payment or Payment(0, 0, 0)
        if self.gold < payment.total():
            return (False, "Wonder does not have enough gold to complete purchase")
        cost = selection.card.cost if selection.action == 'play' else self.get_next_free_stage().cost
        payment_plans = self.get_all_payment_plans(wonders, hand, selection)
        if payment not in payment_plans:
            return (False, f"{payment} is not a valid payment plan for purchase")
        return (True, None)
    
    # Returns the lowest total Payment for the given selection.
    # In the case of a tie, returns the Payment which best balances payment across neighbors.
    def get_min_gold_payment(self, wonders, hand, selection):
        payment_plans = self.get_all_payment_plans(wonders, hand, selection)
        if not payment_plans:
            return None

        min_payment_total = min(plan.total() for plan in payment_plans)

        return min((plan for plan in payment_plans if plan.total() == min_payment_total), key=lambda plan: abs(plan.pos - plan.neg))
    
    # Returns a list of all valid Payments for the given selection.
    def get_all_payment_plans(self, wonders, hand, selection):
        if selection.action == 'wonder' and not self.get_next_free_stage():
            return []
        cost = selection.card.cost if selection.action == 'play' else self.get_next_free_stage().cost
        color = selection.card.color if selection.action == 'play' else None
        neg_neighbor, pos_neighbor = self.get_neighbors(wonders)
        if cost.chain and self.has_chain(cost.chain):
            return [Payment(0, 0, 0)]
        if color and self.has_effect('free_build_first_color', '') and len(self.get_cards_by_color(color)) == 0:
            return [Payment(0, 0, 0)]
        # Assuming the presence of a color means it's a card
        if color and self.has_effect('free_build_alpha', '') and len(hand) == 7:
            return [Payment(0, 0, 0)]
        if color and self.has_effect('free_build_omega', '') and len(hand) == 2:
            return [Payment(0, 0, 0)]
        resources, multi_resources = self.get_resources()
        pos_purchasable_resources, pos_purchasable_multi_resources = pos_neighbor.get_purchasable_resources()
        neg_purchasable_resources, neg_purchasable_multi_resources = neg_neighbor.get_purchasable_resources()
        has_pos_trading = self.has_effect('tradingpost', 'pos')
        has_neg_trading = self.has_effect('tradingpost', 'neg')
        has_marketplace = self.has_effect('marketplace', '')
        required_resources = cost.resources[:]
        for resource in resources:
            if resource in required_resources:
                required_resources.remove(resource)
        payment_plans = self.payment_plans_for(cost.gold, required_resources, multi_resources, has_pos_trading, has_neg_trading, has_marketplace, pos_purchasable_resources, pos_purchasable_multi_resources, neg_purchasable_resources, neg_purchasable_multi_resources)
        l = list(set(payment_plans))
        return l
    
    # Helper for get_all_payment_plans
    def payment_plans_for(self, gold, rr, mr, htpos, htneg, hm, prpos, pmrpos, prneg, pmrneg):
        if not rr:
            yield Payment(0, gold, 0)
            return
        resource = rr[0]
        grey = resource in GREY_RESOURCES
        for i in range(len(mr)):
            if resource in mr[i]:
                yield from self.payment_plans_for(gold, rr[1:], mr[:i] + mr[i+1:], htpos, htneg, hm, prpos, pmrpos, prneg, pmrneg)
        for i in range(len(prpos)):
            cost = 1 if grey and hm or not grey and htpos else 2
            if resource == prpos[i]:
                yield from self.add_payment(self.payment_plans_for(gold, rr[1:], mr, htpos, htneg, hm, prpos[:i] + prpos[i+1:], pmrpos, prneg, pmrneg), 0, 0, cost)
        for i in range(len(prneg)):
            cost = 1 if grey and hm or not grey and htneg else 2
            if resource == prneg[i]:
                yield from self.add_payment(self.payment_plans_for(gold, rr[1:], mr, htpos, htneg, hm, prpos, pmrpos, prneg[:i] + prneg[i+1:], pmrneg), cost, 0, 0)
        for i in range(len(pmrpos)):
            cost = 1 if grey and hm or not grey and htpos else 2
            if resource in pmrpos[i]:
                yield from self.add_payment(self.payment_plans_for(gold, rr[1:], mr, htpos, htneg, hm, prpos, pmrpos[:i] + pmrpos[i+1:], prneg, pmrneg), 0, 0, cost)
        for i in range(len(pmrneg)):
            cost = 1 if grey and hm or not grey and htneg else 2
            if resource in pmrneg[i]:
                yield from self.add_payment(self.payment_plans_for(gold, rr[1:], mr, htpos, htneg, hm, prpos, pmrpos, prneg, pmrneg[:i] + pmrneg[i+1:]), cost, 0, 0)

    # Helper for payment_plans_for
    def add_payment(self, plans, neg, bank, pos):
        for payment in plans:
            yield Payment(payment.neg + neg, payment.bank + bank, payment.pos + pos)

    # Returns a representation of the wonder.
    # Format: [name][side](gold=[gold], res=[resources])
    # - resources: the first letter in each resource's name (e.g. stone="s", ore="o"). all multi-resources are "m"
    def __repr__(self):
        resources, multi_resources = self.get_resources()
        resources_str = ''.join(r[0] for r in resources) + ''.join(f"[{'|'.join(t[0] for t in m)}]" for m in multi_resources)
        return f"{self.name}{self.side}(gold={self.gold}, res={resources_str})"
