import pygame, sys, os
import numpy as np
from numpy import random
import math
from scipy.integrate import ode

sys.path.append("sprites/zombie")
sys.path.append("sprites/player")
sys.path.append("sprites/bullet")

# Constants setup
BG_IMG_DIR = "media/bg_img/" 
PLAYER_SPRITE_DIR = "sprites/player/sprite_imgs/"
ZOMBIE_SPRITE_DIR = "sprites/zombie/sprite_imgs/"
BULLET_SPRITE_DIR = "sprites/bullet/sprite_imgs/"

SOUND_FX_DIR = "media/sound_fx/"
BG_MUSIC = "media/bg_music/theme.mp3"

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

ACCEL = 0.3
WIDTH = 1080
HEIGHT = 600


def rotate(sprite, pos):
    sprite.angle = np.degrees(np.arctan2\
                   (sprite.rect[0] - pos[0], sprite.rect[1] - pos[1]))
    
    sprite.image = pygame.transform.rotate(sprite.image, sprite.angle)


def rotate_dir(sprite, direction):
    sprite.angle = 180 + np.degrees(np.arctan2(direction[0], direction[1]))

    sprite.image = pygame.transform.rotate(sprite.image, sprite.angle)

def animate(sprite):
    sprite.i += 1
    sprite.image = pygame.image.load\
                   (sprite.sprite_img[sprite.i % len(sprite.sprite_img)])

    sprite.rect = sprite.image.get_rect()

def animate_with(sprite, imgs):
    sprite.i += 1
    sprite.image = pygame.image.load(imgs[sprite.i % len(imgs)])

    sprite.rect = sprite.image.get_rect()


def check_boundary(sprite, pos):
    if pos[0] > WIDTH:
        pos[0] = pos[0] - WIDTH
    elif (pos[0] + sprite.dimen) < 0:
        pos[0] = WIDTH + pos[0]

    if pos[1] > HEIGHT:
        pos[1] = pos[1] - HEIGHT
    elif (pos[1] + sprite.dimen) < 0:
        pos[1] = HEIGHT + pos[1]

    return pos


def out_of_bounds(pos):
    if pos[0]*pos[1] < 0 or pos[0] > WIDTH or pos[1] > HEIGHT:
        return True

    return False


def length(v):
    return np.linalg.norm(v)


def normalize(v):
    if length(v) > 0.0:
        return v / length(v)
    else:
        return v

def play_music():
    pygame.mixer.music.load(BG_MUSIC)
    pygame.mixer.music.play()

def stop_music(fade=2000):
    pygame.mixer.music.fadeout(fade)