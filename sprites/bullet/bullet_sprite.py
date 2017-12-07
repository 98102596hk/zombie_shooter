from util import *


# GUN CONFIGURATION
# =============================================================================
#             Weapon Type  Bullet Speed, Bullet Mass, Bullet Dimen, Damage
GUN_CONFIG = {"pistol"  : [15,           1,           10,           10], \
              "machine" : [10,           1,           15,           1], \
              "shotgun" : [15,           10.0,        15,           50]}

SHOTGUN_DEPTH = 200.0
# =============================================================================


# Bullet Sprite
# =============================================================================
class Bullet(pygame.sprite.Sprite):
    def __init__(self, dt=0.2):
        pygame.sprite.Sprite.__init__(self)
        self.i = 0
        self.angle = 0
        self.sprite_img = []
        self.image = None
        self.rect = None
        self.center = np.array([0, 0])
        
        self.pos = np.array([0,0])
        self.vel = np.array([0,0])
        self.mag_vel = 0
        self.curr_time = 0
        self.dt = dt
        self.mass = 1.0
        self.drag = 0.0
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')

        self.type = "pistol"
        self.gun_config = GUN_CONFIG.get(self.type)
        self.dimen = self.gun_config[2]
        self.sound = None
        self.damage = 0
        
        self.shot = False
        self.dist = 0.0


    def setup(self, pos, vel=np.array([0, 0])):
        # Get gun configuration and set up bullet image based on gun type
        img_name = BULLET_SPRITE_DIR + self.type + ".png"
        self.gun_config = GUN_CONFIG.get(self.type)
        self.dimen = self.gun_config[2]
        self.image = pygame.image.load(img_name)
        self.image = pygame.transform.scale(self.image, (int(self.dimen), int(self.dimen)))
        self.rect = self.image.get_rect()

        # Set up the gun fire sound and play it
        self.sound = pygame.mixer.Sound(SOUND_FX_DIR + self.type + ".wav")
        if (self.type == "pistol"):
            self.sound.set_volume(0.1)
        elif (self.type == "machine"):
            self.sound.set_volume(0.05)
        elif (self.type == "shotgun"):
            self.sound.set_volume(0.9)
        self.sound.play()
        
        # Get bullet details
        self.mag_vel = self.gun_config[0]
        self.mass = self.gun_config[1]
        self.damage = self.gun_config[3]
        
        # Init RK4 solver
        self.set_vel(vel)
        self.set_pos(pos)
        self.solver.set_initial_value([self.pos[0], self.pos[1], self.vel[0], self.vel[1]], self.curr_time)


    def f(self, t, state):
        dx, dy = state[2:4] 

        return [dx, dy, 0, 0]


    def update(self):
        self.curr_time += self.dt
        if self.solver.successful():
            self.i += 2

            self.solver.integrate(self.curr_time)
            pos = self.solver.y[0:2]
            self.vel = self.solver.y[2:4]

            if self.type == "shotgun":
                self.dist += length(self.pos - pos)
                if self.dist >= SHOTGUN_DEPTH:
                    self.kill()

            if not out_of_bounds(pos):
                self.set_pos(pos)
            else:
                self.kill()


    def set_pos(self, pos):
        self.pos = pos
        self.rect = self.pos
        self.center[0] = self.pos[0] + self.dimen/2.0
        self.center[1] = self.pos[1] + self.dimen/2.0

    def set_vel(self, direction):
        self.vel = direction*self.mag_vel
# =============================================================================

