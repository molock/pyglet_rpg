#!/usr/bin/env python
# -*- coding: utf-8 -*-
from share.mathlib import *
from engine.mathlib import *

from random import choice, random
from time import time


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
    def alive_only(Class=None):
        def wrapper(method):
            def wrap(self,*args):
                if self.alive:
                    return method(self, *args)
                else:
                    if Class:
                        return getattr(Class, method.__name__)(self, *args)
            return wrap
        return wrapper
    
    @staticmethod
    def player_filter(Class):
        def wrapper(method):
            def wrap(self, player):
                if isinstance(player, Class):
                    return method(self,player)
            return wrap
        return wrapper
    
    @staticmethod
    def player_filter_alive(method):
        def wrap(self, player):
            if player.alive:
                return method(self,player)
        return wrap
    
    
    


#####################################################################
class GameObject(object):
    def __init__(self, name, position):
        self.related_objects = []
        self.name = name
        self.alive = True
        self.delayed = False
        
        self._position = position
        self.cord = position/TILESIZE
        self._prev_position = position
        
        self.gid = str(hash((name, position)))
        
        self.has_events = False
    
    def handle_creating(self):
        pass
    
    def handle_remove(self):
        pass
    
    def regid(self):
        
        self.gid = str(hash((self.name, self.position, random())))
        
    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, position):
        raise Error('Denied')
    
    def set_position(self, position):
        "принудительная установка позиции"
        size = self.world.size*TILESIZE
        if 0<=position.x<=size and 0<=position.y<=size:
            self._position = position
            self._prev_position = position
            self.cord = position/TILESIZE
        else:
            data = (position, self.name, self.world.name, self.world.size)
            self.world.handle_over_range(self, position)
            raise Warning('Invalid position %s %s world %s size %s' % data)
            
    def change_position(self,position):
        "вызывается при смене позиции"
        if not position==self._position:
            
            cur_cord = position/TILESIZE
            
            if 0<=cur_cord.x<=self.world.size and 0<=cur_cord.y<=self.world.size:
                prev_cord = self._position/TILESIZE
                
                if cur_cord!=prev_cord:
                    self.cord_changed = True
                    self.cord = cur_cord
                    
                if position!=self._position:
                    self.position_changed = True
                    
                prev_loc = self.location.cord
                cur_loc = self.world.get_loc_cord(position)
                if prev_loc!=cur_loc:
                    self.location = self.world.change_location(self.name, prev_loc, cur_loc)
                
                self._prev_position = self._position
                self._position  = position
            else:
                data = (position, self.name, self.world.name, self.world.size)
                self.world.handle_over_range(self, position)
                self.move_vector = Point()
                print('Warning: Invalid position %s %s' % (position, self.name))
    
    @staticmethod
    def choice_position(world_map, location, i ,j):
        return True
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, player):
        return self.name==player.name
    
    def __ne__(self, player):
        return self.name!=player.name
    
    def get_location(self):
        return self.world.get_location(self.position)
    
    def update(self):
        pass
    
    def collission(self, player):
        pass
        
    def tile_collission(self, tile):
        pass
    
    def remove(self):
        return True
    
    

class DynamicObject(GameObject):
    def __init__(self, name, position):
        GameObject.__init__(self, name, position)
        
        self.cord_changed = True
        self.position_changed = True
        self.world_changed = False
    
    @property
    def prev_position(self):
        return self._prev_position
    
    @prev_position.setter
    def prev_position(self):
        raise Warning('@prev_position.setter')
    
    def to_remove(self, force=False):
        self.world.game.add_to_remove(self, force)
    
    def add_event(self, action, *args,**kwargs):
        object_type = self.__class__.__name__
        vector = self.position-self.prev_position
        if 'timeout' in kwargs:
            timeout = kwargs['timeout']
        else:
            timeout = 0
        #print 'add_event', action, args
        self.world.add_event(self.gid, object_type, self.position, vector, action, args, timeout)
        self.has_events = True
    
    def complete_round(self):
        self.cord_changed = False
        self.position_changed = False
        self.has_events = False
        
    
    def get_tuple(self):
        return self.name, self.__class__.__name__, self.prev_position, self.get_args()
        
    def get_args(self):
        return {}

class StaticObject(GameObject):
    name_counter =0 
    def __init__(self, position):
        counter = StaticObject.name_counter
        StaticObject.name_counter+=1
    
        name = '%s_%s' % (self.__class__.__name__, counter)
        
        GameObject.__init__(self, name, position)
        
    
    def get_tuple(self):
        return self.name, self.__class__.__name__, self.position, self.get_args()
    
    def get_args(self):
        return {}
    
    def add_event(self, action, *args, **kwargs):
        object_type = self.__class__.__name__
        if 'timeout' in kwargs:
            timeout = kwargs['timeout']
        else:
            timeout = 0
        self.world.add_static_event(self.gid, object_type, self.position, action, args, timeout)

    
    def complete_round(self):
        pass
    

    
    def to_remove(self, force=False):
        self.world.game.add_to_remove_static(self, force)

class ActiveState:
    pass

class Guided(ActiveState):
    "управляемый игроком объекта"
    
    def handle_action(self, action_name, args):
        if hasattr(self, action_name):
            method = getattr(self, action_name)
            if hasattr(method, 'wrappers_action'):
                
                return method(*args)
            else:
                print("%s isn't guided action" % action_name)
                ActionError('no action %s' % action_name)
        else:
            print('no action %s' % action_name)
            raise ActionError('no action %s' % action_name)
    

    
    @staticmethod
    def action(method):
        method.wrappers_action = True
        return method
    


class Solid():
    def __init__(self, radius):
        self.radius = radius
    
    def collission(self, player):
        pass

#####################################################################


        
    

####################################################################


        
class Deadly:
    "класс для живых объектов"
    def __init__(self, corpse, hp, heal_speed=0.01, death_time=20):
        self.hp_value = hp
        self.heal_speed = heal_speed
        self.death_time = death_time
        self.death_time_value = death_time
        self.corpse = corpse
        self.death_counter = 0
        self.spawn()
        self.hitted = 0
    
    def spawn(self):
        self.alive = True
        self.hp = self.hp_value
        
    

    
    def hit(self, hp):
        self.hitted = 10
        if self.alive:
            self.hp-=hp
            
            self.add_event('change_hp', self.hp_value, self.hp if self.hp>0 else 0)
            if self.hp<=0:
                self.die()
                self.hp = self.hp_value
                return True
            else:
                return False
        else:
            return False
    
    def heal(self, hp):
        new_hp = self.hp+ hp
        if new_hp>self.hp_value:
            new_hp = self.hp_value
        
        self.hp = new_hp
        self.add_event('change_hp', self.hp_value, self.hp)
    
    def plus_hp(self, armor):
        self.hp_value+=armor
        self.add_event('change_hp', self.hp_value, self.hp)
    
    def update(self):
        if self.alive:
            if self.hitted:
                self.add_event('defend')
                self.hitted-=1
            else:
                if self.hp<self.hp_value:
                    self.hp+=self.heal_speed
        else:
            if self.death_time>0:
                self.death_time-=1
                self.add_event('die')
            else:
                self.death_time = self.death_time_value
                self.to_remove()
                self.create_corpse()
    
    def create_corpse(self):
        name = 'corpse_%s_%s' % (self.name, self.death_counter)
        corpse = self.corpse(name, self.position)
        self.world.new_static_object(corpse)
    
    def die(self):
        self.alive = False
        self.death_counter+=1
        self.abort_moving()
    
    def get_args(self):
        return {'hp': self.hp, 'hp_value':self.hp_value}
    
    
        


class Fragile:
    "класс для объекто разбивающихся при столкновении с тайлами"
    def tile_collission(self, tile):
        self.alive = False
    
class Mortal:
    "класс для объектов убивающих живых при соприкосновении"
    def __init__(self, damage=1, alive_after_collission = False):
        self.damage = damage
        self.alive_after_collission = alive_after_collission
    
    @wrappers.player_filter(Deadly)
    def collission(self, player):
        if player.fraction!=self.fraction:
            prev_state = player.alive
            player.hit(self.damage)
            self.alive = self.alive_after_collission
            #
            if self.striker in self.world.game.players:
                striker = self.world.game.players[self.striker].player
                if isinstance(striker, Guided):
                    if prev_state and not player.alive:
                        striker.plus_kills()

####################################################################

class Respawnable:
    "класс перерождающихся объектов"
    respawned = False
    def __init__(self, delay, distance):
        self.respawn_delay = delay
        self.respawn_distance = distance
        
    def remove(self):
        return False
    
    def handle_remove(self):
        cord = self.world.size*TILESIZE/2
        start = Point(cord, cord)
        new_position = self.world.choice_position(self, 10 ,start, ask_player = True)
        
        self.set_position(new_position)
        
        self.alive = True
        self.move_vector = Point()
        self.regid()
        self.respawned = True
        self.spawn()



class DiplomacySubject:
    def __init__(self, fraction):
        self.fraction = fraction
        self.invisible = 0
    
    def set_invisible(self, invisible_time):
        self.invisible = invisible_time
    
    def update(self):
        if self.invisible:
            self.invisible-=1

####################################################################
class Temporary:
    "класс объекта с ограниченным сроком существования"
    def __init__(self, lifetime):
        self.lifetime = lifetime
        self.creation_time = time()
    
    def update(self):
        t = time()
        if t-self.creation_time >= self.lifetime:
            self.to_remove(True)




