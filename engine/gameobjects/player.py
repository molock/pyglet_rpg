#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.engine_lib import *
from engine.mathlib import chance
from engine.gameobjects.units_lib import *
from engine.gameobjects.shells import Ball
from engine.gameobjects.movable import Movable
from engine.gameobjects.skills import *
from engine.gameobjects.map_observer import MapObserver


class Player(Respawnable, Unit, MapObserver, Striker, Guided, Stats, Skill):
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
        Stats.__init__(self)
        Skill.__init__(self,100)
    
    def accept(self):
        yield  self.look_map()
        yield self.look_events()
        
    def handle_response(self):
        location = game.get_location(self.position)
        
        if self.respawned:
            yield Respawnable.handle_response(self)
        
        if self.position_changed:
            yield self.camera_move()
        
        if self.cord_changed:
            yield self.look_map()
    
        if location.check_events():
            yield self.look_events()
        
        #if location.check_static_events():
        yield self.look_static()
        
        if self.stats_changed:
            yield self.get_stats()

 
    
    def camera_move(self):
        return ('MoveCamera', Movable.handle_request(self))
        
    def look_static(self):
        static_objects, static_events = MapObserver.look_static(self)
        return ('LookStatic', (static_objects, static_events))
    
    def look_events(self):
        events = MapObserver.look_events(self)
        return ('LookObjects', (events,))
    
    def look_map(self):
        new_looked, observed = MapObserver.look_map(self)
        return ('LookLand', (new_looked, observed))
    
    def get_stats(self):
        return ('PlayerStats', Stats.get_stats(self))
        
    @wrappers.action
    @wrappers.alive_only()
    def Strike(self, vector):
        self.strike_ball(vector)
    
    @wrappers.action
    @wrappers.alive_only()
    def Move(self, vector):
        Movable.move(self, vector)
    
    @wrappers.action
    def Look(self):
        return MapObserver.look(self)
    
    @wrappers.action
    def Skill(self):
        self.skill()
    

    
    @wrappers.alive_only(Deadly)
    def update(self):
        Movable.update(self)
        Striker.update(self)
        Deadly.update(self)
        Stats.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
