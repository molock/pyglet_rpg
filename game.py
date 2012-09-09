#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyglet
from pyglet.image.codecs.png import PNGImageDecoder
from pyglet.gl import *


from os import listdir
from math import hypot
from sys import exit

from engine_lib import Game
from math_lib import Point
from gui_lib import TimerObject, Drawable, InputHandle
from map_lib import Map
from client_lib import Client
from protocol_lib import *




from config import *

class GameWindow():
    "разделяемое состояние элементов gui"
    @staticmethod
    def configure(size):
        cls = GameWindow
        cls.size = size
        cls.window_size = size
        cls.center = Point(cls.window_size/2,cls.window_size/2)
        print 'window center',cls.center
        cls.rad = (size/2)
        cls.clock_setted = False
        cls.complete = 0
        
    @staticmethod
    def gentiles():
        cls = GameWindow
        names = listdir('images')
        cls.tiledict = {}
        for name in names:
            image = pyglet.image.load('images/%s' % name, decoder=PNGImageDecoder()).get_texture()
            cls.tiledict[name[:-4]] = image
    @staticmethod
    def create_tile(point, tilename):
        "создае тайл"
        return (tilename, point.get())
    
    @staticmethod
    def set_position(position):
        GameWindow.position = position


        
        

class Gui(GameWindow, TimerObject, Client, InputHandle, pyglet.window.Window): 
    def __init__(self,size):
        pyglet.window.Window.__init__(self, size, size)
        TimerObject.__init__(self)
        InputHandle.__init__(self)
        Client.__init__(self)
        
        self.configure(size)
        self.gentiles()
        self.objects = ObjectsView()
        self.shift = Point(0,0)
        self.vector = Point(0,0)
        
        self.fps_display = pyglet.clock.ClockDisplay()
        
        #net
        world_size, position, tiles, objects = self.wait_for_accept()
        
        print 'accepteed'

        self.land = LandView(world_size, position, tiles)
        self.objects.insert(objects)
        
    def send_vector(self, vector):
        self.send(vector)
    
    def update(self, dt):
        self.loop()
        delta = self.get_delta()
        vector = self.shift*delta
        if vector> self.shift:
            vector = self.shift
        self.shift = self.shift - vector
        self.land.move_position(vector)
        self.land.update()
        self.objects.update(delta)
        
    def force_complete(self):
        "завершает перемщение по вектору"
        if self.shift:
            print self.shift
            self.land.move_position(self.shift)
            self.shift = Point(0,0)
            self.land.update()
            self.objects.update(0)
    
    def round_update(self, dt):
        "обращение к движку"
        self.force_complete()
        #net
        
        for message in self.in_messages:
            move_vector, newtiles, objects, objects_update = message
            #/net
            self.shift += move_vector
    
            self.land.update()
            self.land.insert(newtiles)
            self.objects.insert(objects, objects_update)
        self.in_messages = []
        self.set_timer()
        logger.debug('>\n')
        

        
    def on_draw(self):
        "прорисовка спрайтов"
        #включаем отображение альфа-канала
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.clear()
        self.land.draw()
        self.objects.draw()
        self.fps_display.draw()
        
    def run(self):
        "старт"
        print 'loop'
        pyglet.clock.schedule(self.update)
        pyglet.clock.schedule_interval(self.round_update, self.timer_value)
        
        pyglet.app.run()
    
    def on_close(self):
        print 'closing'
        self.close_conn()
        exit()


class LandView(GameWindow,  Drawable, Map):
    "клиентская карта"
    def __init__(self, world_size, position, tiles = []):
        Drawable.__init__(self)
        size = world_size
        self.world_size = world_size
        print 'clientworld size', size
        self.map = [[None for j in xrange(size)] for i in xrange(size)]
        self.tiles = []
        if tiles:
            self.insert(tiles)
        self.set_position(position)
        
    def move_position(self, vector):
        "перемещаем камеру"
        self.set_position(self.position + vector)
        
    def insert(self, tiles):
        "обновляет карту, добавляя новые тайлы, координаты - расстояние от стартовой точки"
        for point, tile_type in tiles:
            self.map[point.x][point.y] = tile_type
            
    def look_around(self, rad):
        "список тайлов в поле зрения (координаты в тайлах от позиции камеры, тип)"
        rad = int(rad/TILESIZE)+2
        I,J = (self.position/TILESIZE).get()
        looked = set()
        for i in xrange(I-rad, I+rad):
            for j in xrange(J-rad, J+rad):
                i,j = self.resize(i), self.resize(j)
                try:
                    tile_type = self.map[i][j]
                except IndexError:
                    tile_type = False
                if not tile_type:
                    tile_type = 'fog'
                point = (Point(i,j)*TILESIZE)-self.position
                looked.add((point, tile_type))
        i, j = self.position.get()
        return looked
        
    def update(self):
        "обноление на каждом фрейме"
        looked = self.look_around(self.rad)
        logger.debug('looked len %s' % len(looked))
        self.tiles = [self.create_tile(point+self.center, tile_type) for point, tile_type in looked]



class ObjectsView(GameWindow, Drawable):
    def __init__(self):
        Drawable.__init__(self)
        self.objects = {}
        self.tiles = []
        self.updates = {}
    
    def insert(self, new_objects, updates=None):
        if updates:
            for object_name, vector in updates.items():
                if object_name in self.updates:
                    self.updates[object_name] += vector
                else:
                     self.updates[object_name] = vector
        if new_objects:
            for object_name, (position, tilename) in new_objects.items():
                self.objects[object_name] = {'position':position,'tilename': tilename}

            
    def update(self, delta):
        if self.updates:
            for object_name, vector in self.updates.items():
                if delta:
                    move_vector = vector * delta
                    if move_vector>vector:
                        move_vector = vector
                else:
                    move_vector = vector
                if  vector:
                        self.objects[object_name]['position']+= move_vector
                        self.updates[object_name]-= move_vector
        
        #отображение объектов
        self.tiles = []
        for object_name, game_object in self.objects.items():
            point = game_object['position']
            #проверяем находится ои объект в радиусе обзора
            diff = hypot(self.position.x - point.x, self.position.y - point.y) - self.rad*TILESIZE
            if diff<0:
                tilename = game_object['tilename']
                position = point - self.position +self.center - Point(TILESIZE/2,TILESIZE/2)
                tile = self.create_tile(position, tilename)
                self.tiles.append(tile)
    




    
def main():
    g = Gui(size=600)
    g.run()
if __name__=='__main__':
    if PROFILE:
        import cProfile, pstats
        cProfile.run('main()', '/tmp/game_pyglet.stat')
        stats = pstats.Stats('/tmp/game_pyglet.stat')
        stats.sort_stats('cumulative')
        stats.print_stats()
    else:
        main()

