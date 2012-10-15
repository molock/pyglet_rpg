#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from random import randrange

from engine.engine_lib import *
from engine.gameobjects.player import Player

class GetTeleport:
    "фабрика  телепортов"
    def __init__(self, ttype, dest):
        self.dest = dest
        self.ttype = ttype
        self.BLOCKTILES = ttype.BLOCKTILES
        self.choice_position = ttype.choice_position
    
    def __call__(self, position):
        return self.ttype(position, self.dest)
        

class Teleport(StaticObject, Solid):
    radius = TILESIZE
    BLOCKTILES = Player.BLOCKTILES + ['water']
    min_dist = 3
    def __init__(self, position, dest):
        StaticObject.__init__(self, position)
        self.dest = dest
    
    def handle_creating(self):
        self.world.teleports.append(self.position)
    
    @wrappers.player_filter(Guided)
    def collission(self, player):
        self.world.game.change_world(player, self.dest)
    
    @classmethod
    def choice_position(cls, world, location, i ,j):
        for tpoint in world.teleports:
            dist = abs(Point(i,j)*TILESIZE - tpoint)
            if dist<=cls.min_dist*TILESIZE:
                return False
        return True
        
    
    def remove(self):
        StaticObject.remove(self)
        return True

class Cave(Teleport):
    pass
    
class Stair(Teleport):
    min_dist = 10
    pass

class UpStair(Teleport):
    pass

class DownCave(Teleport):
    pass


class Misc(StaticObject):
    BLOCKTILES = Player.BLOCKTILES
    def __init__(self, position):
        StaticObject.__init__(self, position)
        self.number = randrange(self.count)
    
    def get_args(self):
        return {'number': self.number}

class Mushroom(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 12

class Plant(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 10

class Flower(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 15

class WaterFlower(Misc):
    count = 9
    BLOCKTILES = ['grass', 'forest', 'bush', 'stone', 'underground', 'lava']

class BigWaterFlower(WaterFlower):
    count = 9
    @classmethod
    def choice_position(cls, world, location, i ,j):
        for tile in world.get_near_tiles(i,j):
                if tile in cls.BLOCKTILES:
                    return False
        return True

    
class Rubble(Misc):
    count = 3
    BLOCKTILES = Player.BLOCKTILES
    

class Stone(Misc):
    BLOCKTILES = Player.BLOCKTILES + ['water']
    count = 13

class AloneTree(Misc, Solid):
    BLOCKTILES = ['forest', 'bush', 'water', 'ocean']
    count = 13
    radius = TILESIZE
    def __init__(self, position):
        Misc.__init__(self, position)
        Solid.__init__(self, self.radius)
