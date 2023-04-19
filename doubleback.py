#!/usr/bin/env python
#! -*- coding: utf-8 -*-

"""
Doubleback 2
Based on the TRS-80 Doubleback game, 1982 Dale Lear Licenced to Tandy

Example
http://www.lcurtisboyle.com/nitros9/doubleback.html


To do:
- prevent object from appearing to close to player
- player 2 keyboard - better movement
- high score
- game icon
- sounds if none


bugs
- rotating objects & collisions
- lives not decrementing

"""

import pygame
from pygame.locals import *

import sys
import random
import os
import time
import yaml
import math
import copy

from common import overlap_segments, get_rgb, is_point_in_polygon, get_bonus_mult, \
convert_color, get_coco_rgb, rotate
from player import Player
from game_items import GameItem, TxtMsg, TextObj
from dconst import *
from menu import title_screen


def check_px(i_px, p1_px, p2_px):
    """if item_px within p1_px or p2_px + padding then return True"""
    # trying to prevent items popping up in front of player unfairly
    #print(i_px, p1_px, p2_px)
    padding = 25
    if p1_px[0] - padding < i_px[0] < p1_px[0] + padding and p1_px[1] - padding < i_px[1] < p1_px[1] + padding:
        return True

    if p2_px[0] - padding < i_px[0] < p2_px[0] + padding and p2_px[1] - padding < i_px[1] < p2_px[1] + padding:
        return True

    return False


def get_next_level(level_name):
    """get info for the next level"""
    level_data = game_config["game_levels"].get(level_name, {})

    next_level_score = level_data.get("next_level_score", 10000000)

    level_items = level_data.get("item_list", [])
    if not level_items:
        # get them all
        for i in game_item_data:
            if game_item_data[i]['status']:
                level_items.append(i)


    a = level_data.get("min_delay", 0)
    b = level_data.get("max_delay", 200)

    max_item_cnt = level_data.get("max_items", 5)
    next_level = level_data.get("next_level", level_name)
    level_msg = level_data.get("level_msg", "")

    return level_items, a, b, max_item_cnt, next_level_score, next_level, level_msg


def draw_player(p, bg, draw_eyes=True):
    """draw player snake"""
    # turn off eyes for sometimes
    if len(p.xy_list) > 2:
        pygame.draw.lines(bg, p.color, False, p.xy_list, p.tail_size)

    # player head
    pygame.draw.circle(bg, p.color, p.px, p.head_size, 0)

    if draw_eyes:
        # left eye
        hxy = rotate(p.a + math.pi/2, 6, p.px)
        pygame.draw.circle(bg, (255,255,255), hxy, 8, 0)
        pygame.draw.circle(bg, p.eye_color, hxy, 5, 0)
        # right eye
        hxy = rotate(p.a - math.pi/2, 6, p.px)
        pygame.draw.circle(bg, (255,255,255), hxy, 8, 0)
        pygame.draw.circle(bg, p.eye_color, hxy, 5, 0)
    
    # nose
    hxy = rotate(p.a, 10, p.px)
    pygame.draw.circle(bg, p.color, hxy, 6, 0)


def crash(crash_sound, screen, bg, plr, bg_color):
    """crash animation"""
    # Snake shakes
    pygame.mixer.Sound.play(crash_sound)

    p_old_color = plr.color
    p_old_head_size = plr.head_size
    crash_flag = True

    c = 0
    # copy p - create shallow copy with new values
    p0 = copy.copy(plr)
    
    # erase original player, easy way to do it
    p0.color = bg_color
    draw_player(p0, bg, False)

    # copy current background
    bg0 = bg.copy()


    while crash_flag:
        c += 1

        p0.color = get_rgb()
        #p.color = random.choice([(255,255,255), (0,0,0), (128,128,128), (192,192,192)])
        p0.head_size = random.randint(5,8)
        
        new_tail = []    
        for px in p0.xy_list:
            r = random.choice([1,2,3])
            dx = random.choice([(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1, -1), (0,0)]) 

            x0 = px[0] + dx[0] * r
            y0 = px[1] + dx[1] * r
            new_tail.append((x0, y0))
            
        p0.xy_list = new_tail

        # head random px
        dx = random.choice([(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1, -1), (0,0)]) 

        x0 = px[0] + dx[0] * r
        y0 = px[1] + dx[1] * r        
        p0.px = (x0, y0)

        # reset game screen
        bg.blit(bg0, (0,0))
    

        # p.eye_size & stuff+-
        draw_player(p0, bg)

        screen.blit(bg, (0, 0))
        pygame.display.flip()

        if c > 150:
            crash_flag = False

    # p.x & y = re-center
    plr.color = p_old_color
    plr.head_size = p_old_head_size
    

def game_over(p1_score, p2_score, game_over_sound, txt_pos, screen, bg):
    """game over screen"""

    if game_over_sound:
        pygame.mixer.Sound.play(game_over_sound)

    high_score_file = game_config.get("high_score_file")
    if high_score_file:
        with open(high_score_file, "a", encoding="utf-8") as fh:
            fh.write("{},{}\n".format(p2_score, game_config.get("player", {}).get("p1_name", "Player 1")))
            if p2_score > 0:
                fh.write("{},{}\n".format(p2_score, game_config.get("player", {}).get("p2_name", "Player 2")))
    
    game_over_font = pygame.font.Font(game_config.get("game_font"), game_config.get("game_over_font_size", 64))
    game_over_str = game_config.get("game_over_txt", "Game Over")

    text_color = get_coco_rgb()    
    game_over_text = game_over_font.render(game_over_str, 1, text_color)

    txt_xy = game_over_text.get_rect(center=txt_pos)

    render_flag = True
    done = False
    cnt = 0
    while not done:
        cnt += 1

        if cnt % 64 == 0:
            text_color = get_coco_rgb()
            game_over_text = game_over_font.render(game_over_str, 1, text_color)
            render_flag = True


        if render_flag:
            
            bg.blit(game_over_text, txt_xy)
            render_flag = False

            screen.blit(bg, (0, 0))
            pygame.display.flip()




        for event in pygame.event.get():

            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:
                # any key will exit to menu
                #if event.key == K_ESCAPE:
                done = True



def init_screen():
    max_x = game_config.get("window_x", 600)
    max_y = game_config.get("window_y", 600)
    
    # init screen - should do this all before this
    pygame.mixer.pre_init(44100, 16, 2, 4096)
    
    pygame.init()
    screen = pygame.display.set_mode((max_x, max_y))

    #game_icon = pygame.image.load(os.path.join(img_path, "101664.png"))
    #pygame.display.set_icon(game_icon)
    pygame.display.set_caption(game_config.get("title"))
    pygame.mouse.set_visible(False)

    return screen


def run_game(screen, player_cnt):

    max_x = game_config.get("window_x", 600)
    max_y = game_config.get("window_y", 600)
    
    clock_tick = 15
    #pygame.key.set_repeat(1, 500)

    screen_top_left_px = (0,10)
    screen_bottom_right_px = (max_x, max_y-25)

    
    clock = pygame.time.Clock()

    # begin in center of screen
    p1_pos = (max_x // 2, max_y // 2)
    if player_cnt == 2:
        p1_pos = (max_x // 4, max_y // 2)
    p = Player(p1_pos, screen_top_left_px, screen_bottom_right_px)
    p.color = convert_color(game_config.get("player", {}).get("p1_color", "00FF00"))
    

    p.head_size = game_config.get("player", {}).get("head_size", 10)
    p.tail_size = game_config.get("player", {}).get("tail_width", 3)
    p.tail_length = game_config.get("player", {}).get("tail_length", 30)

    p.eye_color = convert_color(game_config.get("player", {}).get("p1_eye_color", (0,0,0)))
    p1_lives = min(game_config.get("player", {}).get("lives", 3), 255)

    # player 2
    p2_pos = (-20, -20)
    if player_cnt == 2:
        p2_pos = (3 * max_x // 4, max_y // 2)
    p2 = Player(p2_pos, screen_top_left_px, screen_bottom_right_px)
    p2.color = convert_color(game_config.get("player", {}).get("p2_color", "00FF00"))

    p2.head_size = game_config.get("player", {}).get("head_size", 10)
    p2.tail_size = game_config.get("player", {}).get("tail_width", 3)
    p2.tail_length = game_config.get("player", {}).get("tail_length", 30)

    p2.eye_color = convert_color(game_config.get("player", {}).get("p2_eye_color", (0,0,0)))
    p2_lives = min(game_config.get("player", {}).get("lives", 3), 255)

    if player_cnt == 1:
        p2_lives = 0

    # Fill background
    bg = pygame.Surface(screen.get_size())
    bg = bg.convert()

    background_color = convert_color(game_config.get("background_color", "#000000"))
    bg.fill(background_color)
    

    # Screen border, score, lives, etc
    p1_control_poly = [screen_top_left_px[0], screen_bottom_right_px[1], screen_bottom_right_px[0], max_y]
    p2_control_poly = p1_control_poly
    p1_status = True
    p2_status = False

    if player_cnt == 2:
        p1_control_poly = [screen_top_left_px[0], screen_bottom_right_px[1], screen_bottom_right_px[0] // 2, max_y]
        p2_control_poly = [screen_bottom_right_px[0] // 2, screen_bottom_right_px[1], screen_bottom_right_px[0], max_y]
        p2_status = True
    status_font = pygame.font.Font(game_config.get("game_font"), game_config.get("status_bar", {}).get("font_size"))
    p1_status_color = convert_color(game_config.get("status_bar", {}).get("p1_font_color", "#000000"))
    p1_status_bar_color = convert_color(game_config.get("status_bar", {}).get("p1_color", "#00FF00"))
    score_txt = game_config.get("status_bar", {}).get("score_str", "Score")
    lives_txt = game_config.get("status_bar", {}).get("lives_str", "Lives")
    text_color = convert_color(game_config.get("text_color", "#FFFFFF"))

    p2_status_color = convert_color(game_config.get("status_bar", {}).get("p2_font_color", "#000000"))
    p2_status_bar_color = convert_color(game_config.get("status_bar", {}).get("p2_color", "#00FF00"))

    p1_score_pos = (screen_top_left_px[0] + 15, screen_bottom_right_px[1] + 2)
    p2_score_pos = (screen_bottom_right_px[0] // 2 + 15, screen_bottom_right_px[1] + 2)
    p1_lives_pos = (screen_top_left_px[0] + 200, screen_bottom_right_px[1]+2)
    p2_lives_pos = (screen_bottom_right_px[0] //2  + 200, screen_bottom_right_px[1]+2)

    p1_flash_color = convert_color(game_config.get("player",{}).get("p1_flash_color", (0,255,0)))
    p2_flash_color = convert_color(game_config.get("player",{}).get("p2_flash_color", (0,255,255)))
    
    # shows score per item when encircling it
    pts_font = pygame.font.Font(game_config.get("game_font"), 24)
    pts_color = convert_color(game_config.get("points_color"))

    # position of message text (Pause, Level) on screen
    txt_pos = (screen_bottom_right_px[0] // 2, screen_bottom_right_px[1] // 2)

    # get list of items for this level
    txt_list = [] # text like "Pause", "Game Over"
    level_name = game_config.get("start_level")
    level_items, cycle_a, cycle_b, max_item_cnt, next_level_score, next_level_name, level_msg = get_next_level(level_name)
    if level_msg:
        txt = TxtMsg(txt_pos, level_msg, text_color, 60, 0)
        txt_list.append(txt)



    
    if bg_music_list:
        # need to figure out how to go to the next song
        pygame.mixer.init()
        pygame.mixer.music.load(random.choice(bg_music_list) )
        pygame.mixer.music.play(-1, 0.0)
        pygame.mixer.music.set_volume(game_config.get("music_volume", 1.0))

    
    score_sound = pygame.mixer.Sound(game_config.get("sound", {}).get("score"))
    create_sound = pygame.mixer.Sound(game_config.get("sound", {}).get("create_item"))
    crash_sound = pygame.mixer.Sound((game_config.get("sound", {}).get("crash")))
    level_sound = pygame.mixer.Sound((game_config.get("sound", {}).get("level")))
    game_over_sound = pygame.mixer.Sound(game_config.get("sound", {}).get("game_over"))


    # show control box
    control_flag = False
    ss = 0.1 # 10% of screen
    ss_max_x = int(ss*max_x)
    ss_max_y = int(ss*max_y)
    control_box_poly = [screen_top_left_px[0], screen_top_left_px[1], ss_max_x, ss_max_y]

    # game items
    item_list = [] 
    capture_list = []
    

    # every item_cycle, add an item, decrease this as score increases
    item_cycle = random.randint(cycle_a, cycle_b) + 1


    done = False
    go_flag = True # pause

    p1_score = 0    
    p2_score = 0    
    
    loop_cnt = 0
    inv_cnt = 0 # invincible items
    inv_max = game_config.get("max_invincible", 5)

    # main game loop
    while not done:

        if not go_flag:

            
            pause_text = status_font.render("Paused", 1, text_color)
            text_xy = pause_text.get_rect(center=txt_pos)
            bg.blit(pause_text, text_xy)
            # to fix: don't need to re-render page each loop

            screen.blit(bg, (0, 0))
            pygame.display.flip()
            #print("...")

        if go_flag:
            loop_cnt += 1

            bg.fill(background_color)

            if p1_status:
                p.move()
            if p2_status:
                p2.move()

            # status - score, lives
            # p1 
            pygame.draw.rect(bg, p1_status_bar_color, p1_control_poly)

            
            # should only re-render score_text or lives_text when they actually change
            score_str = "{}: {}".format(score_txt, p1_score)
            score_text = status_font.render(score_str, 1, p1_status_color)
            bg.blit(score_text, p1_score_pos)
            lives_str = "{}: {}".format(lives_txt, p1_lives)
            lives_text = status_font.render(lives_str, 1, p1_status_color)
            bg.blit(lives_text, p1_lives_pos)

            if player_cnt == 2:
                pygame.draw.rect(bg, p2_status_bar_color, p2_control_poly)
                score_str = "{}: {}".format(score_txt, p2_score)
                score_text = status_font.render(score_str, 1, p2_status_color)
                bg.blit(score_text, p2_score_pos)            
                lives_str = "{}: {}".format(lives_txt, p2_lives)
                lives_text = status_font.render(lives_str, 1, p2_status_color)
                bg.blit(lives_text, p2_lives_pos)




            # control box - show mouse movements
            if control_flag:

                pygame.draw.rect(bg, (0, 255, 0), control_box_poly) #, 2)
                xn = int(ss_max_x * (p.xd + 1)/2)
                yn = int(ss_max_y * (p.yd + 1)/2)
                pygame.draw.circle(bg, (0, 0, 0), (xn, yn), 2, 0)
                if player_cnt == 2:
                    xn = int(ss_max_x * (p2.xd + 1)/2)
                    yn = int(ss_max_y * (p2.yd + 1)/2)
                    pygame.draw.circle(bg, (255, 255, 255), (xn, yn), 2, 0)


            # display fading text on the screen
            for txt in txt_list:

                txt.action()
                if txt.tick >= txt.max_tick:
                    del txt
                else:
                    pts_text = pts_font.render(txt.txt, 1, txt.color)
                    text_xy = pts_text.get_rect(center=txt.px)
                    bg.blit(pts_text, text_xy)

            if p1_status:
                draw_player(p, bg)
            if p2_status:
                draw_player(p2, bg)

            # draw game images            
            for i in item_list:
                # randomly go after p1 or p2
                if i.tgt == "P1":
                    i.action(p.px)
                else:
                    i.action(p2.px)

                bg.blit(i.game_img, i.px) 
                
            # code smell - should p1 & p2 overlap be combined somehow?
            if p1_status:
                if len(p.xy_list) > 2:
                    px0 = p.xy_list[-1]
                    px1 = p.xy_list[-2]

                    for c in range(0, len(p.xy_list) -3):
                        c2 = c + 1

                        if overlap_segments(px0, px1, p.xy_list[c], p.xy_list[c2]):
                            
                            # is any game items in the polygon?
                            capture_list = []
                            for i in item_list:
                                
                                if is_point_in_polygon(i.px, p.xy_list[c:]):
                                    capture_list.append(i)


                            this_score = 0
                            bonus_mult = get_bonus_mult(len(capture_list))
                            
                            for cl in capture_list:
                                # negative values have no score, don't disappear
                                if cl.value > 0:
                                    pts = cl.value * bonus_mult
                                    this_score += pts
                                    item_list.remove(cl)

                                    txt = TxtMsg(cl.center, pts, pts_color, 30, 3)
                                    txt_list.append(txt)
                                    if cl.delete_sound:
                                        my_sound = pygame.mixer.Sound(cl.create_sound)
                                        pygame.mixer.Sound.play(my_sound)
                                    elif score_sound:
                                        pygame.mixer.Sound.play(score_sound)

                            p1_score += this_score

                            if this_score > 0:
                                pygame.draw.polygon(bg, p1_flash_color, p.xy_list[c:], 0)

                            # did we go up a level?
                            if p1_score >= next_level_score:
                                level_name = next_level_name
                                level_items, cycle_a, cycle_b, max_item_cnt, next_level_score, next_level_name, level_msg = get_next_level(level_name)
                                print("Level: {}, Msg: {}".format(level_name, level_msg))

                                
                                if level_msg:
                                    txt = TxtMsg(txt_pos, level_msg, text_color, 60, -1)
                                    txt_list.append(txt)
                                    if level_sound:
                                        pygame.mixer.Sound.play(level_sound)

            # player2
            if p2_status:
                if len(p2.xy_list) > 2:
                    px0 = p2.xy_list[-1]
                    px1 = p2.xy_list[-2]

                    for c in range(0, len(p2.xy_list) -3):
                        c2 = c + 1

                        if overlap_segments(px0, px1, p2.xy_list[c], p2.xy_list[c2]):
                            
                            # is any game items in the polygon?
                            capture_list = []
                            for i in item_list:
                                
                                if is_point_in_polygon(i.px, p2.xy_list[c:]):
                                    capture_list.append(i)

                            this_score = 0
                            bonus_mult = get_bonus_mult(len(capture_list))
                            
                            for cl in capture_list:
                                # negative values have no score, don't disappear
                                if cl.value > 0:
                                    pts = cl.value * bonus_mult
                                    this_score += pts
                                    item_list.remove(cl)

                                    txt = TxtMsg(cl.center, pts, pts_color, 30, 3)
                                    txt_list.append(txt)
                                    if cl.delete_sound:
                                        my_sound = pygame.mixer.Sound(cl.create_sound)
                                        pygame.mixer.Sound.play(my_sound)
                                    elif score_sound:
                                        pygame.mixer.Sound.play(score_sound)

                            p2_score += this_score

                            if this_score > 0:
                                pygame.draw.polygon(bg, p2_flash_color, p2.xy_list[c:], 0)

                            # did we go up a level?
                            if p2_score >= next_level_score:
                                level_name = next_level_name
                                level_items, cycle_a, cycle_b, max_item_cnt, next_level_score, next_level_name, level_msg = get_next_level(level_name)
                                print("Level: {}, Msg: {}".format(level_name, level_msg))

                                
                                if level_msg:
                                    txt = TxtMsg(txt_pos, level_msg, text_color, 60, -1)
                                    txt_list.append(txt)
                                    if level_sound:
                                        pygame.mixer.Sound.play(level_sound)


            crash_flag = False
            for i in item_list:
                # did player crash into an item?
                
                if i.hit(p.px):
                    print("P1 Crashed into {}  {}".format(i.item_name, MSG_FAIL))

                    p1_lives = p1_lives - 1
                    crash(crash_sound, screen, bg, p, background_color)
                    item_list = []

                    time.sleep(2)
                    crash_flag = True

                # only if p2 exists
                if i.hit(p2.px):
                    print("P2 Crashed into {}  {}".format(i.item_name, MSG_FAIL))

                    p2_lives = p2_lives - 1
                    crash(crash_sound, screen, bg, p2, background_color)
                    item_list = []
                    crash_flag = True

            if crash_flag:
                time.sleep(2)
                if p1_lives <= 0:
                    p1_status = False
                if p2_lives <= 0:
                    p2_status = False
                if p1_lives <= 0 and p2_lives <= 0:
                    game_over(p1_score, p2_score, game_over_sound, txt_pos, screen, bg)
                    done = True
                # what if p1_lives > 0 and p2_live == 0?

            # how many items on the screen - depends on config
            if len(item_list) < max_item_cnt:

                if loop_cnt % item_cycle == 0:
                    item_cycle = random.randint(cycle_a, cycle_b) + 1

                    
                    item = random.choice(level_items)
                    
                    if game_item_data.get(item, {}).get("status", False):
                        
                        i = GameItem(item, game_item_data[item], screen_top_left_px, screen_bottom_right_px)
                        i.tgt = "P1"
                        if player_cnt == 2:
                            i.tgt = random.choice(["P1", "P2"])
                            
                        while check_px(i.px, p.px, p2.px):
                            i.get_new_px()



                    else:
                        print("Missing item '{}'  {}".format(item, MSG_WARN))

                    if i.value == -1:
                        inv_cnt += 1
                        
                    # make sure not more than 5 invincibles
                    if inv_cnt < inv_max:

                        item_list.append(i)
                        if i.create_sound:
                            my_sound = pygame.mixer.Sound(i.create_sound)
                            pygame.mixer.Sound.play(my_sound)
                        elif create_sound:
                            pygame.mixer.Sound.play(create_sound)

        

            screen.blit(bg, (0, 0))
            pygame.display.flip()


        clock.tick(clock_tick) 
        if go_flag:
            if player_cnt == 2:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]: 
                    p2.arrow_movement("up")            
                if keys[pygame.K_DOWN]: 
                    p2.arrow_movement("down")
                if keys[pygame.K_LEFT]: 
                    p2.arrow_movement("left")
                if keys[pygame.K_RIGHT]: 
                    p2.arrow_movement("right")
                if keys[pygame.K_KP1]:
                    p2.arrow_movement("down-left")
                if keys[pygame.K_KP2]:
                    p2.arrow_movement("down")
                if keys[pygame.K_KP3]:
                    p2.arrow_movement("down-right")
                if keys[pygame.K_KP4]:
                    p2.arrow_movement("left")
                if keys[pygame.K_KP6]:
                    p2.arrow_movement("right")
                if keys[pygame.K_KP7]:
                    p2.arrow_movement("up-left")
                if keys[pygame.K_KP8]:
                    p2.arrow_movement("up")
                if keys[pygame.K_KP9]:
                    p2.arrow_movement("up-right")
                


        # key press, mouse clicks
        for event in pygame.event.get():
            mm = pygame.mouse.get_pos()
            p.movement(mm)

            # mouse buttons do nothing

            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:
                #if event.key == K_ESCAPE:
                #    done = True
                
                if event.key == K_w:
                    clock_tick += 1
                    clock_tick = min(clock_tick,50)
                if event.key == K_s:
                    clock_tick -= 1
                    clock_tick = max(clock_tick, 1)
                if event.key == K_c:
                    control_flag = not control_flag

                # cheats                    
                if event.key == K_x:
                    item_list = []
                if event.key == K_z:
                    player_lives += 1                    


                if event.key == K_n:
                    level_name = next_level_name
                    level_items, cycle_a, cycle_b, max_item_cnt, next_level_score, next_level_name, level_msg = get_next_level(level_name)

                    print("* Welcome to level: {}".format(level_name))
                    if level_msg:
                        txt = TxtMsg(txt_pos, level_msg, text_color, 60, -1)
                        txt_list.append(txt)

                


                if event.key in (K_SPACE, K_PAUSE, K_ESCAPE):
                    if event.key == K_ESCAPE and not go_flag:
                        done = True
                    else:
                        go_flag = not go_flag

                    if not go_flag:
                        print("paused")
                        pause_pos = (int(screen_bottom_right_px[0] / 2), int(screen_bottom_right_px[1]/2))
                        pause_text = status_font.render("Paused", 1, text_color)
                        text_xy = pause_text.get_rect(center=pause_pos)
            
                        bg.blit(pause_text, text_xy)


                        if bg_music_list:
                            pygame.mixer.music.pause()
                    else:
                        print("unpaused")
                        if bg_music_list:
                            pygame.mixer.music.unpause()



    pygame.mixer.music.stop()
    
    del p
    del p2



if __name__ == '__main__':

    # reduce error traceback
    #sys.tracebacklimit = 0

    # use "convert" on images to speed it up
    # img = pygame.image.load("Background.png").convert()


    config_file = "config.yaml"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    print("Loading game config: {}".format(config_file))
    # option to load another config from sys.arg[1]

    if not os.path.isfile(config_file):
        print("Cannot find config: {}".format(config_file))
        sys.exit(1)
    
    with open(config_file, "r", encoding="utf-8") as fh:
        try:
            game_config = yaml.load(fh, Loader=yaml.FullLoader)
        except yaml.scanner.ScannerError as err: 
            print("Config file error: {}".format(err))
            sys.exit(1)

    print("Starting Doubleback 2: {}".format(game_config.get("title")))
    



    bg_music_list = []
    print("Background music:")
    tmp_bg_music_list = game_config.get("music")
    for m in tmp_bg_music_list:
        status = MSG_FAIL
        if os.path.isfile(m):
            bg_music_list.append(m)
            status = MSG_OK
        print("- {}  {}".format(m, status))

    
    # check if game items setup okay, use default configs for missing values
    game_item_data = game_config.get("game_items", {})
    print("Game items:")
    for k in game_item_data:
        status = MSG_FAIL
        item_flag = False
        game_item_data[k]['status'] = False 
        img_list = game_item_data[k].get("image_list", [])
        if not img_list:
            img_list = [game_item_data[k].get("image")]
        img_cnt = 0
        for img in img_list:
            if os.path.isfile(img):
                img_cnt += 1
                
        if img_cnt == len(img_list):
            game_item_data[k]['status'] = True

        if game_item_data[k]['status']:
            status = MSG_OK

            if game_item_data[k].get("size_x", 0) == 0:
                game_item_data[k]["size_x"] = game_config.get("default_game_item_size_x", 25)
            if game_item_data[k].get("size_y", 0) == 0:
                game_item_data[k]["size_y"] = game_config.get("default_game_item_size_y", 25)

            if game_item_data[k].get("value", 0) == 0:
                game_item_data[k]["value"] = random.choice([25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 400, 500, 1000])
            
            # debug
            #print("- {:30} {:4} pts  {}".format(k, game_item_data[k].get("value", 0), status))            

    print("{} game item count".format(len(game_item_data)))
    
    # init pygame
    screen = init_screen()
    
    plr_cnt = 1
    while plr_cnt > 0:
        plr_cnt = title_screen(screen, game_config, game_item_data) 

        if plr_cnt > 0:
            run_game(screen, plr_cnt)

    pygame.quit()    



    # freeware message
    end_file = game_config.get("end_text_screen", "")

    if os.path.isfile(end_file):
        if os.name == 'posix':
            os.system('clear')
        else:
            os.system('cls')

        with open(end_file, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip().startswith("#"):
                    continue
                print(line.strip())


    
    sys.exit(0)            
