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
        self.health_count = 0
        self.see = False
        self.showZHealth = False
        self.zhealth_count = 0
        self.wasted_logo = None
        self.wasted_h = 0
        self.wasted_w = 0


    def add_player(self, sprite):
        self.p = sprite
        self.player.add(self.p)
        self.wasted_logo = pygame.image.load("dead_player/wasted.png")
        self.wasted_w = self.wasted_logo.get_width()
        self.wasted_h = self.wasted_logo.get_height()

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
            if z.alive:
                # Player-Zombie collision
                if np.fabs(length(z.pos - self.p.pos)) < self.p.h and self.p.alive:
                    if self.health_count > 50:
                        self.health_count = 0
                        self.p.health -= 20

                    self.health_count += 1

                    if self.p.health <= 0:
                        self.p.image = pygame.image.load("dead_player/1.png")
                        self.p.alive = False
                        z.seesPlayer = False
                        
                # Zombie near player
                if np.fabs(length(z.pos - self.p.pos)) < 200:
                    if self.p.alive:
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
                b.type = self.p.gun

                b.setup([self.p.pos[0] + self.p.w/2, self.p.pos[1]], self.p.vel)
                b.image = pygame.transform.rotate(b.image, self.p.angle)

            
            # Zombie-Bullet collision
            for z in self.zombies:
                if z.alive:
                    if np.fabs(length(b.pos - z.pos)) < z.h / 2.0:
                        b.kill()
                        self.zhealth_count = 100
                        self.showZHealth = True
                        z.b_vel = b.vel
                        z.health -= 20

                        if z.health <= 0:
                            z.alive = False
                            z.image = pygame.image.load("dead_zombie/1.png")
                            # z.kill()

            b.update()           


        self.draw_player()
        self.draw_bullets()
        self.draw_zombies()

        if not self.p.alive:
            self.screen.blit(self.wasted_logo, (WIDTH/2 - self.wasted_w/2, HEIGHT/2 - self.wasted_h/2))

        pygame.draw.rect(self.screen, BLACK,(0, 0, 210, 40))
        pygame.draw.rect(self.screen, GREEN,(5, 5, self.p.health, 30))


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

    count = 0
    gun_count = 30
    # -------- Main Program Loop -----------
    while len(world.zombies) != 0:
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.gun = "pistol"
                    gun_count = 30
                elif event.key == pygame.K_2:
                    player.gun = "machine"
                    gun_count = 0
                elif event.key == pygame.K_RCTRL:
                    if player.gun == "pistol":
                        bullet = Bullet()
                        world.add_bullet(bullet)

        if player.gun == "machine":
            if keys[pygame.K_RCTRL]:
                # count += 1
                # if count > gun_count:
                    # count = 0
                bullet = Bullet()
                world.add_bullet(bullet)

        if player.alive:
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

            player.set_vel(vel)
            player.accel = np.multiply(vel, ACCEL)        

            
        update(screen, world, bg)

if __name__ == '__main__':
    main()