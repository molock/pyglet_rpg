#!/usr/bin/env python
# -*- coding: utf-8 -*-
from share.mathlib import *
from share.map import *
from mathlib import *
import game

#

class UnknownAction(Exception):
    pass


class ActionDenied(Exception):
    pass

class ActionError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return 'ActionError: %s' % self.message

class wrappers:
    @staticmethod
    def alive_only(method):
        def wrap(self,*args):
            if self.alive:
                method(self, *args)
            else:
                ActionDenied
        return wrap
    
    @staticmethod
    def ignore_denied(method):
        def wrap(*args):
            try:
                result = method(*args)
            except ActionDenied:
                return None
            else:
                return result
        return wrap

#####################################################################
class GameObject:
    REMOVE = False            
    alive = True
    def __init__(self, name, position):
        self.name = name
        self.position = position
    
    def handle_action(self, action, args):
        if self.alive:
            if hasattr(self, action):
                return getattr(self, action)(*args)
            else:
                raise ActionError('no action %s' % action)
    
    def update(self):
        pass
    
    def add_event(self, *args):
        game.add_event(self.name, *args)
    
    
    def remove(self):
        return True
    
    def handle_response(self):
        return []

#####################################################################
class StaticObject(GameObject):
    def __init__(self, name, position):
        GameObject.__init__(self, name, position)
    
    def update(self):
        self.add_event(self.position, NullPoint, 'exist', [])

    
    def complete_round(self):
        pass




class Guided(GameObject):
    "управляемый игроком объекта"
    pass

class Solid(GameObject):
    def collission(self, player):
        pass
#####################################################################

class MapObserver(MapTools):
    "класс объекта видящего карту"
    prev_looked = set()
    prev_observed = set()
    def __init__(self, look_size):
        MapTools.__init__(self, game.size, game.size)
        self.look_size = look_size
    def look(self):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        position = self.position
        rad = self.look_size
        I,J = (position/TILESIZE).get()
        #
        new_updates = {}
        #
        observed = set()
        looked = set()
        for i in xrange(I-rad, I+rad):
            for j in xrange(J-rad, J+rad):
                diff = hypot(I-i,J-j) - rad
                if diff<0:
                    i,j = self.resize(i), self.resize(j)
                    try:
                        tile_type = game.world.map[i][j]
                    except IndexError, excp:
                        pass
                    else:
                        looked.add((Point(i,j), tile_type))
                        observed.add((i,j))
                        if (i,j) in game.updates:
                            for uid, (name, object_type, position, action, args) in game.updates[(i,j)]:
                                if name==self.name:
                                    object_type = 'Self'
                                new_updates[uid] = (name, object_type, position, action, args)

        new_looked = looked - self.prev_looked
        self.prev_looked = looked
        self.prev_observed = observed
        return new_looked, observed, new_updates
    

####################################################################

class Stalker:
    "объекты охотящиеся за игроками"
    def __init__(self, look_size):
        self.look_size = look_size
    
    def hunt(self):
        for player in game.players.values():
            if isinstance(player, Guided):
                distance = player.position - self.position
                if True: #abs(distance/TILESIZE)<self.look_size:
                    return player.position - self.position
        return None
        
class Deadly:
    "класс для живых объектов"
    def __init__(self, corpse, hp, heal_speed=0.01, death_time=20):
        self.hp_value = hp
        self.hp = hp
        self.heal_speed = heal_speed
        self.alive = True
        self.death_time = death_time
        self.death_time_value = death_time
        self.corpse = corpse
        self.death_counter = 0
    
    def hit(self, hp):
        self.hp-=hp
        if self.hp<=0:
            self.die()
            self.hp = self.hp_value
    
    def heal(self, hp):
        print 'HEAL %s' % hp
        new_hp = self.hp+ hp
        if new_hp>self.hp_value:
            new_hp = self.hp_value
        
        self.hp = new_hp
    
    def plus_hp(self, armor):
        self.hp_value+=armor
    
    def update(self):
        if self.alive:
            if self.hp<self.hp_value:
                self.hp+=self.heal_speed
        else:
            if self.death_time>0:
                self.death_time-=1
                self.add_event(self.position, NullPoint, 'die',  [])
            else:
                self.death_time = self.death_time_value
                self.REMOVE = True
                self.create_corpse()
    
    def create_corpse(self):
        name = 'corpse_%s_%s' % (self.name, self.death_counter)
        corpse = self.corpse(name, self.position)
        game.new_object(corpse)
    
    def die(self):
        self.alive = False
        self.death_counter+=1
        


class Fragile:
    "класс для объекто разбивающихся при столкновении с тайлами"
    pass
    
class Mortal:
    "класс для объектов убивающих живых при соприкосновении"
    def __init__(self, damage=1):
        self.damage = damage
    
    def collission(self, player):
        if isinstance(player, Deadly):
            if player.fraction!=self.fraction:
                player.hit(self.damage)
                self.alive = False
####################################################################

class Respawnable:
    "класс перерождающихся объектов"
    respawned = False
    def __init__(self, delay, distance):
        self.respawn_delay = delay
        self.respawn_distance = distance
        
    def remove(self):
        print 'respawning %s' % self.name
        new_position = game.choice_position(self, 10 ,self.position)
        vector = new_position - self.position
        self.position = new_position
        game.add_event(self.name, self.prev_position, NullPoint, 'remove')
        game.add_event(self.name, self.position, NullPoint, 'move', [NullPoint.get()])
        self.respawn_message = 'Respawn', self.position
        self.alive = True
        self.respawned = True
        return False

    
    def handle_response(self):
        print 'respawn_message %s' % self.name
        self.respawned = False
        return [self.respawn_message]

class DiplomacySubject:
    def __init__(self, fraction):
        self.fraction = fraction
####################################################################
class Temporary:
    "класс объекта с ограниченным сроком существования"
    def __init__(self, lifetime):
        self.lifetime = lifetime
    
    def update(self):
        self.lifetime-=1
        if self.lifetime<=0:
            self.REMOVE = True

class Striker:
    def __init__(self, strike_speed, shell, damage):
        self.strike_shell = shell
        self.strike_counter = 0
        self.strike_speed = strike_speed
        self.damage = damage
    
    def strike_ball(self, vector):
        if self.strike_counter==0:
            ball_name = 'ball%s' % game.ball_counter
            game.ball_counter+=1
            ball = self.strike_shell(ball_name, self.position, vector, self.fraction, self.damage)
            game.new_object(ball)
            self.strike_counter+=self.strike_speed
    
    def plus_damage(self, damage):
        self.damage+=damage
            
    def update(self):
        if self.strike_counter>0:
            self.strike_counter -=1
    
    def complete_round(self):
        self.striked = False

from random import choice


