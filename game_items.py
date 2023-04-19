#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
Image action ideas
pulse image - transform scale increase & decrease
flip left and right for no good reason
"""

import random
import pygame


class GameItem():
    """images to represent game items"""
    px = (0,0) # top left
    center = (0,0)
    size_px = (0,0) # w x h
    padding = 25
    top_left_px = (0,0)
    bottom_right_px = (10,10)
    value = 100 # score

    img_list = [] # list of images
    game_img_list = [] # pygame images
    img_index = 0 # which image to use in the list
    game_img = None
    item_name = "unknown" # identifier
    tick = 0
    

    velocity = 0
    move_style = ""
    motion = (0,0)
    move_limit = 1
    move_cnt = 0
    angle = 0
    rotation_v = 0 # velocity of rotation (angle)

    create_sound = ""
    delete_sound = ""

    def __init__(self, item_key, item_json, top_left_px, bottom_right_px, px=(0,0)):

        self.item_name = item_key
        self.value = item_json.get("value", random.choice([50, 75, 100, 125, 150, 200]))
        self.size_px = (item_json.get("size_x", 25), item_json.get("size_y", 25))

        self.img = item_json.get("image")
        self.img_list = item_json.get("image_list", [])

        self.flip_flag = random.choice([True, False])
        self.img_ticks = item_json.get("image_change_ticks", 5)

        self.img_index = -1
        if item_json.get("image"):
            self.img_list = [item_json.get("image")]
            self.img_index = 0
        if item_json.get("image_list"):
            self.img_list = item_json.get("image_list")
            self.img_index = 0
        

        self.load_imgs()

        # need to place between padding and account for size
        self.padding = item_json.get("padding", 25)
        self.top_left_px = top_left_px
        self.bottom_right_px = bottom_right_px

        if px == (0,0):
            self.get_new_px()
        else:
            self.px = px
        
        self.center = (self.px[0] + self.size_px[0] // 2, self.px[1] + self.size_px[1] // 2)

        self.velocity = item_json.get("velocity", 0)
        self.move_style = item_json.get("move_style", "")
        self.move_limit = item_json.get("move_limit", 10) # ticks per move
        self.rotation_v = item_json.get("rotate", 0)
        self.rotation_v = random.choice([self.rotation_v, -1*self.rotation_v]) # random direction
        self.create_sound = item_json.get("create_sound")
        self.delete_sound = item_json.get("delete_sound")

        print("Created: {} @ {}".format(self.item_name, self.px))


    def get_new_px(self): 
        x0 = self.top_left_px[0] + self.padding
        x1 = self.bottom_right_px[0] - self.padding - self.size_px[0]
        #print("x = [{}, {}]".format(x0, x1))
        x_pos = random.randint(x0, x1)
        y0 = self.top_left_px[1]+self.padding
        y1 = self.bottom_right_px[1]-self.padding-self.size_px[1]
        #print("y = [{}, {}]".format(y0, y1))
        y_pos = random.randint(y0, y1)
        self.px = (x_pos, y_pos)

        self.center = (self.px[0] + self.size_px[0] // 2, self.px[1] + self.size_px[1] // 2)

    def __del__(self):
        print("Deleted: {}".format(self.item_name))

    def load_imgs(self):
        self.game_img_list = []
        for this_img in self.img_list:
            pygame_img = pygame.image.load(this_img)
            pygame_img = pygame.transform.scale(pygame_img, self.size_px)
            
            #if self.rotation_v > 0:
            #    pygame_img = pygame.transform.rotate(pygame_img, self.angle)

            if self.flip_flag:
                pygame_img = pygame.transform.flip(pygame_img, True, False)
            
            self.game_img_list.append(pygame_img)

        # self.img_index = random.randint(0, len(self.game_img_list)-1)
        self.game_img = self.game_img_list[self.img_index]
    

    def action(self, target_px):
        self.tick += 1
        if self.tick % self.move_limit:
            self.angle += self.rotation_v
            if self.angle > 360:
                self.angle = 0
            elif self.angle < 0:
                self.angle = 360


        if self.tick % abs(self.img_ticks) == 0:
            self.img_index += 1
            if self.img_index >= len(self.game_img_list):
                self.img_index = 0
            self.game_img = self.game_img_list[self.img_index]

            if self.rotation_v != 0:
                #self.game_img = pygame.transform.rotate(self.game_img, self.angle)
                self.game_img = pygame.transform.rotozoom(self.game_img, self.angle, 1.0)

        # movement, pulsing, color changing?
        if self.move_style:
            new_x = self.px[0]
            new_y = self.px[1]
            if self.move_style.startswith("horiz"):
            
                if new_x < target_px[0]:
                    new_x += self.velocity
                elif new_x == target_px[0]:
                    new_x += 0                    
                else:
                    new_x -= self.velocity

            if self.move_style.startswith("vert"):
                if new_y < target_px[1]:
                    new_y += self.velocity
                elif new_y == target_px[1]:
                    new_y += 0
                else:
                    new_y -= self.velocity

            if self.move_style.startswith("targ"):
                if new_x < target_px[0]:
                    new_x += self.velocity
                elif new_x == target_px[0]:
                    new_x += 0
                else:
                    new_x -= self.velocity


                if new_y < target_px[1]:
                    new_y += self.velocity
                elif new_y == target_px[1]:
                    new_y += 0                    
                else:
                    new_y -= self.velocity
                
            # random moves
            if self.move_style == "random-xy":
                
                if self.tick >= self.move_cnt:
                    self.move_cnt = random.randint(1, self.move_limit)
                    self.motion = random.choice([(1,0), (-1,0), (0,1), (0, -1)])
                    self.tick = 0

                new_x += self.motion[0] * self.velocity
                new_y += self.motion[1] * self.velocity

            if self.move_style == "random-x":
                if self.tick >= self.move_cnt:
                    self.move_cnt = random.randint(1, self.move_limit)
                    self.motion = random.choice([(1,0), (-1,0)])
                    self.tick = 0

                new_x += self.motion[0] * self.velocity
                

            if self.move_style == "random-y":
                if self.tick >= self.move_cnt:
                    self.move_cnt = random.randint(1, self.move_limit)
                    self.motion = random.choice([(0,1), (0,-1)])
                    self.tick = 0

                
                new_y += self.motion[1] * self.velocity                

            # just up and down w/o following target
            # just horiz w/o following target

            # within bounds?
            
            new_x = max(self.top_left_px[0] + self.padding, new_x)
            new_x = min(self.bottom_right_px[0] - self.padding - self.size_px[0], new_x)
            
            new_y = max(self.top_left_px[1] + self.padding, new_y)
            new_y = min(self.bottom_right_px[1] - self.padding - self.size_px[1], new_y)

            self.px = (new_x, new_y)
            self.center = (int(new_x + self.size_px[0] / 2), int(new_y + self.size_px[1]/2))    

    # is x in px (0,0) to px+size_px?
    def hit(self, player_px):

        if self.px[0] <= player_px[0] <= self.px[0] + self.size_px[0]:
            if self.px[1] <= player_px[1] <= self.px[1] + self.size_px[1]:
                return True

        return False


class TextObj():
    """menu text"""
    px = (0,0)
    text = ""
    color = (0,0,0)
    font = ""

    text_item = None
    rect = None

    def __init__(self, text, px, color, font):
        self.text = text
        self.color = color
        self.px = px
        self.font = font
        self.render()

    def render(self):
        self.text_item = self.font.render(self.text, 1, self.color)
        # option for non-center?
        self.rect = self.text_item.get_rect(center=self.px)
        #bg.blit(menu_text, txt_xy)


class TxtMsg():
    """store text messages"""
    px = (0,0)

    tick = 0 # time
    txt = ""
    fade = 5
    max_tick = 10
    color = (0,0,0)
    a = 255
    def __init__(self, px, value, color, max_tick, fade):

        self.px = px
        self.tick = 0
        self.txt = str(value)
        self.color = color
        self.max_tick = max_tick
        self.fade = fade

    def action(self):
        self.tick += 1
        if self.tick <= self.max_tick:
            # color fade to black - not to bg color
            # can we do transparency?
            r = self.color[0]
            g = self.color[1]
            b = self.color[2]
            if self.fade < 0:
                self.a = self.a + self.fade
                self.color = (r, g, b, self.a)
            else:
                r = max(0, r - self.fade)
                g = max(0, g - self.fade)
                b = max(0, b - self.fade)
                self.color = (r, g, b)

