#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *
from items import SkillBall

class Skill:
    def __init__(self):
        self.skills = 5
        self.directs = (Point(1,0), Point(-1,0), Point(0,-1), Point(0,1),
                        Point(1,1), Point(1,-1), Point(-1,1), Point(-1,-1),
                        Point(2,1), Point(2,-1), Point(-2,1), Point(-2,-1),
                        Point(1,2), Point(1,-2), Point(-1,2), Point(-1,-2))
    
    def skill(self):
        if self.skills>0:
            for direct in self.directs:
                ball_name = 'ball%s' % game.ball_counter
                game.ball_counter+=1
                ball = SkillBall(ball_name, self.position, direct, self.fraction, self.name, self.damage)
                game.new_object(ball)
            self.skills-=1
    
    def plus_skill(self):
        self.skills+=1

