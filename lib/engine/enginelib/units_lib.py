#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.enginelib.meta import *
from engine.mathlib import chance
from engine.gameobjects.items import *
from engine.enginelib.movable import Movable
from engine.enginelib import wrappers



from random import randrange, random      
from time import time

class Unit(Solid, Movable, Breakable, DiplomacySubject, GameObject):
    def __init__(self, speed, hp, corpse, fraction):
        Movable.mixin(self, speed)
        Breakable.__init__(self, corpse, hp)
        DiplomacySubject.mixin(self, fraction)
        Solid.mixin(self, TILESIZE/2)

class Lootable(Breakable):
    loot = [Lamp, Sceptre, HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold, Cloak]
    def mixin(self, cost):
        self.cost = cost if cost<= 100 else 50
    
    def die(self):
        if chance(self.cost):
            item = choice(self.loot)(self.position)
            self.world.new_object(item)
        Breakable.die(self)


class Fighter:
    def mixin(self):
        assert hasattr(self, 'damage') and hasattr(self, 'attack_speed')
        
        self.attack_speed = 1.0/self.attack_speed
        self.prev_attack = time()
    
    def collission(self, player):
        if isinstance(player, Unit) and not self.fraction is player.fraction:
                cur_time = time()
                if cur_time - self.prev_attack > self.attack_speed:
                    self.prev_attack = cur_time

                    player.hit(self.damage)
                    self.add_event('attack')
    



class Healer:
    heal_timeout = 30
    def mixin(self, heal_hp, heal_player_speed = 0.2):
        self.heal_hp = heal_hp
        self.prev_heal = time()
        self.heal_player_speed = 1.0/heal_player_speed

    def heal_player(self, player):
        cur_time = time()
        if cur_time- self.prev_heal > self.heal_player_speed:
            self.prev_heal = cur_time
            player.heal(5)
            self.add_event('heal', timeout = self.heal_timeout)

class Stalker:
    "объекты охотящиеся за игроками"
    def mixin(self, look_size):
        self.look_size = look_size
    
    def hunt(self, inradius = False):
            players = self.location.get_players_list()
            dists = []
            for player in players:
                if player.fraction!=self.fraction and  player.fraction!='good':
                    if not player.invisible:
                        dists.append(player.position - self.position)
            if dists:
                victim = min(dists, key = abs)
                return victim
            else:
                return Point(0,0)
            
class Striker:
    def mixin(self, strike_speed, shell, damage):
        self.strike_shell = shell
        self.strike_speed = 1.0/strike_speed
        self.damage = damage

        self.prev_strike = time()
    
    @wrappers.alive_only()
    def strike_ball(self, vector):
        if vector:
            cur_time = time()

            if cur_time-self.prev_strike> self.strike_speed:
                self.prev_strike = cur_time

                ball = self.strike_shell(self.position, vector, self.fraction, self.name, self.damage)
                self.world.new_object(ball)
    
    def plus_damage(self, damage):
        self.damage+=damage
            


class Stats:
    def mixin(self):
        self.gold = 0
        self.kills = 0
        self.stats_changed = False
        self.prev_stats = None
    
    def plus_gold(self, gold=1):
        self.gold+=1
    
    def plus_kills(self):
        self.kills+=1
        self.world.game.guided_changed = True
    
    def update(self):
        stats = (self.hp, self.hp_value, self.speed, self.damage,
            self.gold, self.kills, self.death_counter, self.skills, bool(self.invisible))
        if self.prev_stats!=stats:
            self.prev_stats = stats
            self.stats_changed = True
    
    def get_stats(self):
        data = (self.hp, self.hp_value, self.speed, self.damage,
                self.gold, self.kills, self.death_counter ,self.skills, bool(self.invisible))
        self.stats_changed = False
        return data


class Walker(Movable):
    def update(self):
        positive_x = -1 if random()>0.5 else 1
        positive_y = -1 if random()>0.5 else 1
        partx = random()*10
        party = random()*10
        x = positive_x*self.speed*partx
        y = positive_y*self.speed*party
        direct = Point(x,y)
        self.move(direct)


class MetaMonster(Respawnable, Lootable, Unit, Stalker, Walker, DynamicObject):
    radius = TILESIZE
    look_size = 10
    BLOCKTILES = ['stone', 'forest', 'ocean', 'lava']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    def __init__(self, name, position, speed, hp):
        DynamicObject.__init__(self, name, position)
        Unit.__init__(self, speed, hp, Corpse, 'monsters')
        Stalker.mixin(self, self.look_size)
        Respawnable.mixin(self, 60, 100)
        Lootable.mixin(self, self.loot_cost)
        
        self.stopped = False
        
        self.spawn()
    
    def hit(self, damage):
        self.stop(10)
        Breakable.hit(self, damage)
    
    @wrappers.alive_only(Breakable)
    def update(self):
        if chance(70):
            direct = self.hunt()
            if direct:
                self.move(direct)
            else:
                Walker.update(self)
        else:
            Walker.update(self)
        Breakable.update(self)
    
    def get_args(self):
        return Breakable.get_args(self)
    

