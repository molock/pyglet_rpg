#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *
from engine.mathlib import chance
from items import *
from movable import Movable

from config import *


class Unit(Solid, Movable, Deadly, DiplomacySubject):
    def __init__(self, speed, hp, corpse, fraction):
        Movable.__init__(self, speed)
        Deadly.__init__(self, corpse, hp)
        DiplomacySubject.__init__(self, fraction)

class Lootable(Deadly):
    loot = [HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold]
    def die(self):
        if chance(30):
            item = choice(self.loot)(self.position)
            game.new_object(item)
        Deadly.die(self)


#####################################################################
class Player(Unit, MapObserver, Striker, Guided, Respawnable):
    "класс игрока"
    radius = TILESIZE/2
    prev_looked = set()
    speed = 40
    hp = 50
    BLOCKTILES = ['stone', 'forest', 'ocean']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    damage = 2

    def __init__(self, name, player_position, look_size):
        GameObject.__init__(self, name, player_position)
        Unit.__init__(self, self.speed, self.hp, Corpse, self.name)
        MapObserver.__init__(self, look_size)
        Striker.__init__(self,2, Ball, self.damage)
        Respawnable.__init__(self, 10, 30)
    
    @wrappers.alive_only()
    def handle_action(self, action, args):
        GameObject.handle_action(self,action,args)
        
    def handle_response(self):
        if not self.respawned:
            move_vector = Movable.handle_request(self)
            new_looked, observed, updates = self.look()
    
            return [('Look', (move_vector, self.hp, new_looked, observed, updates, []))]
        else:
            return Respawnable.handle_response(self)

    @wrappers.alive_only()
    def Strike(self, vector):
        self.strike_ball(vector)
    
    @wrappers.alive_only()
    def Move(self, vector):
        Movable.move(self, vector)
    
    def Look(self):
        return MapObserver.look(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)
    
    @wrappers.alive_only(Deadly)
    def update(self):
        Movable.update(self)
        Striker.update(self)
        Deadly.update(self)
    

##################################################################### 
from random import randrange       

class Walker(Movable):
    def update(self):
        x = randrange(-self.speed, self.speed)
        y = randrange(-self.speed, self.speed)
        direct = Point(x,y)
        self.move(direct)

class MetaMonster(Lootable, Unit, Respawnable, Stalker, Mortal, Walker):
    radius = TILESIZE
    look_size = 10
    BLOCKTILES = ['stone', 'forest', 'ocean']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    def __init__(self, name, player_position, speed, hp):
        GameObject.__init__(self, name, player_position)
        Unit.__init__(self, speed, hp, Corpse, 'monsters')
        Stalker.__init__(self, self.look_size)
        Mortal.__init__(self, 1)
        Respawnable.__init__(self, 30, 60)
    
    @wrappers.alive_only(Deadly)
    def update(self):
        direct = self.hunt()
        if direct:
            self.move(direct)
        else:
            Walker.update(self)
        Movable.update(self)
        Deadly.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
    


class Zombie(Mortal, MetaMonster):
    hp = 3
    speed = 15
    def __init__(self, name, position):
        Mortal.__init__(self, 2)
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
    

class Ghast(MetaMonster, Mortal):
    hp = 20
    speed = 7
    def __init__(self, name, position):
        Mortal.__init__(self, 2)
        MetaMonster.__init__(self, name, position, self.speed, self.hp)

class Lych(MetaMonster, Striker):
    hp = 5
    speed = 15
    damage = 2
    def __init__(self, name, position):
        MetaMonster.__init__(self, name, position, self.speed, self.hp)
        Striker.__init__(self, 10, DarkBall, self.damage)
    
    @wrappers.alive_only(Deadly)
    def update(self):
        direct = self.hunt()
        if direct:
            self.strike_ball(direct)
        else:
            Walker.update(self)
            
        Movable.update(self)
        Striker.update(self)
        Deadly.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)
