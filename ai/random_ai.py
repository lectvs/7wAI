from game.base import *

from random import choice

class RandomAi:
    def get_selection(self, ai_game, cards):
        ai_info = ai_game.get_ai_info()
        possible_moves = ai_info.wonder.get_all_possible_moves(ai_game.wonders, cards)

        #print(possible_moves)

        if len(possible_moves) > 1:
            possible_moves.pop()  # Remove throw

        move = choice(possible_moves)

        # todo: remove after testing wonders
        if ai_info.wonder.name != 'Halikarnassos' and any(sel.action == 'wonder' for sel in possible_moves):
            move = next(sel for sel in possible_moves if sel.action == 'wonder')
        if ai_info.wonder.name == 'Halikarnassos' and len(cards) == 2 and any(sel.action == 'wonder' for sel in possible_moves):
            move = next(sel for sel in possible_moves if sel.action == 'wonder')

        if move.action in ['wonder', 'throw']:
            move = Selection(choice(cards), move.action, move.payment)
        
        print('AI wants to:', move)

        return move
    
    def get_build_card_from_discard(self, ai_game, cards):
        ai_info = ai_game.get_ai_info()
        possible_cards = [card for card in cards if card not in ai_info.wonder.played_cards]

        #print([card.name for card in possible_cards])

        if len(possible_cards) == 0:
            print(f"No possible cards in the discard?: {cards}")
            return None
        
        card = choice(possible_cards)

        print('AI wants play from discard:', card.name)

        return card