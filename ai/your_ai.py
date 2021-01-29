from game.deck import *
from game.base import *

from random import choice

# Use this as a template to construct your AI!
# Currently this AI greedily picks the card/wonder that gives it the most points.
#
# Some useful methods:
# - AI's wonder                         : ai_game.get_ai_wonder()
# - AI's hand                           : ai_game.get_ai_hand()
# - All wonders                         : ai_game.wonders
# - All hands                           : ai_game.hands
# - Current age                         : ai_game.age
# - All cards in age deck               : get_cards_for_players_age(player_count, age)
# - All possible moves                  : wonder.get_all_possible_moves(wonders, hand)
# - Validate selection                  : wonder.validate_selection(wonders, hand, selection)
# - Get Payment with min total          : wonder.get_min_gold_payment(wonders, hand, selection)
# - Get all Payment options             : wonder.get_all_payment_plans(wonders, hand, selection)
# - New wonder with selection performed : wonder.with_simulated_selection(wonders, selection)
# - Total points                        : wonder.compute_points_total()
# - Check if wonder has an effect       : wonder.has_effect(effect_type[, effect_subtype])
# - All resources                       : wonder.get_resources()
# - All purchasable resources           : wonder.get_purchasable_resources()
# - Full list of resources produced     : wonder.get_all_resources_produced()
# - All cards of a color                : wonder.get_cards_by_color(color)
# - Latest-build stage                  : wonder.get_last_built_stage()
# - Next free stage                     : wonder.get_next_free_stage()
# - Total shield count                  : wonder.get_shields()
# - Has a specific chain                : wonder.has_chain(chain)


# Compute the point gain of the move.
def points_for_move(wonders, wonder, move):
    old_points = wonder.compute_points_total(wonders)
    new_points = wonder.with_simulated_selection(wonders, move).compute_points_total(wonders)
    return new_points - old_points

class YourAi:
    # Required method. Return a Selection representing the move the AI will make.
    def get_selection(self, ai_game, cards):
        wonder = ai_game.get_ai_wonder()
        wonders = ai_game.wonders

        # Get all possible moves as Selections. All selections will come pre-filled with the lowest valid gold payment.
        possible_moves = wonder.get_all_possible_moves(ai_game.wonders, cards)
        print('Possible moves:', possible_moves)

        # Select the move that gives the highest points.
        possible_moves.sort(key=lambda move: points_for_move(wonders, wonder, move), reverse=True)
        best_move = possible_moves[0]
        
        # If the move is to build a wonder stage or throw, randomly choose a card from the hand to use.
        if move.action in ['wonder', 'throw']:
            move = Selection(choice(cards), move.action, move.payment)
        
        print('AI wants to:', move)

        return move
    
    # Required method. Return a Card represting the card the AI will play from the discard pile.
    def get_build_card_from_discard(self, ai_game, cards):
        wonder = ai_game.get_ai_wonder()

        # Get all possible Cards to play.
        possible_cards = [card for card in cards if card not in wonder.played_cards]
        print('Possible discard cards:', [card.name for card in possible_cards])

        # Returning None skips the discard play.
        if len(possible_cards) == 0:
            return None

        # Select the card that gives the highest points.
        possible_cards.sort(key=lambda card: points_for_move(wonders, wonder, Selection(card, 'play', None)), reverse=True)
        best_card = possible_cards[0]

        print('AI wants to play from discard:', card.name)

        return card