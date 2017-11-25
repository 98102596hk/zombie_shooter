import pygame, sys, os
import numpy as np
from scipy.integrate import ode

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.pos = np.array([0,0])
        self.vel = np.array([0,0])

        self.sprite_img = []
        self.image = None
        self.rect = None
        # self.solver = ode(self.f)
        # self.solver.set_integrator('dop853')


    def setup(self):
        for img_name in os.listdir("player/"):
            print img_name
            self.sprite_img.append(os.path.join("player", img_name))


        self.image = pygame.image.load(self.sprite_img[0])
        self.rect = self.image.get_rect()


    def set_pos(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class Z_World():
    def __init__(self, screen):
        self.zombies = pygame.sprite.Group()
        self.player = pygame.sprite.Group()
        self.screen = screen

    def add_player(self, sprite):
        self.player.add(sprite)

    def draw_player(self):
        self.player.draw(self.screen)



# Clears and updates window screen
def update(screen, world):
    screen.fill(WHITE)
    world.draw_player()
    pygame.display.update()


def main():
    # Initialize Pygame
    pygame.init()
     
    # Set the height and width of the screen
    screen_width = 700
    screen_height = 400
    screen = pygame.display.set_mode([screen_width, screen_height])
    screen.fill(WHITE)

    done = False
     
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    clock.tick(30)

    player = Player()
    player.setup()
    player.set_pos([screen_width/2, screen_height/2])

    world = Z_World(screen)
    world.add_player(player)

    score = 0
    
    
    world.draw_player()
    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_w:
                for p in world.player:
                    p.set_pos([0, 0])

        update(screen, world)
        pygame.display.flip()

if __name__ == '__main__':
    main()