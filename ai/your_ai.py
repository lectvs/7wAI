from game.deck import *
from game.base import *

from random import choice

# Use this as a template to construct your AI!
# Currently this AI greedily picks the card/wonder that gives it the most points.
#
# Most of the structs used 
#
# Some useful methods:
# - AI's wonder                         : ai_game.get_ai_wonder() -> Wonder
# - AI's hand                           : ai_game.get_ai_hand() -> Card[]
# - All wonders                         : ai_game.wonders -> Wonder[]
# - All hands                           : ai_game.hands -> Card[][]
# - Current age                         : ai_game.age -> number
# - All cards in age deck               : get_cards_for_players_age(player_count, age) -> Card[]
# - All possible moves                  : wonder.get_all_possible_selections(wonders, hand) -> Selection[]
# - Validate selection                  : wonder.validate_selection(wonders, hand, selection) -> (bool, string)
# - Get Payment with min total          : wonder.get_min_gold_payment(wonders, hand, selection) -> Payment
# - Get all Payment options             : wonder.get_all_payment_plans(wonders, hand, selection) -> Payment[]
# - New wonder with selection performed : wonder.with_simulated_selection(wonders, selection) -> Wonder
# - Total points                        : wonder.compute_points_total() -> number
# - Check if wonder has an effect       : wonder.has_effect(effect_type[, effect_subtype]) -> bool
# - All resources                       : wonder.get_resources() -> (string[], string[])
# - All purchasable resources           : wonder.get_purchasable_resources() -> (string[], string[])
# - Full list of resources produced     : wonder.get_all_resources_produced() -> string[]
# - All cards of a color                : wonder.get_cards_by_color(color) -> Card[]
# - Latest-build stage                  : wonder.get_last_built_stage() -> WonderStage
# - Next free stage                     : wonder.get_next_free_stage() -> WonderStage
# - Total shield count                  : wonder.get_shields() -> number
# - Has a specific chain                : wonder.has_chain(chain) -> bool


# Compute the point gain of the move.
def points_for_selection(wonders, wonder, selection):
    old_points = wonder.compute_points_total(wonders)
    new_points = wonder.with_simulated_selection(wonders, selection).compute_points_total(wonders)
    return new_points - old_points

class YourAi:
    # Required method. Return a Selection representing the move the AI will make.
    def get_selection(self, ai_game, cards):
        wonder = ai_game.get_ai_wonder()
        wonders = ai_game.wonders

        # Get all possible moves as Selections. All selections will come pre-filled with the lowest valid gold payment.
        possible_selections = wonder.get_all_possible_selections(ai_game.wonders, cards)
        print('Possible moves:', possible_selections)

        # Select the move that gives the highest points.
        possible_selections.sort(key=lambda selection: points_for_selection(wonders, wonder, selection), reverse=True)
        best_selection = possible_selections[0]
        
        # If the move is to build a wonder stage or throw, randomly choose a card from the hand to use.
        if best_selection.action in ['wonder', 'throw']:
            best_selection = Selection(choice(cards), best_selection.action, best_selection.payment)
        
        print('AI wants to:', best_selection)

        return best_selection
    
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
        possible_cards.sort(key=lambda card: points_for_selection(wonders, wonder, Selection(card, 'play', None)), reverse=True)
        best_card = possible_cards[0]

        print('AI wants to play from discard:', best_card.name)

        return best_card
    
    # Required method. Return 'Day' or 'Night' to choose your wonder side.
    # Provided is a list of all wonder names, in turn order. Your wonder is always index 0 in this list.
    def get_wonder_side(self, wonder_names):
        my_wonder_name = wonder_names[0]
        neg_neighbor_wonder_name = wonder_names[-1]
        pos_neighbor_wonder_name = wonder_names[1]
        
        # Example: always play Night side on Alexandria and Ephesos, Day otherwise.
        if my_wonder_name in ['Alexandria', 'Ephesos']:
            return 'Night'
        return 'Day'