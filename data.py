# data.py

import pygame

# Màn hình
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

# Bản đồ
MAP_WIDTH, MAP_HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT

# Thông tin nhân vật
player_radius = 20
player_speed = 13
player_x = MAP_WIDTH // 2
player_y = MAP_HEIGHT // 2
unspent_points = 0
player_health = 100
player_max_health = 100
player_attack_cooldown = 0
player_attack_damage = 20
player_level = 1
player_exp = 0
exp_to_next = 100