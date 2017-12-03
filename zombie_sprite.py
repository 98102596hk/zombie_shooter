from util import *

ZOMBIE_VELOCITY = 3.0
ZOMBIE_ACCELERATION = 2.0
ZOMBIE_MASS = 180
ZOMBIE_DRAG = 0.9
ZOMBIE_DIMEN = 30
ZOMBIE_HEALTH = 100

WALK_PROB = [0.125] * 8

class Zombie(pygame.sprite.Sprite):
    def __init__(self, dt=0.5):
        pygame.sprite.Sprite.__init__(self)

        self.i = 0
        self.sprite_img = []
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

    def setup(self):
        for img_name in os.listdir("zombie/"):
            self.sprite_img.append(os.path.join("zombie", img_name))


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

        direction = self.random_walk()
        self.set_pos(self.pos, direction)
        self.set_vel(direction)
        self.set_acc(direction)
        self.solver.set_initial_value([self.pos[0], \
                                       self.pos[1], \
                                       self.vel[0], \
                                       self.vel[1]], self.curr_time)


    def random_walk(self):
        continue_random = random.uniform(0, 1)

        direction = self.dir
        if continue_random < 0.05:
            rand_choice = random.uniform(0, 1)
            cum_prob = np.cumsum(self.walk_prob)

            for i in range(0, len(cum_prob)):
                if rand_choice < cum_prob[i]:
                    direction = self.walks[i]
                    break

            direction = normalize(direction)

        return direction

        # self.dir_acc = self.dir_vel
        # self.acc = np.multiply(self.dir_acc, self.mag_acc)


    def set_pos(self, pos, direction):
        if np.fabs(self.vel[0]) > 0.1 or np.fabs(self.vel[1]) > 0.1:
            animate(self)
            rotate(self, normalize(self.vel))

        self.pos = pos
        self.rect = self.pos

    def set_vel(self, direction):
        self.vel = np.multiply(direction, self.mag_vel)

    def set_acc(self, direction):
        self.acc = np.multiply(direction, self.mag_acc)

    def set_bullet(self, vel=np.array([0, 0]), mass=0.0):
        self.bull_vel = vel
        self.bull_mass = mass

    def set_towards_player(self, player):
        u = normalize(player.pos - self.pos)
        self.set_pos(self.pos, u)
        self.mag_acc *= 2.0
        self.set_acc(u)
        self.mag_acc /= 2.0
        rotate_dir(self, u)
        self.seesPlayer = True


    def f(self, t, state):
        dx = (state[2]*self.mass + self.bull_vel[0]*self.bull_mass)/(self.mass + self.bull_mass)
        dvx = self.acc[0] - self.drag*state[2]

        dy = (state[3]*self.mass + self.bull_vel[1]*self.bull_mass)/(self.mass + self.bull_mass)
        dvy = self.acc[1] - self.drag*state[3]

        return [dx, dy, dvx, dvy]


    def update(self):

        if not self.seesPlayer:
            direction = self.random_walk()
            self.dir = direction
            self.set_acc(direction)
        else:
            direction = self.dir

        self.curr_time += self.dt
        if self.solver.successful():

            self.solver.integrate(self.curr_time)
            pos = self.solver.y[0:2]
            self.vel = self.solver.y[2:4]

            pos = check_boundary(self, pos)


            self.set_pos(pos, direction)

            if (self.bull_mass != 0.0):
                self.i += 1

                if self.i > 100:
                    self.i  = 0
                    self.set_bullet()
