import re, json

from game.base import *
from game.deck import *
from game.wonders import *
from time import sleep
from collections import namedtuple

# Represents a player on BGA.
# - id: the numeric id of the player
# - name: the username of the player
# - wonder: the numeric id of the wonder the player is controlling
PlayerInfo = namedtuple('PlayerInfo', ['id', 'name', 'wonder'])

# Represents a card from the discard pile selector on BGA.
# - discard_id: the numeric id of the card
# - img_index: the index of the card on the BGA master card image
# - card: the Card this discard card represents
DiscardCardInfo = namedtuple('DiscardCardInfo', ['discard_id', 'img_index', 'card'])

# Represents high-level info about the game.
# - players: the list of in-game players (in turn order). active user is always at index 0.
# - wonders_by_id: mapping of a wonders' BGA numeric ids to the Wonders they represent
# - cards_by_id: mapping of cards' BGA numeric ids to the Cards they represent
# - cards_by_img_index: mapping of cards' BGA image index to the Cards they represent
# - age: the current age of the game (1, 2, 3)
class GameInfo:
    def __init__(self, players, wonders_by_id, cards_by_id, cards_by_img_index, age):
        self.players = players
        self.wonders_by_id = wonders_by_id
        self.cards_by_id = cards_by_id
        self.cards_by_img_index = cards_by_img_index
        self.age = age

# Log in to BGA using the given username and password.
def log_in(driver, user, pw):
    driver.get('https://boardgamearena.com/')

    driver.find_element_by_id('connect_button').click()
    driver.find_element_by_id('username_input').send_keys(user)
    driver.find_element_by_id('password_input').send_keys(pw)
    driver.find_element_by_id('submit_login_button').click()

    while driver.current_url != 'https://boardgamearena.com/':
        sleep(1)

# Attempt to rejoin a game in progress if applicable.
def attempt_rejoin(driver):
    banner_links = driver.find_elements_by_css_selector('#current_table_banner a')
    if not banner_links or banner_links[0].text != '7 Wonders':
        return
    banner_links[0].click()
    sleep(1)
    go_to_link = driver.find_element_by_id('access_game_normal')
    if not go_to_link:
        return
    go_to_link.click()

# Go to and start a replay for the given table id, from the perspective of the given player_id.
def go_to_replay(driver, table_id, player_id):
    driver.get(f'https://en.boardgamearena.com/gamereview?table={table_id}')
    driver.find_element_by_id(f'choosePlayerLink_{player_id}').click()

    sleep(1)
    while 'You must choose a card to play' not in driver.find_element_by_id('pagemaintitletext').text:
        driver.find_element_by_id('archive_next').click()
        sleep(0.5)

# Go to the given table id.
def go_to_table(driver, table_id):
    driver.get(f'https://boardgamearena.com/table?table={table_id}')

# Accept an invite to a game if applicable.
def accept_invite(driver):
    driver.get('https://boardgamearena.com/')
    for e in driver.find_elements_by_css_selector('#expected_table_banners a'):
        if e.text == 'Accept':
            e.click()
            return

# Start the game as the host of a table.
def start_game(driver):
    while not driver.find_element_by_id('startgame').text.strip():
        sleep(0.1)
    driver.find_element_by_id('startgame').click()

# Toggle sound off while in-game.
def toggle_sound(driver):
    driver.find_element_by_id('toggleSound').click()

# Fetches all info in a GameInfo object from the BGA game.
def get_game_info(driver):
    player_data = driver.execute_script('return gameui.gamedatas.players')
    player_order_data = driver.execute_script('return gameui.gamedatas.playerorder')
    wonder_data = driver.execute_script('return gameui.gamedatas.wonders')
    card_data = driver.execute_script('return gameui.gamedatas.card_types')

    players = [PlayerInfo(str(pid), player_data[str(pid)]['name'], str(player_data[str(pid)]['wonder'])) for pid in player_order_data]
    wonders_by_id = {wid: get_wonder_by_bga_name_side(wonder_data[wid]['name'], 'Day' if int(wid) <= 7 else 'Night') for wid in wonder_data}
    cards_by_id = {cid: get_card_by_name(card_data[cid]['name']) for cid in card_data}
    cards_by_img_index = {str(card_data[cid]['img']): get_card_by_name(card_data[cid]['name']) for cid in card_data}

    return GameInfo(players, wonders_by_id, cards_by_id, cards_by_img_index, 1)

# Gets the current game state.
DONE = 'done'
CHOOSE_SIDE = 'choose_side'
WAITING = 'waiting'
PLAY_NORMAL = 'play_normal'
PLAY_LAST_CARD = 'play_last_card'
PLAY_DISCARD = 'play_discard'
def get_game_state(driver):
    if driver.execute_script('return gameui.gamedatas.gamestate.name') == 'gameEnd':
        return DONE
    title = driver.find_element_by_id('pagemaintitletext').text
    if 'You must choose a side of your Wonder board' in title:
        return CHOOSE_SIDE
    if 'You must choose a card to play' in title:
        return PLAY_NORMAL
    if 'You may play your last card' in title:
        return PLAY_LAST_CARD
    if 'You may construct a card from the discard pile for free' in title:
        return PLAY_DISCARD
    return WAITING

# Returns a best-guess of the current age of the game.
def get_age(driver, game_info, wonders):
    age_from_game_info = len(driver.execute_script('let args = gameui.gamedatas.gamestate.args; return args ? args.age : ""') or "")
    if age_from_game_info > 0:
        return age_from_game_info
    if wonders:
        max_age_from_cards = 0
        age_1_cards = get_cards_for_players_age(len(game_info.players), 1)
        age_2_cards = get_cards_for_players_age(len(game_info.players), 2)
        age_3_cards = get_cards_for_players_age(len(game_info.players), 3)
        for wonder in wonders:
            for card in wonder.played_cards:
                card_age = 0
                if card in age_1_cards:
                    card_age = 1
                elif card in age_2_cards:
                    card_age = 2
                elif card in age_3_cards:
                    card_age = 3
                if card_age > max_age_from_cards:
                    max_age_from_cards = card_age
        if max_age_from_cards > 0:
            return max_age_from_cards
    return 1

# Sets the age of the game on the GameInfo.
def set_age(driver, game_info, wonders):
    game_info.age = get_age(driver, game_info, wonders)

# Choose the wonder side.
def choose_side(driver, pid, side):
        side = {'Day': 'a', 'Night': 'b'}[side]
        driver.find_element_by_id(f'wonder_face_{pid}_{side}').click()

# Reads the Wonders from BGA along with everything associated with them (military tokens, played cards, etc.)
def get_wonders(driver, game_info):
    board_elements = [driver.find_element_by_id(f'player_board_wrap_{p.id}') for p in game_info.players]
    military_tokens_data = driver.execute_script('let res = {}; for (let key in gameui.victoryStock) { res[key] = gameui.victoryStock[key].items.map(i => parseInt(i.type)) }; return res')
    wonders = [None for player in game_info.players]
    for i in range(len(game_info.players)):
        e, player = board_elements[i], game_info.players[i]
        wonder = game_info.wonders_by_id[player.wonder]()
        wonder.gold = int(e.find_element_by_id(f'coin_{player.id}').text)
        for card_element in e.find_elements_by_css_selector(f'#player_board_content_{player.id} [id^=board_item_wrap_]'):
            m = re.match(r'.*type_([0-9]+).*', card_element.get_attribute('class'))
            if not m:
                raise Exception('Failed to parse card')
            card = game_info.cards_by_id[m.group(1)]
            wonder.played_cards.append(card)
        wonder.stages_built = len(e.find_elements_by_css_selector(f'#wonder_step_built_{player.id} > div'))
        wonder.military_tokens = military_tokens_data[player.id]
        wonders[i] = wonder
    
    return wonders

# Read the current hand.
def read_hand(driver, game_info):
    card_elements = driver.find_elements_by_css_selector('#player_hand > div > div')
    cards = []
    for e in card_elements:
        m = re.match(r'.*type_([0-9]+).*', e.get_attribute('class'))
        if not m:
            raise Exception('Failed to parse card')
        card = game_info.cards_by_id[m.group(1)]
        cards.append(card)
    return cards

# Read the current discard pile.
def read_discard(driver, game_info):
    card_elements = driver.find_elements_by_css_selector('#discarded > [id^=discarded_item_]')
    cards = []
    for e in card_elements:
        discard_id = e.get_attribute('id').split('_')[-1]
        bg_pos = e.value_of_css_property('background-position')
        m = re.match(r'^(.+)% (.+)%$', bg_pos)
        if not m:
            raise Exception('Failed to parse discard card')
        img_index = str(-(int(m.group(1)) + 10*int(m.group(2))) // 100)
        card = game_info.cards_by_img_index[img_index]
        cards.append(DiscardCardInfo(discard_id, img_index, card))
    return cards

# Read the last move for each player from the game logs (logs must be visible for reading to succeed).
def read_last_move(driver, game_info):
    move = [None for player in game_info.players]
    logs = [e.text.split('\n')[0].strip() for e in driver.find_elements_by_css_selector('#logs > div[id^=log_]')]
    for i in range(len(game_info.players)):
        player = game_info.players[i]
        for log in logs:
            m = re.match(r'^(.+) gains 3 coins from discarding a card$', log)
            if m and m.group(1) == player.name:
                move[i] = Selection(None, 'throw', None)
                break
            m = re.match(r'^(.+) constructs a stage of their Wonder.*$', log)
            if m and m.group(1) == player.name:
                move[i] = Selection(None, 'wonder', None)
                break
            m = re.match(r'^(.+) constructs (.+)$', log)
            if m and m.group(1) == player.name:
                card_name = m.group(2).split(' for')[0].split(' (chained')[0]
                move[i] = Selection(get_card_by_name(card_name), 'play', None)
                break
    return move

# Play the given Selection on BGA.
def play_selection(driver, game_info, wonders, selection):
    if not selection.card:
        raise Exception('Selection must contain a card')
    card_id = next((cid for cid in game_info.cards_by_id if game_info.cards_by_id[cid] == selection.card), None)
    set_age(driver, game_info, wonders)
    if card_id == "11" and game_info.age == 2: card_id = "32"
    if card_id == "12" and game_info.age == 2: card_id = "33"
    if card_id == "13" and game_info.age == 2: card_id = "34"
    if not card_id:
        raise Exception('Could not find id for selected card')
    card_element = driver.find_element_by_css_selector(f'.cardcontent.cardtype_{card_id}')
    if not card_element:
        raise Exception('Could not find card element for selected card')
    
    if selection.action == 'throw':
        e = card_element.find_element_by_css_selector('.menulinks > [id^=menudiscard_]')
        driver.execute_script('arguments[0].click()', e)
    else:
        if selection.action == 'play':
            selector = '.menulinks > [id^=menuplay_]'
        elif selection.action == 'wonder':
            selector = '.menulinks > [id^=menuwond_]'
        else:
            raise Exception(f"Action not supported: {selection.action}")

        e = card_element.find_element_by_css_selector(selector)
        driver.execute_script('arguments[0].click()', e)

        if selection.payment.neg + selection.payment.pos == 0:
            return

        sleep(1)
        payment_list = driver.find_element_by_id('payment_list')
        if not payment_list.text.strip():
            return

        payment = selection.payment or Payment(0, 0, 0)
        for pp in payment_list.find_elements_by_css_selector('#paymentpossibilities > [id^=paymentpossibility_]'):
            pnegtext = pp.find_element_by_css_selector('.possibilityleft').text
            ppostext = pp.find_element_by_css_selector('.possibilityright').text
            pneg = 0
            ppos = 0
            m = re.match(r'^← ([0-9]+) to .+$', pnegtext)
            pneg = int(m.group(1)) if m else 0
            m = re.match(r'^to .+ ([0-9]+) →$', ppostext)
            ppos = int(m.group(1)) if m else 0
            if payment.neg == pneg and payment.pos == ppos:
                button = pp.find_element_by_css_selector('.possibilitybutton > a')
                driver.execute_script('arguments[0].click()', button)
                return
        
        raise Exception(f'No matching payment options for {selection}')

# Play the given Card from the discard on BGA.
def play_from_discard(driver, game_info, card):
    if not card:
        driver.find_element_by_id('dontpick').click()
        return
    card_info = next((info for info in read_discard(driver, game_info) if info.card == card), None)
    if not card_info:
        raise Exception(f'Could not find card {card.name} in the discard')
    card_element = driver.find_element_by_css_selector(f'#discarded > [id^=discarded_item_{card_info.discard_id}]')
    if not card_element:
        raise Exception('Could not find discard card element for selected card')
    card_element.click()
    