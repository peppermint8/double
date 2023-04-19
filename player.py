#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
To do:
speed adjust function
"""

import math

class Player():
    """player snake"""
    px = (0,0)
    top_left_px = (0,0)
    bottom_right_px = (1,1)
    screen_px = (0,0)
    eye_color = (0,0,0)
    head_size = 15
    tail_size = 5
    color = (0,0,0)

    velocity = 40
    vx = 0 # velocity x
    vy = 0 # velocity y
    xd = 0
    yd = 0
    a = 0.0 # angle of movement in radians

    window_size = 50 # total segments
    xy_list = []

    def __init__(self, px, top_left_px, bottom_right_px):
        self.px = px
        self.top_left_px = top_left_px
        self.bottom_right_px = bottom_right_px
        self.screen_px = (self.bottom_right_px[0] // 2, self.bottom_right_px[1] // 2)
        self.xy_list = []
        #print("new player")
        #self.velocity = 50
    
    def __del__(self):
        pass
        #print("deleted player")


    def arrow_movement(self, direction):
        x0 = self.screen_px[0]
        y0 = self.screen_px[1]
        v = 30 # screen movement velocity

        move_mode = "tronx"

        if move_mode == "tron":
            # like tron lightcycles
            v = 15 # screen movement velocity
            if direction == "up":
                self.vy = -v
                self.vx = 0
            elif direction == "down":
                self.vy = v
                self.vx = 0
            elif direction == "left":
                self.vx = -v
                self.vy = 0
            elif direction == "right":
                self.vx = v
                self.vy = 0
            elif direction in ("up-left", "left-up"):
                self.vx = -v
                self.vy = -v
            elif direction in ("up-right", "right-up"):
                self.vx = v
                self.vy = -v
            elif direction in ("down-left", "left-down"):
                self.vx = -v
                self.vy = v
            elif direction in ("down-right", "right-down"):
                self.vx = v
                self.vy = v

        else:
            #o = 1.2

            if direction == "up":
                y0 = y0 - v
                #x0 = 0    
            elif direction == "down":
                y0 = y0 + v
                #x0 = 0
            elif direction == "left":
                x0 = x0 - v
                #y0 = 0
            elif direction == "right":
                x0 = x0 + v
                #y0 = 0
            elif direction in ("up-left", "left-up"):
                x0 = x0 - v
                y0 = y0 - v
            elif direction in ("up-right", "right-up"):
                x0 = x0 + v
                y0 = y0 - v
            elif direction in ("down-left", "left-down"):
                x0 = x0 - v
                y0 = y0 + v
            elif direction in ("down-right", "right-down"):
                x0 = x0 + v
                y0 = y0 + v
            x0 = int(x0)
            y0 = int(y0)


        x0 = max(0, x0)
        x0 = min(self.bottom_right_px[0], x0)
        y0 = max(0, y0)
        y0 = min(self.bottom_right_px[1], y0)        
        

        if move_mode != "tron":
            self.movement((x0, y0))

        #self.move()

    def movement(self, px):
        """calculate speed based on (x,y) of mouse in window"""
        # xd = -1 .. 1
        # yd = -1 .. 1
        self.screen_px = px

        self.xd = 2*px[0] / self.bottom_right_px[0] - 1
        self.yd = 2*px[1] / self.bottom_right_px[1] - 1
        
        self.vx = int(self.velocity * self.xd)
        self.vy = int(self.velocity * self.yd)
        #print("v = {},{} -- d = {},{}".format(self.vx, self.vy, self.xd, self.yd))

    def move(self):
        """update player px"""

        self.xy_list.append(self.px)
        # moving window
        if len(self.xy_list) > self.window_size:
            self.xy_list = self.xy_list[1:]
        
        x0 = self.px[0]
        y0 = self.px[1]

        x = self.px[0]
        x += self.vx
        x = max(self.top_left_px[0], x)
        x = min(self.bottom_right_px[0], x)

        y = self.px[1]
        y += self.vy
        y = max(self.top_left_px[1], y)
        y = min(self.bottom_right_px[1], y)

        self.px = (x, y)

        dx = x0 - x
        dy = y0 - y
        d = "-"
        if dx > 0 and dy > 0:
            # up - left
            self.a = math.atan(dy/dx) - math.pi/2
            #d = "up-left"
        elif dx > 0 and dy < 0:
            # down - left
            self.a = math.atan(dy/dx) - math.pi/2
            #d = "down-left"
        elif dx < 0 and dy > 0:
            # up - right
            self.a = math.atan(dy/dx) + math.pi/2
            #d = "up-right"
        elif dx < 0 and dy < 0:
            # down - right
            self.a = math.atan(dy/dx) + math.pi/2
            #d = "down-right"
        elif dx == 0 and dy > 0:
            # up = 0
            #d = "up"
            self.a = 0
        elif dx == 0 and dy < 0:
            # down = 180
            #d = "down"
            self.a = math.pi
        elif dx > 0 and dy == 0:
            # left = 270
            #d = "left"
            self.a = 3 * math.pi / 2
        elif dx < 0 and dy == 0:
            # right = 90
            #d = "right"
            self.a = math.pi / 2
        
        #print("d = {}, dx,dy = {},{}, angle: {:.1f}".format(d, dx, dy, math.degrees(self.a)))
