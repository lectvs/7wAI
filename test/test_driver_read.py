from game.deck import *
from game.ai_game import *
from ai.random_ai import RandomAi
from webdriver.common import *
from selenium import webdriver
from time import sleep

# Tests read functionality on BGA. This file is old and probably doesn't work anymore.

driver = webdriver.Firefox()
driver.implicitly_wait(10)

log_in(driver, 'iluaergkskgyuksb', 'testtest')

go_to_replay(driver, table_id=136822126, player_id=87684192)

game_info = get_game_info(driver)
last_logs = 0

ai = RandomAi()
ai_game = AiGame(0)

while True:
    while 'You' not in driver.find_element_by_id('pagemaintitletext').text:
        sleep(0.1)

    get_game_state(driver)

    if 'You must choose a card to play' in driver.find_element_by_id('pagemaintitletext').text or 'You may play your last card' in driver.find_element_by_id('pagemaintitletext').text:
        driver.implicitly_wait(0)
        wonders = get_wonders(driver, game_info)
        driver.implicitly_wait(10)

        hand = read_hand(driver, game_info)
        if not ai_game.initialized:
            set_age(driver, game_info, wonders)
            ai_game.initialize(game_info.age, wonders, hand)
        else:
            move = read_last_move(driver, game_info)
            ai_game.post_move(wonders, move, hand)
        print()
        print(ai_game)
        print()
        print('ai wants to:', ai.get_selection(ai_game, hand))
    elif 'You may construct a card from the discard pile for free' in driver.find_element_by_id('pagemaintitletext').text:
        discard = read_discard(driver, game_info)

        print()
        print('ai wants to build from discard:', ai.get_build_card_from_discard(ai_game, [info.card for info in discard]))

    while 'You' in driver.find_element_by_id('pagemaintitletext').text:
        sleep(0.1)
    
    while 'You' not in driver.find_element_by_id('pagemaintitletext').text:
        sleep(0.1)
    
    sleep(2)

    while len(driver.find_elements_by_css_selector('#logs > [id^=log_]')) <= last_logs:
        sleep(0.1)
    last_logs = len(driver.find_elements_by_css_selector('#logs > [id^=log_]'))

    while True:
        old_hand = hand
        hand = driver.find_elements_by_css_selector('#player_hand > div > div')
        if len(hand) == 7 or len(hand) < len(old_hand):
            break
        sleep(0.1)

