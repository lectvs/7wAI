from collections import namedtuple

from game.base import *

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
        self.debuggingMode = ''
        # '' for no debug output on get_selection
        # 'terse' for simple card/score debug output on get_selection
        # 'verbose' for full reasoning data debug output on get_selection

    # Returns the Wonder controlled by the AI.
    def get_ai_wonder(self):
        return self.wonders[self.i]

    # Returns the list of Cards in the AI's current hand.
    def get_ai_hand(self):
        return self.hands[self.i]

    def get_pass_to_neighbor(self):
        if self.age == 2:
            return self.wonders[(self.i - 1) % len(self.wonders)]
        else:
            return self.wonders[(self.i + 1) % len(self.wonders)]

    # Initializes this game state on entering the game and at the start of each age.
    def initialize(self, age, wonders, cards):
        self.age = age
        self.wonders = wonders
        self.hands = []
        for i in range(len(self.wonders)):
            self.hands.append(cards[:] if i == self.i else [])
        self.initialized = True

    # Runs after each regular move (non-discard play). Rotates and tracks hands as they move around the board.
    def post_move(self, wonders, selections, cards):
        self.wonders = wonders
        for i in range(len(self.wonders)):
            hand, selection = self.hands[i], selections[i]
            if not selection:
                continue
            if selection.action == 'play' and selection.card in hand:
                hand.remove(selection.card)
            if selection.action in ['wonder', 'throw'] and selection.card in hand and i == self.i:
                hand.remove(selection.card)
        if len(cards) > 1:
            if self.age % 2 == 0:
                self.hands.append(self.hands.pop(0))  # Rotate neg in age 2
            else:
                self.hands.insert(0, self.hands.pop())  # Rotate pos in age 1,3
        self.hands[self.i] = cards[:]

    # Called before Babylon's last card play to ensure Babylon knows what its last card is.
    def pre_last_card_play(self, wonders, cards):
        self.hands[self.i] = cards[:]

    # Returns a representation of each wonder, points distribution, and known hands on separate lines.
    def __repr__(self):
        points = [wonder.get_points_str(self.wonders) for wonder in self.wonders]
        wonders = '\n'.join([f"Wonder: {self.wonders[i]}\n    Points: {points[i]}\n    Known Hand: {[card.name for card in self.hands[i]]}" for i in range(len(self.wonders))])
        return f"{wonders}"
