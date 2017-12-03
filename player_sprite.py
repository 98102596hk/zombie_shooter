from util import *

PLAYER_VELOCITY = 3.0
PLAYER_ACCELERATION = 1.0
PLAYER_MASS = 180
PLAYER_DRAG = 0.09
PLAYER_DIMEN = 30
PLAYER_HEALTH = 200

class Player(pygame.sprite.Sprite):
    def __init__(self, dt=0.5):
        pygame.sprite.Sprite.__init__(self)
        self.i = 0
        self.sprite_img = []
        self.image = None
        self.rect = None
        self.angle = 0
        self.dimen = PLAYER_DIMEN

        self.curr_time = 0
        self.dt = dt
        self.pos = np.array([0,0])
        self.vel = np.array([0,0])
        self.mag_vel = PLAYER_VELOCITY
        self.acc = np.array([0, 0])
        self.dir = np.array([0, -1])
        
        self.mass = PLAYER_MASS
        self.drag = PLAYER_DRAG
        self.gun = "pistol"
        self.health = PLAYER_HEALTH
        
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')

        self.alive = True

        self.flesh_rip = pygame.mixer.Sound('sound_fx/flesh_rip.wav')
        self.flesh_rip.set_volume(0.3)
        self.wasted = pygame.mixer.Sound('sound_fx/wasted.wav')
        self.step = pygame.mixer.Sound('sound_fx/step.wav')
        self.step.set_volume(0.08)

    def setup(self, pos=np.array([0, 0]), vel=np.array([0, 0])):
        for img_name in os.listdir("player/"):
            self.sprite_img.append(os.path.join("player", img_name))

        self.image = pygame.image.load(self.sprite_img[0])
        self.image = pygame.transform.scale(self.image, (self.dimen, self.dimen))
        self.rect = self.image.get_rect()

        self.set_pos(pos)
        self.set_acc()
        self.solver.set_initial_value([self.pos[0], self.pos[1], self.vel[0], self.vel[1]], self.curr_time)

    def set_pos(self, pos):
        if length(self.acc) != 0 and (np.fabs(self.vel[0]) > 0.1 or np.fabs(self.vel[1]) > 0.1):
            animate(self)
            rotate_dir(self, normalize(self.vel))

            if self.i > 20:
                self.i  = 0
                self.step.play()
        

        self.i += 1
        self.pos = pos
        self.rect = self.pos

    def set_dir(self, direction):
        self.dir = direction

    def set_acc(self, mag_acc=PLAYER_ACCELERATION):
        self.acc = np.multiply(self.dir, mag_acc)


    def dec_health(self):
        self.health -= 5

        if self.health <= 0:
            self.alive = False
            self.image = pygame.image.load("dead_player/1.png")

            if pygame.mixer.music.get_busy():
                stop_music(0)
            self.wasted.play()
        else:
            self.flesh_rip.play()

    def f(self, t, state):
        dx = state[2]
        dvx = self.acc[0] - self.drag*state[2]

        dy = state[3]
        dvy = self.acc[1] - self.drag*state[3]

        return [dx, dy, dvx, dvy]

    def update(self):
        if self.alive:
            self.curr_time += self.dt
            if self.solver.successful():

                self.solver.integrate(self.curr_time)
                pos = self.solver.y[0:2]
                self.vel = self.solver.y[2:4]

                pos = check_boundary(self, pos)
                self.set_pos(pos)
