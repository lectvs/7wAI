from collections import namedtuple

from game.base import *

# Everything the AI tracks about a hand as it moves around the table.
Hand = namedtuple('Hand', ['known_cards'])
# Convenience type containing the AI's wonder and its neighbors.
AiInfo = namedtuple('AiInfo', ['wonder', 'neg_neighbor', 'pos_neighbor'])

# Represents a partially-known game from a single player/AI's perspective.
# - i: the index of the AI's wonder/hand/etc.
# - age: the current age of the game (1, 2, 3)
# - hands: a list of Hands representing the tracked hand of each player
# - wonders: a list of Wonders in the game, in order
# - initialized: describes if the game has been initialized
class AiGame:
    def __init__(self, i):
        self.i = i
        self.age = 1
        self.hands = []
        self.wonders = []
        self.initialized = False

    # Returns in a tuple the AI's wonder, its negative neighbor, and its positive neighbor.
    def get_ai_info(self):
        neg_neighbor, pos_neighbor = self.wonders[self.i].get_neighbors(self.wonders)
        return AiInfo(self.wonders[self.i], neg_neighbor, pos_neighbor)

    # Returns the list of Cards in the AI's current hand.
    def get_ai_hand(self):
        return self.hands[self.i].known_cards

    # Initializes this game state on entering the game and at the start of each age.
    def initialize(self, age, wonders, cards):
        self.age = age
        self.wonders = wonders
        self.hands = []
        for i in range(len(self.wonders)):
            self.hands.append(Hand(cards[:]) if i == self.i else Hand([]))
        self.initialized = True

    # Runs after each regular move (non-discard play). Rotates and tracks hands as they move around the board.
    def post_move(self, wonders, selections, cards):
        self.wonders = wonders
        for i in range(len(self.wonders)):
            hand, selection = self.hands[i], selections[i]
            if not selection:
                continue
            if selection.action == 'play' and selection.card in hand.known_cards:
                hand.known_cards.remove(selection.card)
            if selection.action in ['wonder', 'throw'] and selection.card in hand.known_cards and i == self.i:
                hand.known_cards.remove(selection.card)
        if len(cards) > 1:
            if self.age % 2 == 0:
                self.hands.append(self.hands.pop(0))  # Rotate neg in age 2
            else:
                self.hands.insert(0, self.hands.pop())  # Rotate pos in age 1,3
        self.hands[self.i] = Hand(cards[:])

    # Called before Babylon's last card play to ensure Babylon knows what its last card is.
    def pre_last_card_play(self, wonders, cards):
        self.hands[self.i] = Hand(cards[:])

    # Returns a representation of each wonder, points distribution, and known hands on separate lines.
    def __repr__(self):
        points = [wonder.get_points_str(self.wonders) for wonder in self.wonders]
        wonders = '\n'.join([f"Wonder: {self.wonders[i]}, Points: {points[i]}, Known Hand: {[card.name for card in self.hands[i].known_cards]}" for i in range(len(self.wonders))])
        return f"{wonders}"
        