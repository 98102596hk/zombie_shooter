from util import *

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
        self.m = 5

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