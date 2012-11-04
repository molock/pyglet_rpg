#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *


from engine.enginelib.meta import *
from engine.enginelib.equipment import Equipment
from engine.enginelib import wrappers


class Item(GameObject, Solid, Temporary):
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    radius = TILESIZE
    lifetime = 300
    def __init__(self,):
        GameObject.__init__(self)
        Temporary.__init__(self, 10*self.lifetime)
    
    @wrappers.player_filter(Equipment)
    def collission(self, player):
        if player.add_item(self):
            self.location.remove_object(self)
        
    
    def update(self):
        Temporary.update(self)
    
    def effect(self):
        pass
    
    def remove(self):
        GameObject.remove(self)
        return True



class HealPotion(Item):
    "излечивает"
    hp = 5
    def effect(self):
        self.owner.heal(self.hp)

class SpeedPotion(Item):
    "увеличивает скорость"
    speed = 5
    def effect(self):
        self.owner.plus_speed(self.speed)
    
class Sword(Item):
    "увеличивает урон"
    damage = 1
    def effect(self):
        self.owner.plus_damage(self.damage)

class Gold(Item):
    def effect(self):
        self.owner.plus_gold()

class Armor(Item):
    armor = 3
    def effect(self):
        self.owner.plus_hp(self.armor)

class Sceptre(Item):
    def effect(self):
        self.owner.plus_skill()
    
class Cloak(Item):
    invisible_time = 300
    def effect(self):
        self.owner.set_invisible(self.invisible_time)
    
class Lamp(Item):
     def effect(self):
         from engine.gameobjects.units import Ally
         ally = Ally()
         ally.bind_master(self.owner)
         self.owner.location.new_object(ally, chunk = self.owner.chunk.cord)
         
        
