from util import *
from zombie_sprite import *
from player_sprite import *
from bullet_sprite import *


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file="bg.png", location=[0, 0]):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("bg.png")
        self.image = pygame.transform.scale(self.image, (int(WIDTH), int(HEIGHT)))
        self.rect = self.image.get_rect()


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
                z.vel = z.V * u
                z.seesPlayer = True
            else:
                z.seesPlayer = False

            z.update()
            z.b_vel = [0, 0]


        for b in self.bullets:
            if not b.shot:
                b.shot = True
                b.setup(self.p.pos, self.p.vel)
                b.image = pygame.transform.rotate(b.image, self.p.angle)
                
            for z in self.zombies:
                if np.fabs(length(b.pos-z.pos)) < z.h / 2.0:
                    z.b_vel = b.vel
                    z.health -= 1
                    b.kill()

                    if z.health <= 0:
                        z.kill()


            b.update()


        self.draw_player()
        self.draw_bullets()
        self.draw_zombies()


# Clears and updates window screen
def update(screen, world, bg):
    screen.blit(bg.image, bg.rect)
    world.update()
    pygame.display.update()


def main():
    # Initialize Pygame
    pygame.init()
    pygame.display.set_caption("Z World Survival")
    bg = Background('background_image.png', [0,0])
    # Set the height and width of the screen
    screen_width = WIDTH
    screen_height = HEIGHT
    screen = pygame.display.set_mode([screen_width, screen_height])
     
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
    while len(world.zombies) != 0:
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


        if p.gun == "machine":
            if keys[pygame.K_l]:
                bullet = Bullet()
                world.add_bullet(bullet)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                exit()
            elif p.gun == "pistol" and \
                 event.type == pygame.KEYDOWN and \
                 event.key == pygame.K_RCTRL:
                bullet = Bullet()
                world.add_bullet(bullet)
            
        update(screen, world, bg)

if __name__ == '__main__':
    main()