from game.base import *
from random import randint, sample

# This file contains wonder definitions for all wonders in the base 7 Wonders game.

def GIZA_DAY():
    return Wonder('Giza', 'Day', 3, [Effect('resource', 'stone', 1)], [
        WonderStage(1, cost(wood=2), [Effect('points', '', 3)]),
        WonderStage(2, cost(clay=2, loom=1), [Effect('points', '', 5)]),
        WonderStage(3, cost(stone=4), [Effect('points', '', 7)])
    ])
def GIZA_NIGHT():
    return Wonder('Giza', 'Night', 3, [Effect('resource', 'stone', 1)], [
        WonderStage(1, cost(wood=2), [Effect('points', '', 3)]),
        WonderStage(2, cost(stone=3), [Effect('points', '', 5)]),
        WonderStage(3, cost(clay=3), [Effect('points', '', 5)]),
        WonderStage(4, cost(stone=4, press=1), [Effect('points', '', 7)])
    ])

def EPHESOS_DAY():
    return Wonder('Ephesos', 'Day', 3, [Effect('resource', 'press', 1)], [
        WonderStage(1, cost(clay=2), [Effect('points', '', 3)]),
        WonderStage(2, cost(wood=2), [Effect('gold', '', 9)]),
        WonderStage(3, cost(ore=2, glass=1), [Effect('points', '', 7)])
    ])
def EPHESOS_NIGHT():
    return Wonder('Ephesos', 'Night', 3, [Effect('resource', 'press', 1)], [
        WonderStage(1, cost(stone=2), [Effect('gold', '', 4), Effect('points', '', 2)]),
        WonderStage(2, cost(wood=2), [Effect('gold', '', 4), Effect('points', '', 3)]),
        WonderStage(3, cost(ore=2, loom=1), [Effect('gold', '', 4), Effect('points', '', 5)])
    ])

def RHODOS_DAY():
    return Wonder('Rhodos', 'Day', 3, [Effect('resource', 'ore', 1)], [
        WonderStage(1, cost(wood=2), [Effect('points', '', 3)]),
        WonderStage(2, cost(clay=3), [Effect('shields', '', 2)]),
        WonderStage(3, cost(ore=4), [Effect('points', '', 7)])
    ])
def RHODOS_NIGHT():
    return Wonder('Rhodos', 'Night', 3, [Effect('resource', 'ore', 1)], [
        WonderStage(1, cost(stone=3), [Effect('shields', '', 1), Effect('gold', '', 3), Effect('points', '', 3)]),
        WonderStage(2, cost(ore=4), [Effect('shields', '', 1), Effect('gold', '', 4), Effect('points', '', 4)]),
    ])

def ALEXANDRIA_DAY():
    return Wonder('Alexandria', 'Day', 3, [Effect('resource', 'glass', 1)], [
        WonderStage(1, cost(stone=2), [Effect('points', '', 3)]),
        WonderStage(2, cost(ore=2), [Effect('multi_resource_unpurchasable', 'wood/stone/ore/clay', 1)]),
        WonderStage(3, cost(press=1, loom=1), [Effect('points', '', 7)])
    ])
def ALEXANDRIA_NIGHT():
    return Wonder('Alexandria', 'Night', 3, [Effect('resource', 'glass', 1)], [
        WonderStage(1, cost(clay=2), [Effect('multi_resource_unpurchasable', 'wood/stone/ore/clay', 1)]),
        WonderStage(2, cost(ore=3), [Effect('multi_resource_unpurchasable', 'glass/press/loom', 1)]),
        WonderStage(3, cost(wood=4), [Effect('points', '', 7)])
    ])

def OLYMPIA_DAY():
    return Wonder('Olympia', 'Day', 3, [Effect('resource', 'clay', 1)], [
        WonderStage(1, cost(stone=2), [Effect('points', '', 3)]),
        WonderStage(2, cost(wood=2), [Effect('free_build_first_color', '', 1)]),
        WonderStage(3, cost(clay=3), [Effect('points', '', 7)])
    ])
def OLYMPIA_NIGHT():
    return Wonder('Olympia', 'Night', 3, [Effect('resource', 'clay', 1)], [
        WonderStage(1, cost(ore=2), [Effect('free_build_alpha', '', 1), Effect('points', '', 2)]),
        WonderStage(2, cost(clay=3), [Effect('free_build_omega', '', 1), Effect('points', '', 3)]),
        WonderStage(3, cost(glass=1, press=1, loom=1), [Effect('points', '', 5)])
    ])

def BABYLON_DAY():
    return Wonder('Babylon', 'Day', 3, [Effect('resource', 'wood', 1)], [
        WonderStage(1, cost(clay=2), [Effect('points', '', 3)]),
        WonderStage(2, cost(ore=2, loom=1), [Effect('multi_science', 'compass/tablet/gear', 1)]),
        WonderStage(3, cost(wood=4), [Effect('points', '', 7)])
    ])
def BABYLON_NIGHT():
    return Wonder('Babylon', 'Night', 3, [Effect('resource', 'wood', 1)], [
        WonderStage(1, cost(stone=2), [Effect('play_last_card', '', 1)]),
        WonderStage(2, cost(clay=3, glass=1), [Effect('multi_science', 'compass/tablet/gear', 1)])
    ])

def HALIKARNASSOS_DAY():
    return Wonder('Halikarnassos', 'Day', 3, [Effect('resource', 'loom', 1)], [
        WonderStage(1, cost(ore=2), [Effect('points', '', 3)]),
        WonderStage(2, cost(glass=1, press=1), [Effect('build_from_discard', '', 1)]),
        WonderStage(3, cost(stone=3), [Effect('points', '', 7)])
    ])
def HALIKARNASSOS_NIGHT():
    return Wonder('Halikarnassos', 'Night', 3, [Effect('resource', 'loom', 1)], [
        WonderStage(1, cost(clay=2), [Effect('build_from_discard', '', 1), Effect('points', '', 2)]),
        WonderStage(2, cost(glass=1, press=1), [Effect('build_from_discard', '', 1), Effect('points', '', 1)]),
        WonderStage(3, cost(wood=3), [Effect('build_from_discard', '', 1)])
    ])

ALL_WONDERS = [
    [GIZA_DAY, GIZA_NIGHT],
    [EPHESOS_DAY, EPHESOS_NIGHT],
    [RHODOS_DAY, RHODOS_NIGHT],
    [ALEXANDRIA_DAY, ALEXANDRIA_NIGHT],
    [OLYMPIA_DAY, OLYMPIA_NIGHT],
    [BABYLON_DAY, BABYLON_NIGHT],
    [HALIKARNASSOS_DAY, HALIKARNASSOS_NIGHT]
]


# Returns a random sample of Wonders with random sides.
def get_random_wonders(num):
    wonders = sample(ALL_WONDERS, num)
    return [wonder[randint(0, 1)]() for wonder in wonders]


def get_all_wonders():
    res = []
    for wonder in ALL_WONDERS:
        res.append(wonder[0]())
    for wonder in ALL_WONDERS:
        res.append(wonder[1]())
    return res


# Returns the wonder factory for the given BGA wonder name and side.
def get_wonder_by_bga_name_side(name, side):
    name_i = {
        'The Pyramids of Giza': 0,
        'The Temple of Artemis in Ephesus': 1,
        'The Colossus of Rhodes': 2,
        'The Lighthouse of Alexandria': 3,
        'The Statue of Zeus in Olympia': 4,
        'The Hanging Gardens of Babylon': 5,
        'The Mausoleum of Halicarnassus': 6
    }
    side_i = {'Day': 0, 'Night': 1}
    if name not in name_i or side not in side_i:
        raise Exception(f"Could not parse wonder: {name} {side}")
    return ALL_WONDERS[name_i[name]][side_i[side]]
