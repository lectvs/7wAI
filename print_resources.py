from game.deck import *
from game.wonders import *
from collections import namedtuple


AgeAiVar = namedtuple('AgeAiVar', ['actualValue', 'defaultValue', 'mutationProfile'])

class AiVar:
    def __init__(self, defaultArr, mutationProfile):
        self.ages = [
            AgeAiVar(defaultArr[0], defaultArr[0], mutationProfile),
            AgeAiVar(defaultArr[1], defaultArr[1], mutationProfile),
            AgeAiVar(defaultArr[2], defaultArr[2], mutationProfile),
        ]
    def __str__(self):
        return f"1:{self.ages[0].actualValue}, 2:{self.ages[1].actualValue}, 3:{self.ages[2].actualValue}"

    def getAgeValue(self, age):
        agv = self.ages[age].actualValue
        if isinstance(agv, str):
            return eval(agv, {a1: self.ages[0].actualValue, a2: self.ages[1].actualValue, a3: self.ages[2].actualValue})
        else:
            return agv

# mutability
MUTABILITY_NONE = 0
MUTABILITY_RARE = 1
MUTABILITY_LOW = 25
MUTABILITY_MED = 500
MUTABILITY_HIGH = 1000

MUTATE_SIZE_NONE = 0
MUTATE_SIZE_TINY = 0.05
MUTATE_SIZE_SMALL = 0.1
MUTATE_SIZE_BIG = 0.2

wonder_coefficients = {
    "Giza_Day": {
        "stage1_w":     AiVar( [1,   2,     3], ['rare','normal', 0, 3] ),
        "stage1_w":     AiVar( [1,   2,     3], ['rare','normal', 0, 3] ),
        "stage2_w":     AiVar( [0.5, 1,     2], ['rare','normal', 0, 2] ),
        "stage3_w":     AiVar( [0.1, 0.1,   1], ['rare','normal', 0, 2] ),
        "military_w":   AiVar( [1,   1,     1], ['rare','normal', 0, 2] ),
        "science_w":    AiVar( [1,   1,     1], ['rare','normal', 0, 2] ),
        "blue_w":       AiVar( [1,   1,     1], ['rare','normal', 0, 2] ),
        "coin_w":       AiVar( [1,   1,     1], ['rare','normal', 0, 2] ),

        "wood_t":       AiVar( [2.2, 3,  'a2'], ['rare','normal', 0, 3] ),
        "ore_t":        AiVar( [1,   3,  'a2'], ['rare','normal', 0, 3] ),
        "clay_t":       AiVar( [2.1, 3,  'a2'], ['rare','normal', 0, 3] ),
        "stone_t":      AiVar( [2,   4,  'a2'], ['rare','normal', 0, 4] ),
        "loom_t":       AiVar( [1.1, 1,     1], ['none', 'slow', 1, 1] ),
        "press_t":      AiVar( [1,   1,     1], ['none', 'slow', 1, 1] ),
        "glass_t":      AiVar( [1,   1,     1], ['none', 'slow', 1, 1] ),

        "resource_c":   AiVar( [1,   1,     1], ['normal','normal', 0, 2] ),
        "points_c":     AiVar( [1,   1,     2], ['normal','normal', 0,2] ),
        "coin_add_c":   AiVar( [1,   1,     1], ['normal','normal', 0,2] ),
        "coin_spend_c": AiVar( [1,   1,     1], ['normal','normal', 0,2] ),
        "military_c":   AiVar( [1,   1,     1], ['normal','normal', 0,2] ),
        "science_c":    AiVar( [1,   1,     1], ['normal','normal', 0,2] ),
        "chain_c":      AiVar( [1,   1,   '0'], ['normal','normal', 0,2] ),
    }
}

all_cards = [
    LUMBER_YARD,
    STONE_PIT,
    CLAY_POOL,
    ORE_VEIN,
    TREE_FARM,
    EXCAVATION,
    CLAY_PIT,
    TIMBER_YARD,
    FOREST_CAVE,
    MINE,
    GLASSWORKS,
    PRESS,
    LOOM,
    PAWNSHOP,
    BATHS,
    ALTAR,
    THEATER,
    TAVERN,
    MARKETPLACE,
    WEST_TRADING_POST,
    EAST_TRADING_POST,
    STOCKADE,
    BARRACKS,
    GUARD_TOWER,
    APOTHECARY,
    WORKSHOP,
    SCRIPTORIM,
    SAWMILL,
    QUARRY,
    BRICKYARD,
    FOUNDRY,
    STATUE,
    AQUEDUCT,
    TEMPLE,
    COURTHOUSE,
    CARAVANSERY,
    FORUM,
    VINEYARD,
    BAZAAR,
    STABLES,
    ARCHERY_RANGE,
    WALLS,
    TRAINING_GROUND,
    DISPENSARY,
    LABORATORY,
    LIBRARY,
    SCHOOL,
    PANTHEON,
    GARDENS,
    TOWN_HALL,
    PALACE,
    SENATE,
    LIGHTHOUSE,
    HAVEN,
    CHAMBER_OF_COMMERCE,
    LUDUS,
    ARENA,
    CASTRUM,
    FORTIFICATIONS,
    CIRCUS,
    ARSENAL,
    SIEGE_WORKSHOP,
    LODGE,
    ACADEMY,
    OBSERVATORY,
    STUDY,
    UNIVERSITY,
    WORKERS_GUILD,
    CRAFTSMENS_GUILD,
    MAGISTRATES_GUILD,
    TRADERS_GUILD,
    BUILDERS_GUILD,
    SPIES_GUILD,
    PHILOSOPHERS_GUILD,
    DECORATORS_GUILD,
    SCIENTISTS_GUILD,
    SHIPOWNERS_GUILD,
]

def printResources():
    for card in all_cards:
        wood = card.cost.resources.count("wood")
        ore = card.cost.resources.count("ore")
        clay = card.cost.resources.count("clay")
        stone = card.cost.resources.count("stone")
        press = card.cost.resources.count("press")
        loom = card.cost.resources.count("loom")
        glass = card.cost.resources.count("glass")
        if (wood + ore + clay + stone + press + loom + glass) > 2:
            print(f"{card.name}\t{card.color}\t{wood}\t{ore}\t{clay}\t{stone}\t{press}\t{loom}\t{glass}")

def printChains():
    for card in all_cards:
        wood = card.cost.resources.count("wood")
        ore = card.cost.resources.count("ore")
        clay = card.cost.resources.count("clay")
        stone = card.cost.resources.count("stone")
        press = card.cost.resources.count("press")
        loom = card.cost.resources.count("loom")
        glass = card.cost.resources.count("glass")
        if len(card.chains) > 0:
            for chain in card.chains:
                print(f'"{chain}": 1,')

# printResources()
# print(f"{wonder_coefficients['Giza_Day']['military_w']}")
# printChains()

c_to = {}
c_to["#defult"] = 123
for key in c_to:
    print(key)