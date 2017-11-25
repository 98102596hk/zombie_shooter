import pygame, sys, os
import numpy as np
import math
from scipy.integrate import ode

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

ACCEL = 0.3

class Player(pygame.sprite.Sprite):
    def __init__(self, dt=0.1):
        pygame.sprite.Sprite.__init__(self)
        self.i = 0
        self.pos_vec = np.array([0, -1])
        self.pos = np.array([0,0])
        self.vel = np.array([0,0])
        self.angle = 0
        self.sprite_img = []
        self.image = None
        self.rect = None
        self.curr_time = 0
        self.dt = dt
        self.accel = np.array([0, 0])
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')

        self.drag = 0.1

    def setup(self, pos, vel=np.array([0, 0])):
        for img_name in os.listdir("player/"):
            print img_name
            self.sprite_img.append(os.path.join("player", img_name))


        self.image = pygame.image.load(self.sprite_img[0])
        self.rect = self.image.get_rect()

        self.pos = pos
        self.vel = vel

        self.set_pos(self.pos)
        self.solver.set_initial_value([self.pos[0], self.pos[1], self.vel[0], self.vel[1]], self.curr_time)


    def set_accel(self, a):
        self.accel = a


    def rotate(self, pos):
        self.angle = math.degrees(math.atan2\
              (self.rect[0]-pos[0], self.rect[1]-pos[1]))
        
        self.image=pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect()


    def animate(self, pos):
        if (np.fabs(self.vel[0]) > 0.4 or np.fabs(self.vel[1]) > 0.4):
            self.i += 1
            self.image = pygame.image.load(self.sprite_img[self.i%len(self.sprite_img)])

            self.rotate(pos)


    def set_pos(self, pos):
        self.animate(pos)

        self.pos = pos
        self.rect = self.pos


    def set_vel(self, vel=np.array([0, 0])):
        self.vel = normalize(vel)


    def f(self, t, state):

        dx = state[2]
        dvx = self.accel[0] - self.drag*state[2]

        dy = state[3]
        dvy = self.accel[1] - self.drag*state[3]

        return [dx, dy, dvx, dvy]


    def update(self):
        self.curr_time += self.dt
        if self.solver.successful():

            self.solver.integrate(self.curr_time)
            pos = self.solver.y[0:2]
            self.vel = self.solver.y[2:4]/self.dt
            # if not math.isnan(self.vel[0]):
            #     print self.vel[0]

            self.set_pos(pos)


class Z_World():
    def __init__(self, screen):
        self.zombies = pygame.sprite.Group()
        self.player = pygame.sprite.Group()
        self.screen = screen

    def add_player(self, sprite):
        self.player.add(sprite)

    def draw_player(self):
        self.player.draw(self.screen)


def length(v):
    return np.linalg.norm(v)


def normalize(v):
    if length(v) > 0:
        return v / length(v)
    else:
        return v

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
     
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    clock.tick(20)

    player = Player()
    player.setup([screen_width/2, screen_height/2])

    world = Z_World(screen)
    world.add_player(player)

    score = 0
    
    vel = np.array([0, 0])
    world.draw_player()
    # -------- Main Program Loop -----------
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_s]:
            if keys[pygame.K_w]:
                vel[1] = -1
            else:
                vel[1] = 1
        else:
            vel[1] = 0

        if keys[pygame.K_a] or keys[pygame.K_d]:
            if keys[pygame.K_a]:
                vel[0] = -1
            else:
                vel[0] = 1
        else:
            vel[0] = 0

        for p in world.player:
            p.set_vel(vel)
            p.accel = [vel[0]*ACCEL, vel[1]*ACCEL]
            p.update()

        update(screen, world)

if __name__ == '__main__':
    main()