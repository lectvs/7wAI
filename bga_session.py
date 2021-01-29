import traceback
from concurrent.futures.thread import ThreadPoolExecutor

from users import USERS
from session.ai_session import AiSession
from game.ai_game import *
from ai.random_ai import RandomAi
from ai.first_ai import FirstAi
from webdriver.common import *
from selenium import webdriver
from time import sleep
from random import uniform, choice

# Runs a full session on BGA.
# Prerequisites:
# - Install Selenium: https://selenium-python.readthedocs.io/installation.html#downloading-python-bindings-for-selenium
# - Download the Firefox webdriver and add it to your PATH: https://selenium-python.readthedocs.io/installation.html#drivers
# Steps:
# - 1. Configure all users to log in in users.py
# - 2. Configure manual_mode and ai to your liking
# - 3. Run `python bga_session.py`
# - 4. Navigate to the game on BGA until you are in-game (i.e. you can see your wonder board)
# - 5. Press enter in console to start the AI
# - 6. If manual_mode is True, press enter on each turn to perform the action.

players = USERS
manual_mode = False
ai = FirstAi()

def create_session(player):
    options = webdriver.FirefoxOptions()
    options.add_argument("--width=780")
    options.add_argument("--height=1000")
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(2)
    return AiSession(driver, player[0], player[1], ai)

executor = ThreadPoolExecutor(len(players))
sessions = list(executor.map(create_session, players))

input('Enter to start AI')
for session in sessions:
    session.start_ai()
    session.set_state()
    if session.game_state == CHOOSE_SIDE:
        session.choose_side()
        sleep(0.5)

while any(session.game_state != DONE for session in sessions):
    print('Waiting for next move...')
    while all(session.game_state in [WAITING, DONE] for session in sessions):
        if all(session.game_state == DONE for session in sessions):
            break
        for session in sessions:
            session.set_state()
        sleep(0.5)
    
    sleep(uniform(0, 1))

    try:
        selections = [session.select() for session in sessions]
    except Exception:
        traceback.print_exc()
        selections = [None for session in sessions]

    print()
    print(sessions[0].ai_game)
    print()

    for session, selection in zip(sessions, selections):
        if selection:
            print(session.name, 'will:', selection)

    if manual_mode:
        print()
        input('Enter to continue')

    for session, selection in zip(sessions, selections):
        try:
            session.act(selection)
        except Exception:
            traceback.print_exc()
            continue
        sleep(0.5)

print()
print('Game is done')
