from util import *


class Player(pygame.sprite.Sprite):
    def __init__(self, dt=0.5):
        pygame.sprite.Sprite.__init__(self)
        self.i = 0
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
        self.health = HUMAN_HEALTH
        self.alive = True
        self.h = 0
        self.w = 0
        self.dir = np.array([0, -1])

    def setup(self, pos=np.array([0, 0]), vel=np.array([0, 0])):
        for img_name in os.listdir("player/"):
            self.sprite_img.append(os.path.join("player", img_name))

        self.image = pygame.image.load(self.sprite_img[0])
        self.image = pygame.transform.scale(self.image, (int(30), int(60)))
        self.rect = self.image.get_rect()
        self.h = self.image.get_height()
        self.w = self.image.get_width()

        self.set_vel(vel)
        self.set_pos(pos)
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
