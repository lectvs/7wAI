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


players = USERS
manual_mode = True

def create_session(player):
    options = webdriver.FirefoxOptions()
    options.add_argument("--width=780")
    options.add_argument("--height=1000")
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(2)
    return AiSession(driver, player[0], player[1], FirstAi())

executor = ThreadPoolExecutor(len(players))
sessions = list(executor.map(create_session, players))

input('Enter to start AI')
for session in sessions:
    session.start_ai()
    session.set_state()
    if session.game_state == CHOOSE_SIDE:
        session.choose_side(choice(['Day', 'Night']))
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
