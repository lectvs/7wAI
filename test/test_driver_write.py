import re

from game.base import *
from game.deck import *
from game.ai_game import *
from ai.random_ai import RandomAi
from webdriver.common import *
from selenium import webdriver
from time import sleep

driver = webdriver.Firefox()
driver.implicitly_wait(10)

log_in(driver, 'iluaergkskgyuksb', 'testtest')

go_to_game(driver, table_id=140257071)

game_info = get_game_info(driver)

while True:
    input_move = input("Move: ")
    m = re.match(r'^([^\s]+) (.+) \(([0-9]+),\s*([0-9]+),\s*([0-9]+)\)$', input_move)
    if m:
        action = m.group(1)
        card_name = m.group(2)
        payment = Payment(int(m.group(3)), int(m.group(4)), int(m.group(5)))
    else:
        m = re.match(r'^([^\s]+) (.+)$', input_move)
        if m:
            action = m.group(1)
            card_name = m.group(2)
            payment = None
        else:
            print('Invalid input:', input_move)
            continue
    
    card = get_card_by_name(card_name)
    
    try:
        play_selection(driver, game_info, None, Selection(card, action, payment))
    except Exception as e:
        print(e)
