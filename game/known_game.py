from game.base import *

class KnownGame:
    def __init__(self, wonders):
        self.wonders = wonders
        self.hands = [[] for wonder in wonders]
        self.discard_pile = []
        self.age = 1
        self.age_initialized = False
        self.wait_for_last_card_play = False
        self.wait_for_discard_play = False

    def initialize_age(self, age, hands):
        if len(hands) != len(self.wonders):
            raise Exception("Number of wonders is different from the number of hands")
        if any(len(hand) != 7 for hand in hands):
            raise Exception("Hands do not all contain 7 cards")
        self.hands = hands
        self.wait_for_last_card_play = False
        self.wait_for_discard_play = False
        self.age = age
        self.age_initialized = True

    def execute_turn(self, selections):
        # Validate
        if not self.age_initialized:
            raise Exception("Age is not initialized")
        if self.wait_for_last_card_play:
            raise Exception("Cannot play now, waiting for Babylon to play last card")
        if self.wait_for_discard_play:
            raise Exception("Cannot play now, waiting for Halikarnassos to build from the discard pile")
        if len(selections) != len(self.wonders):
            raise Exception("Number of selections is different from the number of hands")
        for i in range(len(self.wonders)):
            is_valid, error = self.wonders[i].validate_selection(self.wonders, self.hands[i], selections[i])
            if not is_valid:
                raise Exception(f"Error for {self.wonders[i].name}: {error}")
        # Perform
        effects_for_process = [[] for wonder in self.wonders]
        for i in range(len(self.wonders)):
            self.execute_selection(i, selections[i], effects_for_process)
        
        for i in range(len(self.wonders)):
            self.execute_effects(self.wonders[i], effects_for_process[i])
        
        # Discard cards at end of age
        if len(self.hands[0]) == 1:
            for i in range(len(self.wonders)):
                if self.wonders[i].has_effect('play_last_card', ''):
                    print(f"{self.wonders[i].name} can play its last card")
                    self.wait_for_last_card_play = True
                else:
                    self.discard_pile.extend(self.hands[i])
                    self.hands[i].clear()

        if not self.wait_for_last_card_play and not self.wait_for_discard_play:
            self.process_end_of_turn()

    def execute_last_card_turn(self, selection):
        # Validate
        if not self.age_initialized:
            raise Exception("Age is not initialized")
        if not self.wait_for_last_card_play:
            raise Exception("Cannot play last card now")
        for i in range(len(self.wonders)):
            if not self.wonders[i].has_effect('play_last_card'):
                continue
            is_valid, error = self.wonders[i].validate_selection(self.wonders, self.hands[i], selection)
            if not is_valid:
                raise Exception(f"Error for {self.wonders[i].name}: {error}")
            effects_for_process = [[] for wonder in self.wonders]
            self.execute_selection(i, selection, effects_for_process)
            self.execute_effects(self.wonders[i], effects_for_process[i])
            break
        self.wait_for_last_card_play = False
        if not self.wait_for_discard_play:
            self.process_end_of_turn()
    
    def execute_discard_turn(self, card):
        # Validate
        if not self.age_initialized:
            raise Exception("Age is not initialized")
        if not self.wait_for_discard_play:
            raise Exception("Cannot build from the discard now")
        if self.wait_for_last_card_play:
            raise Exception("Cannot build from the discard, waiting for Babylon to play last card")
        for i in range(len(self.wonders)):
            if not self.wonders[i].has_effect('build_from_discard'):
                continue
            if card in self.wonders[i].played_cards:
                raise Exception(f"Cannot build card {card.name} from discard since it is already in the player's wonder")
            if not card:
                print(f"{self.wonders[i].name} has decided not to play a card from the discard")
                break
            self.wonders[i].played_cards.append(card)
            self.execute_effects(self.wonders[i], card.effects)
            self.discard_pile.remove(card)
            print(f"{self.wonders[i].name} plays {card.name}")
            break
        self.wait_for_discard_play = False
        self.process_end_of_turn()

    def process_end_of_turn(self):
        # End of age?
        if len(self.hands[0]) == 0:
            for wonder in self.wonders:
                neg_wonder = self.get_neg_neighbor(wonder)
                wonder_shields = wonder.get_shields()
                neg_wonder_shields = neg_wonder.get_shields()
                
                if wonder_shields == neg_wonder_shields:
                    print(f"{neg_wonder.name} and {wonder.name} tie on military with {wonder_shields} shields each")
                elif wonder_shields > neg_wonder_shields:
                    print(f"{wonder.name} defeats {neg_wonder.name}, {wonder_shields} shields to {neg_wonder_shields}")
                    wonder.military_tokens.append({ 1: 1, 2: 3, 3: 5 }[self.age])
                    neg_wonder.military_tokens.append(-1)
                else:
                    print(f"{neg_wonder.name} defeats {wonder.name}, {neg_wonder_shields} shields to {wonder_shields}")
                    neg_wonder.military_tokens.append({ 1: 1, 2: 3, 3: 5 }[self.age])
                    wonder.military_tokens.append(-1)
            self.age_initialized = False
        else:
            if self.age % 2 == 0:
                self.hands.append(self.hands.pop(0))  # Rotate neg in age 2
            else:
                self.hands.insert(0, self.hands.pop())  # Rotate pos in age 1,3

    def execute_selection(self, i, selection, effects_for_process):
        hand, wonder = self.hands[i], self.wonders[i]
        wonder.play_selection(self.wonders, selection, apply_immediate_effects=False)
        if selection.action == 'play':
            self.execute_payment(wonder, selection.payment)
            effects_for_process[i] = selection.card.effects
            print(f"{wonder.name} plays {selection.card.name}")
        if selection.action == 'wonder':
            self.execute_payment(wonder, selection.payment)
            effects_for_process[i] = wonder.get_last_built_stage().effects
            print(f"{wonder.name} buries {selection.card.name} to build wonder stage {wonder.stages_built}")
        if selection.action == 'throw':
            self.discard_pile.append(selection.card)
            print(f"{wonder.name} throws {selection.card.name} for 3 gold")
        hand.remove(selection.card)

    def execute_effects(self, wonder, effects):
        previous_gold = wonder.gold
        wonder.apply_immediate_effects(self.wonders, effects)

        gold_gain = wonder.gold - previous_gold
        if wonder.gold != previous_gold:
            print(f"{wonder.name} gains {wonder.gold - previous_gold} gold")
        if any(e.type == 'build_from_discard' for e in effects):
            print(f"{wonder.name} can build a card from the discard pile")
            self.wait_for_discard_play = True

    def execute_payment(self, wonder, payment):
        if payment:
            neg_neighbor, pos_neighbor = wonder.get_neighbors(self.wonders)
            neg_neighbor.gold += payment.neg
            pos_neighbor.gold += payment.pos
            pm = []
            if payment.neg > 0:
                pm.append(f"{payment.neg} to {self.get_neg_neighbor(wonder).name}")
            if payment.pos > 0:
                pm.append(f"{payment.pos} to {self.get_pos_neighbor(wonder).name}")
            if payment.bank > 0:
                pm.append(f"{payment.bank} to the bank")
            
            if payment.total() > 0:
                print(f"{wonder.name} pays: {', '.join(pm)}")

    def get_pos_neighbor(self, wonder):
        return self.wonders[(self.wonders.index(wonder) + 1) % len(self.wonders)]
    
    def get_neg_neighbor(self, wonder):
        return self.wonders[(self.wonders.index(wonder) - 1) % len(self.wonders)]

    def get_total_score(self):
        return sum(sum(wonder.compute_points_distribution(self.wonders).values()) for wonder in self.wonders)

    def get_points_str(self, wonder):
        distr = wonder.compute_points_distribution(self.wonders)
        return f"{distr.get('military', 0)}/{distr.get('gold', 0)}/{distr.get('points', 0)}/{distr.get('science', 0)}/{distr.get('yellow', 0)}/{distr.get('guild', 0)}/{sum(distr.values())}"

    def __repr__(self):
        points = [self.get_points_str(wonder) for wonder in self.wonders]
        wonders = '\n'.join([f"Wonder: {self.wonders[i]}, Points: {points[i]}, Hand: {[card.name for card in self.hands[i]]}" for i in range(len(self.wonders))])
        discard = f"Discarded cards: {len(self.discard_pile)}"
        return f"{wonders}\n{discard}"
