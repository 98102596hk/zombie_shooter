from util import *


GUN_CONFIG = {"pistol" : [15, 1.0, 10, 10], "machine" : [10, 2.0, 15, 1], "shotgun" : [10, 10.0, 10, 10 ]}

class Bullet(pygame.sprite.Sprite):
    def __init__(self, dt=0.2):
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
        self.accel = np.array([0, 0])
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.drag = 0.0
        self.mag_vel = 0
        self.shot = False
        self.type = "pistol"
        self.mass = 1.0
        self.gun_config = GUN_CONFIG.get(self.type)
        self.sound = None
        self.damage = 0
        self.dist = 0.0

    def setup(self, pos, vel=np.array([0, 0])):
        img_name = "bullet/" + self.type + ".png"
        self.gun_config = GUN_CONFIG.get(self.type)
        self.image = pygame.image.load(img_name)
        self.image = pygame.transform.scale(self.image, (int(self.gun_config[2]), int(self.gun_config[2])))
        self.rect = self.image.get_rect()
        self.sound = pygame.mixer.Sound("sound_fx/" + self.type + ".wav")

        if (self.type == "pistol"):
            self.sound.set_volume(0.1)
        elif (self.type == "machine"):
            self.sound.set_volume(0.01)
        elif (self.type == "shotgun"):
            self.sound.set_volume(0.9)
        self.sound.play()

        self.damage = self.gun_config[3]
        self.mag_vel = self.gun_config[0]
        self.mass = self.gun_config[1]
        self.set_vel(normalize(vel))
        self.set_pos(pos)
        self.solver.set_initial_value([self.pos[0], self.pos[1], self.vel[0], self.vel[1]], self.curr_time)


    def set_pos(self, pos):
        self.pos = pos
        self.rect = self.pos


    def set_vel(self, direction):
        self.vel = direction*self.mag_vel


    def f(self, t, state):
        dx = state[2]
        dvx = 0

        dy = state[3]
        dvy = 0

        return [dx, dy, dvx, dvy]


    def update(self):
        self.curr_time += self.dt
        if self.solver.successful():
            self.i += 2


            self.solver.integrate(self.curr_time)
            pos = self.solver.y[0:2]
            self.vel = self.solver.y[2:4]

            if self.type == "shotgun":
                self.dist += length(self.pos - pos)
                if self.dist >= 200.0:
                    self.kill()


            if not out_of_bounds(pos):
                self.set_pos(pos)
            else:
                self.kill()

