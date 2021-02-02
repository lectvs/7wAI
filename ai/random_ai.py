from game.base import *

from random import choice

# An AI which makes random choices from the list of possible moves.
class RandomAi:
    def get_selection(self, ai_game, cards):
        wonder = ai_game.get_ai_wonder()
        possible_selections = wonder.get_all_possible_selections(ai_game.wonders, cards)

        #print(possible_selections)

        # To make the AI a bit more interesting, remove the 'throw' move if there are other valid moves.
        if len(possible_selections) > 1:
            possible_selections.pop()

        selection = choice(possible_selections)

        # If the move is to build a wonder stage or throw, randomly choose a card from the hand to use.
        if selection.action in ['wonder', 'throw']:
            selection = Selection(choice(cards), selection.action, selection.payment)
        
        # print('AI wants to:', selection)

        return selection
    
    def get_build_card_from_discard(self, ai_game, cards):
        wonder = ai_game.get_ai_wonder()
        possible_cards = [card for card in cards if card not in wonder.played_cards]

        # print([card.name for card in possible_cards])

        # Returning None skips the discard play.
        if len(possible_cards) == 0:
            # print(f"No possible cards in the discard: {cards}")
            return None
        
        card = choice(possible_cards)

        # print('AI wants to play from discard:', card.name)

        return card
    
    def get_wonder_side(self, wonder_names):
        return choice(['Day', 'Night'])