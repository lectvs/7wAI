from game.base import *

# This file contains all cards in the base 7 Wonders game, for all player counts.

# AGE 1
LUMBER_YARD = Card('Lumber Yard', 'brown', cost(), [Effect('resource', 'wood', 1)], [])
STONE_PIT = Card('Stone Pit', 'brown', cost(), [Effect('resource', 'stone', 1)], [])
CLAY_POOL = Card('Clay Pool', 'brown', cost(), [Effect('resource', 'clay', 1)], [])
ORE_VEIN = Card('Ore Vein', 'brown', cost(), [Effect('resource', 'ore', 1)], [])
TREE_FARM = Card('Tree Farm', 'brown', cost(gold=1), [Effect('multi_resource', 'wood/clay', 1)], [])
EXCAVATION = Card('Excavation', 'brown', cost(gold=1), [Effect('multi_resource', 'stone/clay', 1)], [])
CLAY_PIT = Card('Clay Pit', 'brown', cost(gold=1), [Effect('multi_resource', 'ore/clay', 1)], [])
TIMBER_YARD = Card('Timber Yard', 'brown', cost(gold=1), [Effect('multi_resource', 'wood/stone', 1)], [])
FOREST_CAVE = Card('Forest Cave', 'brown', cost(gold=1), [Effect('multi_resource', 'wood/ore', 1)], [])
MINE = Card('Mine', 'brown', cost(gold=1), [Effect('multi_resource', 'stone/ore', 1)], [])
GLASSWORKS = Card('Glassworks', 'grey', cost(), [Effect('resource', 'glass', 1)], [])
PRESS = Card('Press', 'grey', cost(), [Effect('resource', 'press', 1)], [])
LOOM = Card('Loom', 'grey', cost(), [Effect('resource', 'loom', 1)], [])
PAWNSHOP = Card('Pawnshop', 'blue', cost(), [Effect('points', '', 3)], ['hammer'])
BATHS = Card('Baths', 'blue', cost(stone=1), [Effect('points', '', 3)], ['waterdrop'])
ALTAR = Card('Altar', 'blue', cost(), [Effect('points', '', 3)], ['star'])
THEATER = Card('Theater', 'blue', cost(), [Effect('points', '', 3)], ['mask'])
TAVERN = Card('Tavern', 'yellow', cost(), [Effect('gold', '', 5)], [])
MARKETPLACE = Card('Marketplace', 'yellow', cost(), [Effect('marketplace', '', 1)], ['camel'])
WEST_TRADING_POST = Card('West Trading Post', 'yellow', cost(), [Effect('tradingpost', 'neg', 1)], ['market'])
EAST_TRADING_POST = Card('East Trading Post', 'yellow', cost(), [Effect('tradingpost', 'pos', 1)], ['market'])
STOCKADE = Card('Stockade', 'red', cost(wood=1), [Effect('shields', '', 1)], [])
BARRACKS = Card('Barracks', 'red', cost(ore=1), [Effect('shields', '', 1)], [])
GUARD_TOWER = Card('Guard Tower', 'red', cost(clay=1), [Effect('shields', '', 1)], [])
APOTHECARY = Card('Apothecary', 'green', cost(loom=1), [Effect('science', 'compass', 1)], ['horseshoe', 'bowl'])
WORKSHOP = Card('Workshop', 'green', cost(glass=1), [Effect('science', 'gear', 1)], ['target', 'lamp'])
SCRIPTORIUM = Card('Scriptorium', 'green', cost(press=1), [Effect('science', 'tablet', 1)], ['scales', 'book'])

# AGE 2
SAWMILL = Card('Sawmill', 'brown', cost(gold=1), [Effect('resource', 'wood', 1), Effect('resource', 'wood', 1)], [])
QUARRY = Card('Quarry', 'brown', cost(gold=1), [Effect('resource', 'stone', 1), Effect('resource', 'stone', 1)], [])
BRICKYARD = Card('Brickyard', 'brown', cost(gold=1), [Effect('resource', 'clay', 1), Effect('resource', 'clay', 1)], [])
FOUNDRY = Card('Foundry', 'brown', cost(gold=1), [Effect('resource', 'ore', 1), Effect('resource', 'ore', 1)], [])
STATUE = Card('Statue', 'blue', cost(ore=2, wood=1, chain='hammer'), [Effect('points', '', 4)], [])
AQUEDUCT = Card('Aqueduct', 'blue', cost(stone=3, chain='waterdrop'), [Effect('points', '', 5)], [])
TEMPLE = Card('Temple', 'blue', cost(wood=1, clay=1, glass=1), [Effect('points', '', 4)], [])
COURTHOUSE = Card('Courthouse', 'blue', cost(clay=2, loom=1, chain='scales'), [Effect('points', '', 4)], [])
CARAVANSERY = Card('Caravansery', 'yellow', cost(wood=2, chain='camel'), [Effect('multi_resource_unpurchasable', 'wood/stone/ore/clay', 1)], ['lighthouse'])
FORUM = Card('Forum', 'yellow', cost(clay=2, chain='market'), [Effect('multi_resource_unpurchasable', 'glass/press/loom', 1)], ['barrel'])
VINEYARD = Card('Vineyard', 'yellow', cost(), [Effect('gold_for_cards', 'brown', 1)], [])
BAZAAR = Card('Bazaar', 'yellow', cost(), [Effect('gold_for_cards', 'grey', 1)], [])
STABLES = Card('Stables', 'red', cost(wood=1, ore=1, clay=1, chain='horseshoe'), [Effect('shields', '', 2)], [])
ARCHERY_RANGE = Card('Archery Range', 'red', cost(wood=2, ore=1, chain='target'), [Effect('shields', '', 2)], [])
WALLS = Card('Walls', 'red', cost(stone=3), [Effect('shields', '', 2)], ['castle'])
TRAINING_GROUND = Card('Training Ground', 'red', cost(ore=2, wood=1), [Effect('shields', '', 2)], ['helmet'])
DISPENSARY = Card('Dispensary', 'green', cost(ore=2, glass=1, chain='bowl'), [Effect('science', 'compass', 1)], ['bolt', 'torch'])
LABORATORY = Card('Laboratory', 'green', cost(clay=2, press=1, chain='lamp'), [Effect('science', 'gear', 1)], ['saw', 'planets'])
LIBRARY = Card('Library', 'green', cost(stone=2, loom=1, chain='book'), [Effect('science', 'tablet', 1)], ['temple', 'scroll'])
SCHOOL = Card('School', 'green', cost(wood=1, press=1), [Effect('science', 'tablet', 1)], ['harp', 'feather'])

# AGE 3
PANTHEON = Card('Pantheon', 'blue', cost(clay=2, ore=1, glass=1, press=1, loom=1, chain='star'), [Effect('points', '', 7)], [])
GARDENS = Card('Gardens', 'blue', cost(clay=2, wood=1, chain='mask'), [Effect('points', '', 5)], [])
TOWN_HALL = Card('Town Hall', 'blue', cost(stone=2, ore=1, glass=1), [Effect('points', '', 6)], [])
PALACE = Card('Palace', 'blue', cost(wood=1, stone=1, ore=1, clay=1, glass=1, press=1, loom=1), [Effect('points', '', 8)], [])
SENATE = Card('Senate', 'blue', cost(wood=2, stone=1, ore=1, chain='temple'), [Effect('points', '', 6)], [])
LIGHTHOUSE = Card('Lighthouse', 'yellow', cost(stone=1, glass=1, chain='lighthouse'), [Effect('gold_and_points_for_cards', 'yellow', 1)], [])
HAVEN = Card('Haven', 'yellow', cost(wood=1, ore=1, loom=1, chain='barrel'), [Effect('gold_and_points_for_cards', 'brown', 1)], [])
CHAMBER_OF_COMMERCE = Card('Chamber of Commerce', 'yellow', cost(clay=2, press=1), [Effect('gold_and_points_for_cards', 'grey', 1)], [])
LUDUS = Card('Ludus', 'yellow', cost(stone=1, ore=1), [Effect('gold_and_points_for_cards', 'red', 1)], [])
ARENA = Card('Arena', 'yellow', cost(stone=2, ore=1, chain='bolt'), [Effect('gold_and_points_for_stages', '', 1)], [])
CASTRUM = Card('Castrum', 'red', cost(clay=2, wood=1, press=1), [Effect('shields', '', 3)], [])
FORTIFICATIONS = Card('Fortifications', 'red', cost(ore=3, clay=1, chain='castle'), [Effect('shields', '', 3)], [])
CIRCUS = Card('Circus', 'red', cost(stone=3, ore=1), [Effect('shields', '', 3)], [])
ARSENAL = Card('Arsenal', 'red', cost(wood=2, ore=1, loom=1), [Effect('shields', '', 3)], [])
SIEGE_WORKSHOP = Card('Siege Workshop', 'red', cost(clay=3, wood=1, chain='saw'), [Effect('shields', '', 3)], [])
LODGE = Card('Lodge', 'green', cost(clay=2, press=1, loom=1, chain='torch'), [Effect('science', 'compass', 1)], [])
ACADEMY = Card('Academy', 'green', cost(stone=3, glass=1, chain='harp'), [Effect('science', 'compass', 1)], [])
OBSERVATORY = Card('Observatory', 'green', cost(ore=2, glass=1, loom=1, chain='planets'), [Effect('science', 'gear', 1)], [])
STUDY = Card('Study', 'green', cost(wood=1, press=1, loom=1, chain='feather'), [Effect('science', 'gear', 1)], [])
UNIVERSITY = Card('University', 'green', cost(wood=2, glass=1, press=1, chain='scroll'), [Effect('science', 'tablet', 1)], [])
WORKERS_GUILD = Card('Workers Guild', 'purple', cost(ore=2, wood=1, stone=1, clay=1), [Effect('points_for_cards', 'brown', 1)], [])
CRAFTSMENS_GUILD = Card('Craftsmens Guild', 'purple', cost(stone=2, ore=2), [Effect('points_for_cards', 'grey', 1)], [])
MAGISTRATES_GUILD = Card('Magistrates Guild', 'purple', cost(wood=3, stone=1, loom=1), [Effect('points_for_cards', 'blue', 1)], [])
TRADERS_GUILD = Card('Traders Guild', 'purple', cost(glass=1, press=1, loom=1), [Effect('points_for_cards', 'yellow', 1)], [])
BUILDERS_GUILD = Card('Builders Guild', 'purple', cost(stone=3, clay=2, glass=1), [Effect('points_for_stages', '', 1)], [])
SPIES_GUILD = Card('Spies Guild', 'purple', cost(clay=2, glass=1), [Effect('points_for_cards', 'red', 1)], [])
PHILOSOPHERS_GUILD = Card('Philosophers Guild', 'purple', cost(clay=3, press=1, loom=1), [Effect('points_for_cards', 'green', 1)], [])
DECORATORS_GUILD = Card('Decorators Guild', 'purple', cost(ore=2, stone=1, loom=1), [Effect('points_for_finished_wonder', '', 1)], [])
SCIENTISTS_GUILD = Card('Scientists Guild', 'purple', cost(wood=2, ore=2, press=1), [Effect('multi_science', 'compass/tablet/gear', 1)], [])
SHIPOWNERS_GUILD = Card('Shipowners Guild', 'purple', cost(wood=3, glass=1, press=1), [Effect('points_for_self_cards', 'brown', 1), Effect('points_for_self_cards', 'grey', 1), Effect('points_for_self_cards', 'purple', 1)], [])

# Returns a list of Cards in the deck for the given player count and age.
# Note: will return all guilds in age 3 (at the beginning of the list). Removal of guilds must be done by the caller.
def get_cards_for_players_age(players, age):
    if age == 1:
        cards = [
            LUMBER_YARD, STONE_PIT, CLAY_POOL, ORE_VEIN, CLAY_PIT, TIMBER_YARD,
            GLASSWORKS, PRESS, LOOM,
            BATHS, ALTAR, THEATER,
            MARKETPLACE, WEST_TRADING_POST, EAST_TRADING_POST,
            STOCKADE, BARRACKS, GUARD_TOWER,
            APOTHECARY, WORKSHOP, SCRIPTORIUM
        ]
        if players >= 4:
            cards.extend([
                LUMBER_YARD, ORE_VEIN, EXCAVATION,
                PAWNSHOP,
                TAVERN,
                GUARD_TOWER,
                SCRIPTORIUM
            ])
        if players >= 5:
            cards.extend([
                STONE_PIT, CLAY_POOL, FOREST_CAVE,
                ALTAR,
                TAVERN,
                BARRACKS,
                APOTHECARY
            ])
        if players >= 6:
            cards.extend([
                TREE_FARM, MINE,
                GLASSWORKS, PRESS, LOOM,
                THEATER,
                MARKETPLACE
            ])
        if players >= 7:
            cards.extend([
                PAWNSHOP, BATHS,
                TAVERN, WEST_TRADING_POST, EAST_TRADING_POST,
                STOCKADE,
                WORKSHOP
            ])
    elif age == 2:
        cards = [
            SAWMILL, QUARRY, BRICKYARD, FOUNDRY,
            GLASSWORKS, PRESS, LOOM,
            STATUE, AQUEDUCT, TEMPLE, COURTHOUSE,
            CARAVANSERY, FORUM, VINEYARD,
            STABLES, ARCHERY_RANGE, WALLS,
            DISPENSARY, LABORATORY, LIBRARY, SCHOOL
        ]
        if players >= 4:
            cards.extend([
                SAWMILL, QUARRY, BRICKYARD, FOUNDRY,
                BAZAAR,
                TRAINING_GROUND,
                DISPENSARY
            ])
        if players >= 5:
            cards.extend([
                GLASSWORKS, PRESS, LOOM,
                COURTHOUSE,
                CARAVANSERY,
                STABLES,
                LABORATORY
            ])
        if players >= 6:
            cards.extend([
                TEMPLE,
                CARAVANSERY, FORUM, VINEYARD,
                ARCHERY_RANGE, TRAINING_GROUND,
                LIBRARY
            ])
        if players >= 7:
            cards.extend([
                STATUE, AQUEDUCT,
                CARAVANSERY, FORUM, BAZAAR,
                WALLS, TRAINING_GROUND,
                SCHOOL
            ])
    elif age == 3:
        cards = [
            WORKERS_GUILD, CRAFTSMENS_GUILD, MAGISTRATES_GUILD, TRADERS_GUILD, BUILDERS_GUILD, SPIES_GUILD, PHILOSOPHERS_GUILD, DECORATORS_GUILD, SCIENTISTS_GUILD, SHIPOWNERS_GUILD,
            PANTHEON, GARDENS, TOWN_HALL, PALACE, SENATE,
            LIGHTHOUSE, HAVEN, ARENA,
            FORTIFICATIONS, ARSENAL, SIEGE_WORKSHOP,
            LODGE, ACADEMY, OBSERVATORY, STUDY, UNIVERSITY
        ]
        if players >= 4:
            cards.extend([
                GARDENS,
                HAVEN, CHAMBER_OF_COMMERCE,
                CASTRUM, CIRCUS,
                UNIVERSITY
            ])
        if players >= 5:
            cards.extend([
                SENATE,
                LUDUS, ARENA,
                ARSENAL, SIEGE_WORKSHOP,
                STUDY
            ])
        if players >= 6:
            cards.extend([
                PANTHEON, TOWN_HALL,
                LIGHTHOUSE, CHAMBER_OF_COMMERCE,
                CIRCUS,
                LODGE
            ])
        if players >= 7:
            cards.extend([
                PALACE,
                LUDUS,
                CASTRUM, FORTIFICATIONS,
                ACADEMY, OBSERVATORY,
            ])
    else:
        cards = []
    return cards


# Gets a card by its name.
def get_card_by_name(name):
    for age in [1, 2, 3]:
        for card in get_cards_for_players_age(7, age):
            if card.name == name:
                return card
    return None

