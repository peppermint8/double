#!/usr/bin/env python
#! -*- coding: utf-8 -*-
"""
title screen
"""


import pygame
from pygame.locals import *
import random

from common import convert_color, get_coco_rgb
from game_items import GameItem, TextObj

def get_menu_items(item_cnt, all_item_list, game_config, item_txt_color, game_item_data, max_px, item_font):
    """ show item_cnt random items on the menu"""
    item_list = []
    item_txt_list = []
    for i in range(0, item_cnt):
        item = random.choice(all_item_list)
                    
        if game_item_data.get(item, {}).get("status", False):

            px = (300, game_config.get("menu", {}).get("item_y", 350) + i * 60)
            
            i = GameItem(item, game_item_data[item], (0,0), max_px, px)
            i.size_px = (game_config.get("default_game_item_size_x", 40), game_config.get("default_game_item_size_y", 40))
            i.load_imgs()
            item_list.append(i)
            txt_px = (px[0] + 65, px[1] + 10)
            val = i.value
            my_value = "{}, {} points".format(i.item_name.title().replace("_", " "), val)
            if val == -1:
                my_value = "{}, invincible".format(i.item_name.title().replace("_", " "))
                
            
            
            txt = TextObj(my_value, txt_px, item_txt_color, item_font)
            item_txt_list.append(txt)

    return item_list, item_txt_list


def title_screen(screen, game_config, game_item_data):
    """menu screen"""

    player_cnt = 0

    bg = pygame.Surface(screen.get_size())
    bg = bg.convert()

    background_color = convert_color(game_config.get("background_color", "#000000"))
    bg.fill(background_color)


    # initialize a dummy player and have random objects appear with point value
    max_x = game_config.get("window_x", 600)
    max_y = game_config.get("window_y", 600)

    title_font = pygame.font.Font(game_config.get("game_font"), game_config.get("menu", {}).get("title_font_size", 64))
    menu_font = pygame.font.Font(game_config.get("game_font"), game_config.get("menu", {}).get("option_font_size", 48))
    item_font = pygame.font.Font(game_config.get("game_font"), game_config.get("menu", {}).get("item_font_size", 48))
    
    title_str = game_config.get("title", "Doubleback 2")
    title_color = get_coco_rgb()    
    title_px = (max_x // 2, game_config.get("menu", {}).get("title_y", 150))
    title_obj = TextObj(title_str, title_px, title_color, title_font)
    
    # title_desc    

    menu_color = convert_color(game_config.get("menu", {}).get("menu_color", "#000000"))
    menu_select_color = convert_color(game_config.get("menu", {}).get("menu_select_color", "#000000"))


    # better way to do options?  list?
    menu_list = []
    menu_str = game_config.get("menu", {}).get("option1", "One Player")
    menu_px = (max_x // 2, game_config.get("menu", {}).get("option1_y", 150))
    txt = TextObj(menu_str, menu_px, menu_select_color, menu_font) # txt, px, color, font
    menu_list.append(txt)
    
    menu_str = game_config.get("menu", {}).get("option2", "Two Players")
    menu_px = (max_x // 2, game_config.get("menu", {}).get("option2_y", 250))
    txt = TextObj(menu_str, menu_px, menu_color, menu_font)
    menu_list.append(txt)
    
    menu_str = game_config.get("menu", {}).get("quit_txt", "Exit")
    menu_px = (max_x // 2, game_config.get("menu", {}).get("quit_y", 350))
    txt = TextObj(menu_str, menu_px, menu_color, menu_font)
    menu_list.append(txt)
    
    all_item_list = []
    for i in game_item_data:
        if game_item_data[i]['status']:
            all_item_list.append(i)

    item_list = []
    item_txt_list = []
    item_txt_color = convert_color(game_config.get("menu", {}).get("item_txt_color", "#00FF00"))

    item_cnt = game_config.get("menu", {}).get("item_count", 4)
    item_rotate = game_config.get("menu", {}).get("item_rotate", 1000)
    item_list, item_txt_list = get_menu_items(item_cnt, all_item_list, game_config, item_txt_color, game_item_data, (max_x, max_y), item_font)

    menu_id = 1 # first menu item (1..3), 1 = selected


    decoration_x = max_x // 3
    decoration_step = -25

    done = False
    cnt = 0
    render_flag = True
    line_rgb = get_coco_rgb()
    while not done:
        cnt += 1

        
        if cnt % 64 == 0:
            title_obj.color = get_coco_rgb()
            title_obj.render()
            render_flag = True

        if cnt % item_rotate == 0:
            item_list, item_txt_list = get_menu_items(item_cnt, all_item_list, game_config, item_txt_color, game_item_data, (max_x, max_y), item_font)
            line_rgb = get_coco_rgb()
        

        if render_flag:
            
            render_flag = False
            bg.fill(background_color)
            
            # decorative lines
            for x in range(decoration_x, 0, decoration_step):
                pygame.draw.aalines(bg, line_rgb, False, [(x,0), (0, decoration_x-x)], 1)
                


            bg.blit(title_obj.text_item, title_obj.rect)

            for txt in menu_list:
                bg.blit(txt.text_item, txt.rect)


            for i in item_list:
                bg.blit(i.game_img, i.px) 
    
            for i in item_txt_list:
                bg.blit(i.text_item, i.px)            



        screen.blit(bg, (0, 0))
        pygame.display.flip()


        new_menu_id = menu_id
        for event in pygame.event.get():
            
            if event.type == QUIT:
                done = True
            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    done = True
                if event.key == K_1:
                    new_menu_id = 1
                    player_cnt = 1
                elif event.key == K_2:
                    player_cnt = 2
                    new_menu_id = 2
                elif event.key == K_q:
                    player_cnt = 0
                    new_menu_id = 3
                elif event.key == K_RETURN:
                    player_cnt = 0
                    if menu_id == 1:
                        player_cnt = 1
                    elif menu_id == 2:
                        player_cnt = 2
                    done = True
                elif event.key == K_UP:
                    new_menu_id -= 1
                    new_menu_id = max(1, new_menu_id)        
                elif event.key == K_DOWN:
                    new_menu_id += 1
                    new_menu_id = min(3, new_menu_id)

            

            if menu_id != new_menu_id:
                m = menu_list[menu_id-1]
                m.color = menu_color
                m.render()

                menu_id = new_menu_id
                m = menu_list[menu_id-1]
                m.color = menu_select_color
                m.render()

                player_cnt = 0
                if menu_id == 1:
                    player_cnt = 1
                elif menu_id == 2:
                    player_cnt = 2


                render_flag = True        

    print("Player count: {}".format(player_cnt))
    return player_cnt



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

