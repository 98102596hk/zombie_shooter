from util import *


# CONSTANTS
# =============================================================================
PLAY_MOTION = PLAYER_SPRITE_DIR + "motion/"
PLAY_DEAD = PLAYER_SPRITE_DIR + "dead/1.png"
FX_FLESH_RIP = SOUND_FX_DIR + "flesh_rip.wav"
FX_WASTED = SOUND_FX_DIR + "wasted.wav"
FX_STEP_SAND = SOUND_FX_DIR + "step.wav"

PLAYER_VELOCITY = 3.0
PLAYER_ACCELERATION = 1.0
PLAYER_MASS = 180
PLAYER_DRAG = 0.09
PLAYER_DIMEN = 30
PLAYER_HEALTH = 200
# =============================================================================


# Player Sprite
# =============================================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, dt=0.5):
        pygame.sprite.Sprite.__init__(self)
        self.i = 0
        self.sprite_img = []
        self.image = None
        self.rect = None
        self.angle = 0
        self.dimen = PLAYER_DIMEN
        self.center = np.array([0, 0])

        self.curr_time = 0
        self.dt = dt
        self.pos = np.array([0,0])
        self.vel = np.array([0,0])
        self.mag_vel = PLAYER_VELOCITY
        self.acc = np.array([0, 0])
        self.dir = np.array([0, -1])
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        
        self.mass = PLAYER_MASS
        self.drag = PLAYER_DRAG
        self.gun = "pistol"
        self.health = PLAYER_HEALTH
        self.alive = True

        self.wasted = pygame.mixer.Sound(FX_WASTED)
        self.flesh_rip = pygame.mixer.Sound(FX_FLESH_RIP)
        self.flesh_rip.set_volume(0.3)
        self.step = pygame.mixer.Sound(FX_STEP_SAND)
        self.step.set_volume(0.06)


    def setup(self, pos=np.array([0, 0]), vel=np.array([0, 0])):
        for img_name in os.listdir(PLAY_MOTION):
            self.sprite_img.append(os.path.join(PLAY_MOTION, img_name))

        self.image = pygame.image.load(self.sprite_img[0])
        self.image = pygame.transform.scale(self.image, (self.dimen, self.dimen))
        self.rect = self.image.get_rect()

        # Init RK4 solver
        self.set_pos(pos)
        self.set_acc()
        self.solver.set_initial_value([self.pos[0], self.pos[1], self.vel[0], self.vel[1]], self.curr_time)


    def f(self, t, state):
        dx, dy = state[2:4]
        dvx, dvy = self.acc - self.drag*state[2:4]

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


    def draw(self, screen):
        screen.blit(self.image, self.rect)


    def set_pos(self, pos):
        if length(self.acc) != 0 and (np.fabs(self.vel[0]) > 0.1 or np.fabs(self.vel[1]) > 0.1):
            animate(self)
            rotate(self, self.dir)

            if self.i > 20:
                self.i  = 0
                self.step.play()
        

        self.i += 1
        self.pos = pos
        self.rect = self.pos
        self.center[0] = self.pos[0] + self.dimen/2.0
        self.center[1] = self.pos[1] + self.dimen/2.0

    def set_dir(self, direction):
        self.dir = direction


    def set_acc(self, mag_acc=PLAYER_ACCELERATION):
        self.acc = mag_acc*self.dir


    def dec_health(self):
        self.health -= 5

        if self.health <= 0:
            self.alive = False
            self.image = pygame.image.load(PLAY_DEAD)

            if pygame.mixer.music.get_busy():
                stop_music(0)
            self.wasted.play()
        else:
            self.flesh_rip.play()
# =============================================================================