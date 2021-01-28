from selenium import webdriver
from webdriver.common import *
from game.ai_game import *

class AiSession:
    def __init__(self, driver, user, pw, ai):
        self.driver = driver
        self.name = user
        self.game_info = None
        self.game_state = WAITING
        self.ai = ai
        self.ai_game = AiGame(0)

        log_in(self.driver, user, pw)
        attempt_rejoin(self.driver)
    
    def attempt_rejoin(self):
        attempt_rejoin(self.driver)
    
    def start_ai(self):
        self.game_info = get_game_info(self.driver)
        toggle_sound(self.driver)
    
    def choose_side(self, side):
        ai_id = self.game_info.players[0].id
        choose_side(self.driver, ai_id, side)

    def set_state(self):
        self.game_state = get_game_state(self.driver)
    
    def select(self):
        self.game_info = get_game_info(self.driver)
        self.set_state()

        self.driver.implicitly_wait(0)
        wonders = get_wonders(self.driver, self.game_info)
        self.driver.implicitly_wait(2)

        if self.game_state == WAITING or self.game_state == DONE:
            return None

        if self.game_state == PLAY_NORMAL or self.game_state == PLAY_LAST_CARD:
            hand = read_hand(self.driver, self.game_info)
            old_age = self.game_info.age
            set_age(self.driver, self.game_info, wonders)
            if not self.ai_game.initialized or self.game_info.age != old_age:
                self.ai_game.initialize(self.game_info.age, wonders, hand)
            else:
                move = read_last_move(self.driver, self.game_info)
                self.ai_game.post_move(wonders, move, hand)

            return self.ai.get_selection(self.ai_game, hand)

        if self.game_state == PLAY_DISCARD:
            hand = read_hand(self.driver, self.game_info)
            old_age = self.game_info.age
            set_age(self.driver, self.game_info, wonders)
            if not self.ai_game.initialized or self.game_info.age != old_age:
                self.ai_game.initialize(self.game_info.age, wonders, hand)
            discard = read_discard(self.driver, self.game_info)

            card = self.ai.get_build_card_from_discard(self.ai_game, [info.card for info in discard])
            return Selection(card, 'play', None)

    def act(self, selection):
        if self.game_state == PLAY_NORMAL or self.game_state == PLAY_LAST_CARD:
            play_selection(self.driver, self.game_info, self.ai_game.wonders, selection)
            self.game_state = WAITING
        elif self.game_state == PLAY_DISCARD:
            play_from_discard(self.driver, self.game_info, selection.card)
            self.game_state = WAITING
        

        
        