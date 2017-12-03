from util import *
from zombie_sprite import *
from player_sprite import *
from bullet_sprite import *


class Background(pygame.sprite.Sprite):
    def __init__(self, image="bg.png"):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (int(WIDTH), int(HEIGHT)))
        self.rect = self.image.get_rect()


class Z_World():
    def __init__(self, screen):
        self.i = 0
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
        self.alert = True
        self.zombieShot = False
        self.zombie_health = 100

        self.alert_sound = pygame.mixer.Sound('sound_fx/alert.wav')


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
        group = pygame.sprite.Group()
        for z in self.zombies:
            if not z.alive:
                z.draw(self.screen)
            else:
                group.add(z)

        group.draw(self.screen)
    

    def draw_bullets(self):
        self.bullets.draw(self.screen)


    def update(self):
        self.p.update()
            

        self.alert = True
        for z in self.zombies:
            if z.alive:
                if self.p.alive:
                    # Zombie near player
                    dist = length((self.p.pos + self.p.dimen/2) - (z.pos + z.dimen/2))
                    if dist < 200:
                        z.set_towards_player(self.p)    
                        if z.alert and not pygame.mixer.music.get_busy():
                            z.alert = False
                            self.alert_sound.stop()
                            self.alert_sound.play()
                            play_music()

                        # Player-Zombie collision
                        if dist <= (z.dimen/2 + self.p.dimen/2 - 10):
                            z.biting = True
                            self.health_count += 1
                            if self.health_count > 50:
                                self.health_count = 0
                                self.p.dec_health()

                                if not self.p.alive:
                                    rotate(self.p, z.pos)
                        else:
                            z.biting = False
                    else:
                        z.alert = True
                        z.seesPlayer = False

                    self.alert = self.alert and z.alert
                else:
                    if z.seesPlayer:
                        z.seesPlayer = False
                        z.biting = False
            
            z.update()


        if self.alert and pygame.mixer.music.get_busy():
            stop_music()


        for b in self.bullets:
            if not b.shot:
                b.shot = True
                b.type = self.p.gun

                b.setup(self.p.pos + self.p.dimen/2 - b.gun_config[2]/2, self.p.vel)
                b.image = pygame.transform.rotate(b.image, self.p.angle)

            # Zombie-Bullet collision
            for z in self.zombies:
                if z.alive:
                    if length(b.pos - z.pos) <= z.dimen:
                        z.dec_health(b.damage)
                        z.set_bullet(b)
                        b.kill()

                        if not z.alive:
                            rotate(z, self.p.pos)

                        self.zombie_health = z.health
                        self.zombieShot = True
                        

                b.update()           


        
        self.draw_bullets()

        if self.p.alive:
            self.draw_zombies()
            self.draw_player()
        else:
            self.draw_player()
            self.draw_zombies()

        if not self.p.alive:
            self.screen.blit(self.wasted_logo, (WIDTH/2 - self.wasted_w/2, HEIGHT/2 - self.wasted_h/2))

        if self.zombieShot:
            pygame.draw.rect(self.screen, BLACK, (WIDTH-110, 0, 110, 40))
            pygame.draw.rect(self.screen, RED, (WIDTH-105, 5, self.zombie_health, 30))

        pygame.draw.rect(self.screen, BLACK, (0, 0, 210, 40))
        pygame.draw.rect(self.screen, GREEN, (5, 5, self.p.health, 30))


# Clears and updates window screen
def update(screen, world, bg):
    screen.blit(bg.image, bg.rect)
    world.update()
    pygame.display.update()


def main():
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption("Z World Survival")
    bg = Background()
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


    paused = False
    direction = np.array([0, 0])
    world.draw_player()
    the_end = False
    count = 0
    gun_count = 30
    j = 0
    lag = 20
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
                    lag = 20
                    j = 0
                elif event.key == pygame.K_2:
                    player.gun = "machine"
                    lag = 5
                    j = 0
                elif event.key == pygame.K_3:
                    player.gun = "shotgun"
                    lag = 50
                    j = 0
                elif event.key == pygame.K_p:
                    paused = True
                elif event.key == pygame.K_r:
                    paused = False


        if keys[pygame.K_RCTRL] or keys[pygame.K_LCTRL]:
            if j <= 0:
                j = lag
                bullet = Bullet()
                world.add_bullet(bullet)
        j -= 1

        if player.alive:
            if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    direction[1] = -1
                else:
                    direction[1] = 1
            else:
                direction[1] = 0

            if keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    direction[0] = -1
                else:
                    direction[0] = 1
            else:
                direction[0] = 0

            direction = normalize(direction)
            if (length(direction) > 0):
                player.set_dir(direction)
                player.set_acc()
            else:
                player.set_acc(0.0)  
        else:
            if not the_end:
                the_end = True
                bg = Background("bg_dead.png")
          
        if not paused:  
            update(screen, world, bg)


if __name__ == '__main__':
    main()