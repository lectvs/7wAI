from game.base import *

# Simulates a 7 Wonders game locally.
# - wonders: a list of Wonders in this game
# - hands: a list of Card lists representing each player's hand
# - discard_pile: a list of all Cards in the discard pile
# - age: the age of the game (1, 2, 3)
# - age_initialized: describes if the age has been initialized
# - wait_for_last_card_play: describes if we are waiting for Babylon to play its last card
# - wait_for_discard_play: describes if we are waiting for Halikarnassos to build from the discard
class KnownGame:
    def __init__(self, wonders):
        self.wonders = wonders
        self.hands = [[] for wonder in wonders]
        self.discard_pile = []
        self.age = 1
        self.age_initialized = False
        self.wait_for_last_card_play = False
        self.wait_for_discard_play = False

    # Initializes the age with the given hands dealt to players.
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

    # Executes a turn with all selections provided.
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
        # Perform turn
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

        # Only process the end of the turn after last-card-play/discard-play.
        if not self.wait_for_last_card_play and not self.wait_for_discard_play:
            self.process_end_of_turn()

    # Executes Babylon's last card turn with the provided Selection.
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
    
    # Executes Halikarnassos' discard play with the provided Card.
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

    # Process end of turn, including:
    # - Rotating hands around the table
    # - Resolving military post-age
    # - Ending each age
    def process_end_of_turn(self):
        # End of age?
        if len(self.hands[0]) == 0:
            for wonder in self.wonders:
                neg_wonder = wonder.get_neighbors(self.wonders)[0]
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

    # Helper for execute_turn
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

    # Helper for execute_turn
    def execute_effects(self, wonder, effects):
        previous_gold = wonder.gold
        wonder.apply_immediate_effects(self.wonders, effects)

        gold_gain = wonder.gold - previous_gold
        if wonder.gold != previous_gold:
            print(f"{wonder.name} gains {wonder.gold - previous_gold} gold")
        if any(e.type == 'build_from_discard' for e in effects):
            print(f"{wonder.name} can build a card from the discard pile")
            self.wait_for_discard_play = True

    # Helper for execute_selection
    def execute_payment(self, wonder, payment):
        if payment:
            neg_neighbor, pos_neighbor = wonder.get_neighbors(self.wonders)
            neg_neighbor.gold += payment.neg
            pos_neighbor.gold += payment.pos
            pm = []
            if payment.neg > 0:
                pm.append(f"{payment.neg} to {neg_neighbor.name}")
            if payment.pos > 0:
                pm.append(f"{payment.pos} to {pos_neighbor.name}")
            if payment.bank > 0:
                pm.append(f"{payment.bank} to the bank")
            
            if payment.total() > 0:
                print(f"{wonder.name} pays: {', '.join(pm)}")

    # Returns the current sum total score of all wonders in the game.
    def get_total_score(self):
        return sum(wonder.compute_points_total(self.wonders) for wonder in self.wonders)

    # Returns a representation of each wonder, points distribution, hands, and discard count on separate lines.
    def __repr__(self):
        points = [wonder.get_points_str(self.wonders) for wonder in self.wonders]
        wonders = '\n'.join([f"Wonder: {self.wonders[i]}, Points: {points[i]}, Hand: {[card.name for card in self.hands[i]]}" for i in range(len(self.wonders))])
        discard = f"Discarded cards: {len(self.discard_pile)}"
        return f"{wonders}\n{discard}"
