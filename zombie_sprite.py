from util import *


class Zombie(pygame.sprite.Sprite):
    def __init__(self, dt=0.5):
        pygame.sprite.Sprite.__init__(self)
        self.i = 0
        self.pos = np.array([0, 0])
        self.vel = np.array([0, 0]) # used for velocity direction when normalized
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
        self.V = 3.0 # velocity magnitude
        self.health = ZOMBIE_HEALTH
        self.seesPlayer = False
        self.h = 0.0
        self.w = 0.0
        self.b_vel = np.array([0, 0])
        self.off = 0
        self.alive = True
        self.alert = True

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
        dx = state[2] + self.b_vel[0]*0.05
        dvx = self.accel[0] - self.drag*state[2]

        dy = state[3] + self.b_vel[1]*0.05
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
