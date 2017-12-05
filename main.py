from util import *
from zombie_sprite import *
from player_sprite import *
from bullet_sprite import *


# Constants setup
TITLE = "Z WORLD SURVIVAL"

BG_IMG      = BG_IMG_DIR + "bg.png"
BG_DEAD_IMG = BG_IMG_DIR + "bg_dead.png"
WASTED_LOGO = BG_IMG_DIR + "wasted.png"

FX_ALERT = SOUND_FX_DIR + "alert/wav"

NUM_ZOMBIES = 5
NUM_LEVELS = 5


class Background(pygame.sprite.Sprite):
    def __init__(self, image=BG_IMG):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.image = pygame.transform.scale(self.image, (int(WIDTH), int(HEIGHT)))
        self.rect = self.image.get_rect()

class Z_World():
    def __init__(self, screen):
        self.i = 0
        self.p = pygame.sprite.Sprite
        self.zombies = pygame.sprite.Group()
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
        self.z_count = 0
        self.bullet_dir = np.array([0, -1])

        self.wasted_logo = pygame.image.load(WASTED_LOGO)
        self.wasted_w = self.wasted_logo.get_width()
        self.wasted_h = self.wasted_logo.get_height()
        self.alert_sound = pygame.mixer.Sound(FX_ALERT)


    def add_player(self, sprite):
        self.p = sprite


    def add_zombie(self, sprite):
        self.z_count += 1
        self.zombies.add(sprite)


    def add_bullet(self, sprite):
        self.bullets.add(sprite)


    def draw_player(self):
        self.p.draw(self.screen)


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
                    dist = length(self.p.center - z.center)
                    if dist < 200:
                        z.set_towards_player(self.p)    
                        if z.alert and not pygame.mixer.music.get_busy():
                            z.alert = False
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
                                    rotate(self.p, z.center)
                        else:
                            z.biting = False
                    else:
                        z.alert = True
                        z.seesPlayer = False

                    self.alert = self.alert and z.alert

                    if length(self.p.acc) > 0.0:
                        self.bullet_dir = normalize(self.p.acc)
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

               
                b.setup(self.p.center - b.dimen/2, self.bullet_dir)
                b.image = pygame.transform.rotate(b.image, self.p.angle)

            # Zombie-Bullet collision
            for z in self.zombies:
                if z.alive:
                    if length(b.center - z.center) < z.dimen/2.0:
                        z.dec_health(b.damage)
                        z.set_bullet(b)
                        b.kill()

                        if not z.alive:
                            rotate(z, self.p.center)
                            self.z_count -= 1

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


def reset_world(world):
    # Add player to zombie world and position in the center of the screen
    player = Player()
    player.setup([WIDTH / 2 - player.dimen / 2, HEIGHT / 2 - player.dimen / 2])
    world.add_player(player)

    for z in world.zombies:
        z.kill()
        del z

    num = world.i + NUM_ZOMBIES
    world.i += 1
    setup_zombies(world, num)

    return player


# Creates number of zombies defined by num
def setup_zombies(world, num=NUM_ZOMBIES):
    for i in range(num):
        zombie = Zombie()
        zombie.setup()
        world.add_zombie(zombie)


def main():
    # Initialize Pygame
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption(TITLE)
    bg = Background()

    # Set the height and width of the screen
    screen = pygame.display.set_mode([WIDTH, HEIGHT])
    clock = pygame.time.Clock()
    world = Z_World(screen)

    paused = False
    the_end = False

    direction = np.array([0, 0])

    # used for gun reload lag
    j = 0 
    lag = 20

    # -------- Main Program Loop -----------
    while True:
        if world.z_count <= 0 and world.i < NUM_LEVELS:
            player = reset_world(world)

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            # Handle quitting game
            if event.type == pygame.QUIT or \
               event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                # Gun choice
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

                # Pause game
                elif event.key == pygame.K_p:
                    paused = True

                # Resume game
                elif event.key == pygame.K_r:
                    paused = False

        # Handle shooting
        if keys[pygame.K_RCTRL] or keys[pygame.K_LCTRL]:
            if j <= 0:
                j = lag
                bullet = Bullet()
                world.add_bullet(bullet)
        j -= 1


        if player.alive:
            # Sets player direction based on user input
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

            if length(direction) > 0.0:
                player.set_dir(direction)
                player.set_acc()
            else:
                player.set_acc(0.0)  
        else:
            # Change background when player dies
            if not the_end:
                the_end = True
                bg = Background(BG_DEAD_IMG)
          
        # Main update
        if not paused:  
            update(screen, world, bg)


if __name__ == '__main__':
    main()