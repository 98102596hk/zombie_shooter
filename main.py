import pygame, sys
import numpy as np
from scipy.integrate import ode

# set up the colors
BLACK = (0, 0, 0)

class Player(pygame.sprite.Sprite):
    def __init__(self, name, mass, color=WHITE, radius=0, imagefile=None):
        pygame.sprite.Sprite.__init__(self)

        self.pos = np.array([0,0])
        self.vel = np.array([0,0])


        if imagefile:
            self.image = load_image(imagefile)
            self.image = pygame.transform.scale(self.image, (int(radius*2), int(radius*2)))
        else:
            self.image = pygame.Surface([radius*2, radius*2])
            self.image.fill(BLACK)
            pygame.draw.circle(self.image, color, (radius, radius), radius, radius)
        


        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
