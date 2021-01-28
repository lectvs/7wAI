from collections import namedtuple

from game.base import *

Hand = namedtuple('Hand', ['known_cards'])
AiInfo = namedtuple('AiInfo', ['wonder', 'neg_neighbor', 'pos_neighbor'])

class AiGame:
    def __init__(self, i):
        self.i = i
        self.age = 1
        self.hands = []
        self.wonders = []
        self.initialized = False

    def get_ai_info(self):
        neg_neighbor, pos_neighbor = self.wonders[self.i].get_neighbors(self.wonders)
        return AiInfo(self.wonders[self.i], neg_neighbor, pos_neighbor)

    def get_ai_hand(self):
        return self.hands[self.i].known_cards

    def initialize(self, age, wonders, cards):
        self.age = age
        self.wonders = wonders
        self.hands = []
        for i in range(len(self.wonders)):
            self.hands.append(Hand(cards[:]) if i == self.i else Hand([]))
        self.initialized = True

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

    def pre_last_card_play(self, wonders, cards):
        self.hands[self.i] = Hand(cards[:])

    def get_points_str(self, wonder):
        distr = wonder.compute_points_distribution(self.wonders)
        return f"{distr.get('military', 0)}/{distr.get('gold', 0)}/{distr.get('points', 0)}/{distr.get('science', 0)}/{distr.get('yellow', 0)}/{distr.get('guild', 0)}/{sum(distr.values())}"

    def __repr__(self):
        points = [self.get_points_str(wonder) for wonder in self.wonders]
        wonders = '\n'.join([f"Wonder: {self.wonders[i]}, Points: {points[i]}, Known Hand: {[card.name for card in self.hands[i].known_cards]}" for i in range(len(self.wonders))])
        return f"{wonders}"
        