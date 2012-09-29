#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.mathlib import Point, NullPoint

from pyglet.window.key import UP, DOWN, LEFT, RIGHT, RSHIFT, SPACE

class InputHandle:
    "перехват устройств ввода"
    pressed = {}
    MOVE_BUTTON = 1
    STRIKE_BUTTON = 4
    control_keys = [UP, DOWN, LEFT, RIGHT, RSHIFT, SPACE]
    striking = False
    
    def __init__(self):
        self.step = TILESIZE/2
        self.vector = NullPoint
        self.vectors = {UP:Point(0,self.step), DOWN: Point(0,-self.step),
               LEFT : Point(-self.step,0), RIGHT : Point(self.step,0)}
            
    def on_key_press(self, symbol, modifiers):
        "движение с помощью клавиатуры"
        if symbol in self.control_keys:
            self.pressed[symbol] = True
            if symbol==SPACE:
                self.send_skill()
            
    def on_key_release(self, symbol, modifiers):
        if symbol in self.control_keys:
            del self.pressed[symbol]
        
    def on_mouse_press(self, x, y, button, modifiers):
        "перехватывавем нажатие левой кнопки мышки"
        #левая кнопка - движение
        if button==self.MOVE_BUTTON:
            self.vector = (Point(x,y) - self.center)
            
            
        elif button==self.STRIKE_BUTTON:
            vector = (Point(x,y) - self.center)
            self.send_ball(vector)
            self.striking = vector
    
    def on_mouse_release(self, x, y, button, modifiers):
        if button==self.MOVE_BUTTON:
            self.vector = False
        elif button==self.STRIKE_BUTTON:
            self.striking = False
    
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if button==self.MOVE_BUTTON:
            self.vector = (Point(x,y) - self.center)
        elif button==self.STRIKE_BUTTON:
            self.striking = (Point(x,y) - self.center)
            
        
    
    def handle_input(self):
        self.step = self.stats.speed
        if self.pressed:
            #получаем список векторов соответствующим нажатым клавишам
            if RSHIFT in self.pressed:
                speed = 2
            else:
                speed = 1
            vectors = [self.vectors[symbol] for symbol in self.pressed if symbol in self.vectors]
            #получаем их сумму и если она не равна нулю - посылаем
            vector = sum(vectors, Point(0,0))*speed
            if vector:
                self.send_move(vector)
        elif self.vector:
            self.send_move(self.vector)
        if self.striking:
            self.send_ball(self.striking)