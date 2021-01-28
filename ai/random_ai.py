from game.base import *

from random import choice

# An AI which makes random choices from the list of possible moves.
class RandomAi:
    def get_selection(self, ai_game, cards):
        ai_info = ai_game.get_ai_info()
        possible_moves = ai_info.wonder.get_all_possible_moves(ai_game.wonders, cards)

        #print(possible_moves)

        # To make the AI a bit more interesting, remove the 'throw' move if there are other valid moves.
        if len(possible_moves) > 1:
            possible_moves.pop()

        move = choice(possible_moves)

        # If the move is to build a wonder stage or throw, randomly choose a card from the hand to use.
        if move.action in ['wonder', 'throw']:
            move = Selection(choice(cards), move.action, move.payment)
        
        print('AI wants to:', move)

        return move
    
    def get_build_card_from_discard(self, ai_game, cards):
        ai_info = ai_game.get_ai_info()
        possible_cards = [card for card in cards if card not in ai_info.wonder.played_cards]

        #print([card.name for card in possible_cards])

        # Returning None skips the discard play.
        if len(possible_cards) == 0:
            print(f"No possible cards in the discard: {cards}")
            return None
        
        card = choice(possible_cards)

        print('AI wants to play from discard:', card.name)

        return card