import pygame, sys, os
import numpy as np
from numpy import random
import math
from scipy.integrate import ode

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

ACCEL = 0.3

WIDTH = 1080
HEIGHT = 720

WALK_PROB = [0.125] * 8
ZOMBIE_HEALTH = 3


class Zombie(pygame.sprite.Sprite):
    def __init__(self, dt=0.5):
        pygame.sprite.Sprite.__init__(self)
        self.i = 0
        self.pos_vec = np.array([0, -1])
        self.pos = np.array([0, 0])
        self.vel = np.array([0, 0])
        self.angle = 0
        self.sprite_img = []
        self.image = None
        self.rect = None
        self.curr_time = 0
        self.dt = dt
        self.accel = np.array([0, 0])
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.drag = 0.3
        self.prob = WALK_PROB
        self.walks = []
        self.a = ACCEL
        self.V = 3.0
        self.health = ZOMBIE_HEALTH
        self.seesPlayer = False
        self.h = 0.0
        self.w = 0.0


    def setup(self, vel=np.array([0, 0])):
        for img_name in os.listdir("zombie/"):
            self.sprite_img.append(os.path.join("zombie", img_name))


        self.image = pygame.image.load(self.sprite_img[0])
        self.image = pygame.transform.scale(self.image, (int(30), int(60)))
        self.h = self.image.get_height()
        self.w = self.image.get_width()
        self.rect = self.image.get_rect()

        '''
        Velocity in order: up, up-right, right, down-right, down, down-left,
                           left, up-left
        '''
        self.walks = [[0, -1], \
                      [1, -1], \
                      [1, 0],  \
                      [1, 1],  \
                      [0, 1],  \
                      [-1, 1], \
                      [-1, 0], \
                      [-1, -1]]

        self.pos[0] = random.choice([random.randint(0, 100),\
                                     random.randint(WIDTH-100, WIDTH)])
        self.pos[1] = random.choice([random.randint(0, 100), \
                                     random.randint(HEIGHT-100, HEIGHT)])

        self.vel = self.random_walk()
        self.accel = np.multiply(self.vel, ACCEL)

        self.set_pos(self.pos)
        self.solver.set_initial_value([self.pos[0], \
                                       self.pos[1], \
                                       self.vel[0], \
                                       self.vel[1]], self.curr_time)


    def random_walk(self):
        continue_random = random.uniform(0, 1)

        if continue_random < 0.05 and not self.seesPlayer:
            rand_choice = random.uniform(0, 1)
            cum_prob = np.cumsum(self.prob)

            vel = np.array([-1, -1])

            for i in range(0, len(cum_prob)):
                if rand_choice <= cum_prob[i]:
                    vel = self.walks[i]
                    break

            vel = np.multiply(normalize(vel), self.V)
        else:
            vel = self.vel

        self.accel = np.multiply(vel, self.a)

        return vel


    def set_pos(self, pos):
        if (np.fabs(self.vel[0]) > 0.4 or np.fabs(self.vel[1]) > 0.4) or self.seesPlayer:
            animate(self)

            rotate(self, pos)

        self.pos = pos
        self.rect = self.pos


    def f(self, t, state):
        dx = state[2]
        dvx = self.accel[0] - self.drag*state[2]

        dy = state[3]
        dvy = self.accel[1] - self.drag*state[3]

        return [dx, dy, dvx, dvy]


    def update(self):
        self.vel = self.random_walk()

        self.curr_time += self.dt
        if self.solver.successful():

            self.solver.integrate(self.curr_time)
            pos = self.solver.y[0:2]
            self.vel = self.solver.y[2:4]

            pos = check_boundary(pos)

            self.set_pos(pos)


class Player(pygame.sprite.Sprite):
    def __init__(self, dt=0.5):
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
        self.gun = "pistol"
        self.accel = np.array([0, 0])
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.drag = 0.03

    def setup(self, pos, vel=np.array([0, 0])):
        for img_name in os.listdir("player/"):
            self.sprite_img.append(os.path.join("player", img_name))

        self.image = pygame.image.load(self.sprite_img[0])
        self.image = pygame.transform.scale(self.image, (int(30), int(60)))
        self.rect = self.image.get_rect()

        self.pos = pos
        self.vel = vel

        self.set_pos(self.pos)
        self.solver.set_initial_value([self.pos[0], self.pos[1], self.vel[0], self.vel[1]], self.curr_time)


    def set_pos(self, pos):
        if (np.fabs(self.vel[0]) > 0.8 or np.fabs(self.vel[1]) > 0.8):
            animate(self)
            rotate(self, pos)

        self.pos = pos
        self.rect = self.pos


    def set_vel(self, vel=np.array([0, 0])):
        self.vel = normalize(vel)*vel


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
            self.vel = self.solver.y[2:4]

            pos = check_boundary(pos)
            self.set_pos(pos)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, gun="pistol", dt=0.2):
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
        self.drag = 0.0
        self.V = 100.0
        self.shot = False
        self.type = gun

    def setup(self, pos, vel=np.array([0, 0])):
        img_name = "bullet/" + self.type + ".png"
        self.image = pygame.image.load(img_name)
        self.image = pygame.transform.scale(self.image, (int(10), int(10)))

        self.rect = self.image.get_rect()

        self.set_vel(vel)
        self.set_pos(pos)
        self.solver.set_initial_value([self.pos[0], self.pos[1], self.vel[0], self.vel[1]], self.curr_time)


    def set_pos(self, pos):
        self.pos = pos
        self.rect = self.pos


    def set_vel(self, vel=np.array([0, 0])):
        self.vel = normalize(vel)*self.V


    def f(self, t, state):
        dx = state[2]
        dvx = 0

        dy = state[3]
        dvy = 0

        return [dx, dy, dvx, dvy]


    def update(self):
        self.curr_time += self.dt
        if self.solver.successful():

            self.solver.integrate(self.curr_time)
            pos = self.solver.y[0:2]
            self.vel = self.solver.y[2:4]

            if not out_of_bounds(pos):
                self.set_pos(pos)
            else:
                self.kill()


class Z_World():
    def __init__(self, screen):
        self.p = pygame.sprite.Sprite
        self.zombies = pygame.sprite.Group()
        self.player = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.screen = screen
        self.see = False


    def add_player(self, sprite):
        self.p = sprite
        self.player.add(self.p)


    def add_zombie(self, sprite):
        self.zombies.add(sprite)


    def add_bullet(self, sprite):
        self.bullets.add(sprite)


    def draw_player(self):
        self.player.draw(self.screen)


    def draw_zombies(self):
        self.zombies.draw(self.screen)
    

    def draw_bullets(self):
        self.bullets.draw(self.screen)


    def update(self):
        self.p.update()

        for z in self.zombies:
            if np.fabs(length(z.pos - self.p.pos)) < 200:
                u = normalize(self.p.pos - z.pos)
                z.vel = z.V*u
                z.seesPlayer = True
            else:
                z.seesPlayer = False

            z.update()


        for b in self.bullets:
            if not b.shot:
                b.shot = True
                b.setup(self.p.pos, self.p.pos)
                b.image = pygame.transform.rotate(b.image, self.p.angle)

            for z in self.zombies:
                if np.fabs(length(b.pos-z.pos)) < z.h / 2.0:
                    z.health -= 1
                    b.kill()
                    if z.health <= 0:
                        z.kill()
                    
                    break

            b.update()



        self.draw_player()
        self.draw_bullets()
        self.draw_zombies()


def rotate(sprite, pos):
    sprite.angle = np.degrees(np.arctan2\
                   (sprite.rect[0] - pos[0], sprite.rect[1] - pos[1]))
    
    sprite.image = pygame.transform.rotate(sprite.image, sprite.angle)
    sprite.rect = sprite.image.get_rect()


def animate(sprite):
    sprite.i += 1
    sprite.image = pygame.image.load\
                   (sprite.sprite_img[sprite.i % len(sprite.sprite_img)])


def check_boundary(pos):
    if pos[0] > WIDTH:
        pos[0] = pos[0] - WIDTH
    elif pos[0] < 0:
        pos[0] = WIDTH - pos[0]

    if pos[1] > HEIGHT:
        pos[1] = pos[1] - HEIGHT
    elif pos[1] < 0:
        pos[1] = HEIGHT - pos[1]

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


# Clears and updates window screen
def update(screen, world):
    screen.fill(WHITE)
    world.update()
    pygame.display.update()


def main():
    # Initialize Pygame
    pygame.init()
     
    # Set the height and width of the screen
    screen_width = WIDTH
    screen_height = HEIGHT
    screen = pygame.display.set_mode([screen_width, screen_height])
    # screen.fill(WHITE)
     
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()


    world = Z_World(screen)

    player = Player()
    player.setup([screen_width / 2, screen_height / 2])
    world.add_player(player)

    for i in range(5):
        zombie = Zombie()
        zombie.setup()
        world.add_zombie(zombie)

    score = 0
    

    vel = np.array([0, 0])
    world.draw_player()


    # -------- Main Program Loop -----------
    while True:
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
            p.accel = np.multiply(vel, ACCEL)


        if player.gun == "machine":
            if keys[pygame.K_l]:
                bullet = Bullet()
                world.add_bullet(bullet)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                exit()
            elif p.gun == "pistol" and event.type == pygame.KEYDOWN and event.key == pygame.K_RCTRL:
                bullet = Bullet()
                world.add_bullet(bullet)
            
        update(screen, world)

if __name__ == '__main__':
    main()