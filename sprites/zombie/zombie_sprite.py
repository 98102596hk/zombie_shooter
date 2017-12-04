from util import *


ZOMBIE_VELOCITY = 3.0
ZOMBIE_ACCELERATION = 2.0
ZOMBIE_MASS = 180
ZOMBIE_DRAG = 0.9
ZOMBIE_DIMEN = 30
ZOMBIE_HEALTH = 100
WALK_PROB = [0.125] * 8

FX_FLESH_SHOT = SOUND_FX_DIR + "bullet_flesh.wav"
Z_MOTION = ZOMBIE_SPRITE_DIR + "motion/"
Z_ATTACK = ZOMBIE_SPRITE_DIR + "attack/"
Z_DEAD = ZOMBIE_SPRITE_DIR + "dead/1.png"


class Zombie(pygame.sprite.Sprite):
    def __init__(self, dt=0.5):
        pygame.sprite.Sprite.__init__(self)

        self.i = 0
        self.sprite_img = []
        self.bite_img = []
        self.image = None
        self.rect = None
        self.angle = 0
        self.dimen = ZOMBIE_DIMEN

        self.curr_time = 0
        self.dt = dt
        self.pos = np.array([0, 0])
        self.vel = np.array([0, 0])
        self.mag_vel = ZOMBIE_VELOCITY
        self.acc = np.array([0, 0])
        self.mag_acc = ZOMBIE_ACCELERATION
        self.dir = np.array([0, 0])
        self.bull_vel = np.array([0, 0])
        self.bull_mass = 0.0

        self.mass = ZOMBIE_MASS
        self.drag = ZOMBIE_DRAG
        self.health = ZOMBIE_HEALTH

        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')

        self.walks = []
        self.walk_prob = WALK_PROB

        self.seesPlayer = False
        self.alive = True
        self.alert = True

        self.flesh_hit = pygame.mixer.Sound(FX_FLESH_SHOT)
        self.flesh_hit.set_volume(0.3)
        self.biting = False


    def draw(self, screen):
        screen.blit(self.image, self.rect)
        

    def setup(self):
        for img_name in os.listdir(Z_MOTION):
            self.sprite_img.append(os.path.join(Z_MOTION, img_name))

        for img_name in os.listdir(Z_ATTACK):
            self.bite_img.append(os.path.join(Z_ATTACK, img_name))

        self.image = pygame.image.load(self.sprite_img[0])
        self.image = pygame.transform.scale(self.image, (self.dimen, self.dimen))
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

        self.dir = self.walks[random.randint(0, len(self.walks))]


        # Init RK4 solver
        self.random_walk()
        self.set_pos(self.pos)
        self.set_vel()
        self.set_acc()
        self.solver.set_initial_value([self.pos[0], \
                                       self.pos[1], \
                                       self.vel[0], \
                                       self.vel[1]], self.curr_time)


    def random_walk(self):
        continue_random = random.uniform(0, 1)

        if continue_random < 0.05:
            rand_choice = random.uniform(0, 1)
            cum_prob = np.cumsum(self.walk_prob)

            for i in range(0, len(cum_prob)):
                if rand_choice < cum_prob[i]:
                    direction = self.walks[i]
                    break

            self.dir = normalize(direction)


    def set_pos(self, pos):
        if np.fabs(self.vel[0]) > 0.1 or np.fabs(self.vel[1]) > 0.1:
            if not self.biting:
                animate(self)
            else:
                animate_with(self, self.bite_img)
            rotate_dir(self, self.dir)

        self.pos = pos
        self.rect = self.pos


    def set_vel(self):
        self.vel = np.multiply(self.dir, self.mag_vel)


    def set_acc(self):
        self.acc = np.multiply(self.dir, self.mag_acc)


    def set_bullet(self, bullet=None):
        if bullet==None:
            self.bull_vel = np.array([0, 0])
            self.bull_mass = 0.0
        else:
            self.bull_vel = normalize(bullet.vel)*bullet.mag_vel*10
            self.bull_mass = bullet.mass


    def set_towards_player(self, player):
        self.seesPlayer = True
        self.dir = normalize((player.pos + player.dimen/2) - (self.pos + self.dimen/2))
        self.set_pos(self.pos)
        self.mag_acc *= 2.0
        self.set_acc()
        self.mag_acc /= 2.0


    def dec_health(self, damage):
        self.flesh_hit.play()
        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.image = pygame.image.load(Z_DEAD)


    def f(self, t, state):
        dx, dy = (state[2:4]*self.mass + 10*self.bull_vel*self.bull_mass)/(self.mass + self.bull_mass)
        dvx, dvy = self.acc - self.drag*state[2:4]

        return [dx, dy, dvx, dvy]


    def update(self):
        if self.alive:
            if not self.seesPlayer:
                self.random_walk()
                self.set_acc()

            if not self.biting or self.bull_mass != 0.0:
                self.curr_time += self.dt
                if self.solver.successful():

                    self.solver.integrate(self.curr_time)
                    pos = self.solver.y[0:2]
                    self.vel = self.solver.y[2:4]
                    self.dir = normalize(self.vel)

                    pos = check_boundary(self, pos)


                    self.set_pos(pos)

            if (self.bull_mass != 0.0):
                self.i += 1

                if self.i > 50:
                    self.i  = 0
                    self.set_bullet()
