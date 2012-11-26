#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from clientside.gui.window import create_tile, create_label

from share.point import Point

from inspect import getmro
from collections import namedtuple

sprite_size = namedtuple('sprite_size',['width','height'])

class ActionError(BaseException):
    pass


class ClientObject:
    @classmethod
    def init_cls(cls, surface):
        cls.surface = surface
    def __init__(self, name, position):
        self.position = position
        self.name = name
        self.delayed = False
        self._REMOVE = False
        sprite = self.surface.tiledict[self.tilename]
        self.sprite = sprite_size(sprite.width, sprite.height)
    
    def handle_action(self, action, args):
        if hasattr(self, action):
            try:
                getattr(self, action)(*args)
            except TypeError as error:
                print self.name, action, args
                raise error
        else:
            raise ActionError('no action %s.%s' % (self.__class__.__name__, action))
    
    def update(self, delta):
        pass
    
    def force_complete(self):
        pass
        
    
    
    def remove(self):
        self._REMOVE = True

    def round_update(self):
        pass

    def hover(self):
        pass

    def unhover(self):
        pass

    def _delay(self):
        self._remove_time = time()

    def _is_alive(self):
        return time() - self._remove_time < 5


class StaticObject(ClientObject):
    def __init__(self, name, position):
        ClientObject.__init__(self, name, position)
        
        self.hovered = False
    
    
    def hover(self):
        self.hovered = True
    
    def draw(self):
        
        return [create_tile(self.position, self.tilename, -1, hover=self.hovered)]
    

    def unhover(self):
        self.hovered = False
    


class DynamicObject(ClientObject):
    REMOVE = False
    "класс игрового объекта на карте"
    def __init__(self, name, position):
        ClientObject.__init__(self, name, position)
        
            
    def draw(self):
        return [create_tile( self.position, self.tilename)]
        
    



class MapAccess:
    pass


class Animated:
    "класс для анимированных объектов"
    def __init__(self):
        if not hasattr(self, 'init'):
            self.init = True
            self.animations = {}
        
    def create_animation(self, name, tilename, frames, freq, repeat = True):
        frames-=1
        self.animations[name] = {}
        self.animations[name]['counter'] = 0
        self.animations[name]['tilename'] = tilename
        self.animations[name]['frames'] = frames #количество кадров на анимацию
        self.animations[name]['freq'] = freq #количество кадров на каждый кадр анимации
        self.animations[name]['frame_counter'] = 0 #счетчик фреймов текущего кадра 
        self.animations[name]['repeat?'] = repeat
        self.animations[name]['repeated'] = False
        self.animations[name]['prev_frame'] = 0
        
        
    
    def get_animation(self, name):
        freq = self.animations[name]['freq']
        tilename = self.animations[name]['tilename']
        repeated = self.animations[name]['repeated']
        need_repeat = self.animations[name]['repeat?']
        prev_frame = self.animations[name]['prev_frame']
        
        if repeated and not need_repeat:
            n = self.animations[name]['frames']
        else:
            if self.animations[name]['frame_counter']<freq:
                self.animations[name]['frame_counter']+=1
            else:
                self.animations[name]['frame_counter'] = 0
                frames = self.animations[name]['frames']
                if self.animations[name]['counter'] < frames-1:
                    self.animations[name]['counter']+=1
                else:
                    if not self.animations[name]['repeat?']:
                        self.animations[name]['repeated'] = True
                    self.animations[name]['counter'] = 0
            
            n = self.animations[name]['counter']
            
            
        tilename = '_'+tilename+'_%s' % n

        return tilename
    
#
class Movable(Animated, DynamicObject):
    def __init__(self, frames=1):
        Animated.__init__(self)
        self.moving = False
        self.vector = Point(0,0)
        self.create_animation('moving', 'move', frames,2)

    def get_vector(self):
        return self.vector
    
    def move(self, xy):
        vector = Point(*xy)
        self.vector += vector
        if self.vector:
            self.moving = True
            
            
    def draw(self):
        position = self.position
        if self.moving:
            tilename = self.tilename + self.get_animation('moving')
        else:
            tilename = self.tilename
        return [create_tile(position, tilename)]

    def update(self, delta):
        if self.vector:
            move_vector = self.vector * delta
            if move_vector>self.vector:
                move_vector = self.vector
            self.position += move_vector
            self.vector -=move_vector
        else:
            self.moving = False
    
    def round_update(self):
        self.moving = False
    
    def force_complete(self):
        if self.vector:
            self.position+=self.vector
            self.vector = Point(0,0)



class Fighter(Animated):
    def __init__(self, frames):
        Animated.__init__(self)
        self.create_animation('attack', 'attack', frames,3)
        self.attacking = False
    
    def attack(self):
        self.attacking = True
    
    def draw(self):
        tilename = self.tilename + self.get_animation('attack')
        return [create_tile(self.position, tilename)]
    
    def round_update(self):
        self.attacking = False
            
class Sweemer(MapAccess):
    def update(self, delta):
        i,j = (self.position/TILESIZE).get()
        if MapAccess.map[i][j]=='water':
            self.inwater= True
            self.prefix = '_water'
        else:
            self.inwater = False
            self.prefix = ''
    

class Breakable(Animated):
    def __init__(self, hp_value, hp,frames):
        Animated.__init__(self)
        self.dead = False
        self.defended = False
        
        self.hp = hp
        self.hp_value = hp_value
        
        self.create_animation('death', 'die', frames, 3)
        self.create_animation('defend', 'defend', 2, 3)
    
    def change_hp(self, hp_value, hp):
        self.hp = hp
        self.hp_value = hp_value
    
    def draw(self):
        position = self.position
        if self.dead:
            tilename = self.tilename + self.get_animation('death')
        else:
            tilename = self.tilename + self.get_animation('defend')
        
        sprite = create_tile(position, tilename, -1 )
        return [sprite]
    
    def draw_label(self):
        label = create_label('%d/%d' % (self.hp, self.hp_value), self.position+Point(0, self.sprite.height))
        return [label]
    
    def die(self):
        self.dead = True
    
    def defend(self):
        self.defended = True
    
    def round_update(self):
        self.defended = False
