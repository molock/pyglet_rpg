#!/usr/bin/env python
# -*- coding: utf-8 -*-
#разделяемое состояние всех объектов игры
from config import *


from weakref import proxy, ProxyType
from random import  choice
from collections import OrderedDict
from threading import Event

from engine.mathlib import Cord, Position, ChunkCord
from engine.enginelib.meta import Guided, HierarchySubject, Respawnable
from engine.enginelib.mutable import MutableObject


        
class __GameSingleton(object):
    "синглтон игрового движка - хранит карты, все объекты, и предоставляет доступ к ним"
    def __init__(self):
        self.guided_players = {} #управляемые игроки
        self.players = {}
        
        self.monster_count = 0
        self.guided_changed = False
        self.stopped = False
        self._active = Event()

    def is_active(self):
        return self._active.is_set()

    def wait(self):
        return self._active.wait()

    def set_activity(self):
        self._active.set()

    def unset_activity(self):
        self._active.clear()

    
    def start(self):
        print('Engine initialization...')
        self_proxy = proxy(self)
        
        self.locations = OrderedDict()
        self.active_locations = {}
        
        self.locations['ground'] = Location(self_proxy, 'ground')
        self.locations['underground'] = Location(self_proxy, 'underground')
        self.locations['underground2'] = Location(self_proxy, 'underground2')
        self.mainlocation = self.locations['ground']
        
        for location in self.locations.values():
            print('location %s initialization' % location.name)
            location.start()
            location.save(True)

        
        
        print('Engine initialization complete. \n')

    def add_active_location(self, location):
        self.active_locations[location.name] = location
        if not self.is_active():
            self.set_activity()

    def remove_active_location(self,location):
        key = location.name
        if key in self.active_locations:
            del self.active_locations[key]

        if not self.active_locations:
            self.unset_activity()
        
    def _new_object(self, player):
        "создает динамический объект"
        assert not isinstance(player, ProxyType)

        if isinstance(player, Guided):  print ('game._new_object', player)
        
        self.players[player.name] = player
         
        if isinstance(player, Guided):
            self.guided_players[player.name] = proxy(player)
                

        
    
    
    def _remove_object(self, player):
        assert player.name in self.players
        name = player.name

        player.handle_remove()
        player.location.pop_object(player)

        if not isinstance(player, Respawnable):
            

            if isinstance(player, Guided):
                print ('game._remove_object', player, force)
                

            del self.players[name]
            
        else:

            player._GameObject__REMOVE = False
            player.regid()
            player.respawned = True
            
            if isinstance(player, MutableObject):
                player.flush()

            chunk_cord = game.mainlocation.main_chunk.cord
            self.mainlocation.add_object(player, chunk_cord)

            player.handle_respawn()




    def remove_guided(self, name):
        print ('\n\n remove_guided', name)
        assert name in self.guided_players

        player = self.guided_players[name]
        del self.guided_players[name]

        player.handle_quit()
        player.location.pop_object(player)

        del self.players[name]
        print 'weak', player





    


    def change_location(self, player, location_name, chunk = None):
        "переметить объект из одного мира в другой"

        assert isinstance(player, ProxyType)

        if isinstance(player, Guided):  print ('game.change_location', player, location_name
        )

        prev_location = player.location

        new_location = self.locations[location_name]
    

        if not chunk:
        #нходим новый чанк
            dest_chunk_cord = choice(new_location.teleports)
        else:
            dest_chunk_cord = chunk
        

        
        #меняем локацию
        prev_location.pop_object(player)
        new_location.add_object(player, dest_chunk_cord)
                
        
        
        if isinstance(player, MutableObject):
            player.flush()
        #обновляем хэш объекта
        player.regid()
        
        if isinstance(player, HierarchySubject):
            for slave in player.get_slaves():
                self.change_location(slave, new_location.name, chunk = dest_chunk_cord)
        
    
    def get_active_chunks(self):
        "список активных локаций"
        for_sum = [list(loc.get_active_chunks()) for loc in self.active_locations.values() if loc.has_active_chunks()]
        return sum(for_sum, [])
    
    def get_guided_list(self, self_name):
        return [player.get_online_tuple(self_name) for player in self.guided_players.values()]
    
    def save(self):
        for location in self.locations.values():
            location.save()

    def stop(self):
        self.stopped = True




game = __GameSingleton()
##кольцевая зависимость
from engine.world.location import Location
