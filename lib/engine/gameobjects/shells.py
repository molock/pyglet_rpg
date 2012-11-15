#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from engine.enginelib.meta import *
from engine.enginelib.mutable import MutableObject

from weakref import ProxyType

from config import *

class Shell(MutableObject, DiplomacySubject, Temporary, Solid, Mortal, ActiveState):
    def __init__(self, direct, speed, fraction, striker, damage, alive_after_collission):
        assert isinstance(striker, ProxyType)
        assert isinstance(direct, Position)

        MutableObject.__init__(self, None, speed = self.speed)

        Temporary.mixin(self, 1)
        Mortal.mixin(self, damage, alive_after_collission)
        DiplomacySubject.mixin(self, fraction)

        one_step = Position(self.speed, self.speed)
        self.direct = direct*(abs(one_step)/abs(direct))


        self.alive = True
        self.striker = striker

    def collission(self, player):
        if isinstance(player, Breakable):
            player.move(self.direct)
            Mortal.collission(self, player)

    def update(self):
        self.move(self.direct)


class DeviationMixin(Shell):
    __deviation = Position(0,0)


    def set_deviation(self, deviation):
        assert isinstance(deviation, Position)
        self.__deviation = deviation

    # def update(self):
    #     vector = self.direct +  self.__deviation
    #     self.move(self.direct)





class Ball(Fragile,  Shell):
    "снаряд игрока"
    radius = TILESIZE/2
    speed = 60
    BLOCKTILES = ['stone', 'forest']
    explode_time = 20
    alive_after_collission = False
    def __init__(self, direct, fraction, striker, damage = 2):
        Shell.__init__(self, direct, self.speed, fraction, striker, damage, self.alive_after_collission)
        
    
    def update(self):
        Shell.update(self)
        Temporary.update(self)
            
    
    
    def collission(self, player):
        Mortal.collission(self, player)
                
    
    def tile_collission(self, tile):
        self.add_to_remove()

    def handle_remove(self):
        return ('explode', self.explode_time)


class AllyBall(Ball):
    pass
                    


class DarkBall(Ball):
    "снаряд лича"
    radius = TILESIZE/3
    speed = 30
    
class SkillBall(Ball, DeviationMixin):
    radius = TILESIZE
    speed = 70
    alive_after_collission = True

