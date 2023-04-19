#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import random
import pygame
import math

CZ = 3 * math.pi / 4 # to adjust for screen
# rotate(r, 100, cx, cy)
# r = radians

def rotate(r, size, cxy):
    r0 = r - CZ
    
    x = math.cos(r0) * size - math.sin(r0) * size + cxy[0]
    y = math.sin(r0) * size + math.cos(r0) * size + cxy[1]

    x = int(x)
    y = int(y)
    return (x,y)


def convert_color(color_str):
    clr = (0, 0, 0)
    if not color_str:
        return get_rgb()

    if not color_str.startswith("#"):
        color_str = "#" + color_str
    
    clr = pygame.Color(color_str)

    return clr


def get_coco_rgb():
    """
TRS-80 Color Computer colors
black text = 183018
green      = 00ff00 cls(1)
yellow     = ffff44 cls(2)
blue       = 2211bb cls(3)
red        = bb0022 cls(4)
white      = ffffff cls(5)
cyan       = 00dd66 cls(6)
pink       = ff11ff cls(7)
orange     = ff4400 cls(8)

    """

    rgb = random.choice(["#000000", "#00ff00", "#ffff44", "#2211bb", "#bb0022", "#ffffff", "#00dd66", "#ff11ff", "#ff4400"])

    return convert_color(rgb)

def get_rgb():
    rgb = (random.randint(1,255), random.randint(1,255), random.randint(1,255))
    return rgb 

def overlap_segments(px1, px2, px3, px4):
    """do segments a (px1, px2) and b (px3, px4) overlap"""
    # px = (x,y)

    x0 = px1[0]
    x1 = px2[0]
    x2 = px3[0]
    x3 = px4[0]

    x_overlap = overlap(x0, x1, x2, x3)

    y0 = px1[1]
    y1 = px2[1]
    y2 = px3[1]
    y3 = px4[1]

    y_overlap = overlap(y0, y1, y2, y3)

    return x_overlap and y_overlap



def overlap(a, b, c, d):
    """
1 ......... 8
      5 ....... 13

a ----------- b
      c -------- d

           a--b
                    c--d


a between c&d or b between c&d

a < c or b < d
c < a


    """
    segment_overlap = False
    
    a0 = min(a,b)
    b0 = max(a,b)
    c0 = min(c,d)
    d0 = max(c,d)

    # c between a&b or d between a&b
    t1 = a0 <= c0 <= b0 or a0 <= d0 <= b0 
    # a between c&d or b between c&d
    t2 = c0 <= a0 <= d0 or c0 <= b0 <= d0 

    segment_overlap = t1 or t2

    return segment_overlap

def is_point_in_polygon(point, polygon):
    """Return True if a point is inside a polygon, and False otherwise."""
    # ChatGPT-3 - 2023-04-03
    # bug - point may be outside polygon but in bounding box
    x, y = point
    
    # Check if point is outside the bounding box of the polygon
    min_x, min_y, max_x, max_y = polygon[0][0], polygon[0][1], polygon[0][0], polygon[0][1]
    for i in range(1, len(polygon)):
        if polygon[i][0] < min_x:
            min_x = polygon[i][0]
        if polygon[i][1] < min_y:
            min_y = polygon[i][1]
        if polygon[i][0] > max_x:
            max_x = polygon[i][0]
        if polygon[i][1] > max_y:
            max_y = polygon[i][1]
    if x < min_x or x > max_x or y < min_y or y > max_y:
        return False
    
    # Check if point is inside the polygon
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        if ((polygon[i][1] > y) != (polygon[j][1] > y)) and \
           (x < (polygon[j][0] - polygon[i][0]) * (y - polygon[i][1]) / (polygon[j][1] - polygon[i][1]) + polygon[i][0]):
            inside = not inside
        j = i
    return inside

def get_bonus_mult(capture_cnt):
    """give player bonus if more than one item in the polygon"""
    bonus_mult = 1
    if capture_cnt in (2,3):
        bonus_mult = 2
    elif capture_cnt == 4:
        bonus_mult = 3
    elif capture_cnt > 4:
        bonus_mult = 4


    return bonus_mult                        
