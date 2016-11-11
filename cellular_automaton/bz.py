#!/usr/bin/python
import sys
import argparse
import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider

class BZReaction(object):
    def __init__(self):
        self._parse_args()
        self._setup()

    def _parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--width', type=int, default=100)
        parser.add_argument('--height', type=int, default=100)
        parser.add_argument('--seed', type=int)
        parser.add_argument('--wrap', action='store_true')
        parser.add_argument('k1', type=float)
        parser.add_argument('k2', type=float)
        parser.add_argument('g', type=float)
        args = parser.parse_args()

        self.__dict__.update(**vars(args))

    def _setup(self):
        if self.seed:
            np.random.seed(self.seed)

        # initial board setup
        self.statemax = 255
        self.game = np.random.random_integers(0, self.statemax,
                                              size=(self.height, self.width))
        self.maxarr = np.ones_like(self.game) * self.statemax

        # convolution params
        in2 = np.array([[1,1,1], [1,0,1], [1,1,1]])
        self.convolution_params = dict(mode='same', in2=in2)
        if not self.wrap:
            self.convolution_params.update(dict(boundary='fill', fillvalue=0))
        else:
            self.convolution_params.update(dict(boundary='wrap'))

        # plot setup
        self.fig, self.ax = plt.subplots()
        self.ax.set_axis_off()

        self.k1ax = self.fig.add_axes([0.2, 0.06, 0.6, 0.02])
        self.k2ax = self.fig.add_axes([0.2, 0.04, 0.6, 0.02])
        self.gax = self.fig.add_axes([0.2, 0.02, 0.6, 0.02])

        self.k1slider = Slider(self.k1ax, '$k_1$', 0.01, 3, valinit=self.k1, valfmt='%0.1f')
        self.k1slider.on_changed(self._update_k1)
        self.k2slider = Slider(self.k2ax, '$k_2$', 0.01, 3, valinit=self.k2, valfmt='%0.1f')
        self.k2slider.on_changed(self._update_k2)
        self.gslider = Slider(self.gax, '$g$', 1, self.statemax, valinit=self.g, valfmt='%0.1f')
        self.gslider.on_changed(self._update_g)

    def _update_k1(self, value):
        self.k1 = value
        self.k1slider.valtext.set_text('{}'.format(value))
        self.fig.canvas.draw()

    def _update_k2(self, value):
        self.k2 = value
        self.k2slider.valtext.set_text('{}'.format(value))
        self.fig.canvas.draw()

    def _update_g(self, value):
        self.g = value
        self.gslider.valtext.set_text('{}'.format(value))
        self.fig.canvas.draw()

    def _setup_plot(self):
        cmap = 'inferno'
        self.im = self.ax.imshow(self.game, cmap=cmap, vmin=0,
                                 vmax=self.statemax,
                                 extent=[0,self.height,0,self.width],
                                 interpolation='lanczos')
        return self.im,

    def step(self, i):
        # mask of 0 < infected < 255 cells
        infected = ((self.game > 0) & (self.statemax > self.game)).astype(int)
        # mask of sick == 255 cells
        sick = ((self.game == self.statemax)).astype(int)
        # count of infected neighbors
        a = convolve2d(infected, **self.convolution_params).astype(int)
        # count of sick neighbors
        b = convolve2d(sick, **self.convolution_params).astype(int)
        # total values of neighboring cells + SELF <-- key to this not being garbage
        s = convolve2d(self.game, **self.convolution_params).astype(int) + self.game

        # healthy cells get infected
        case1 = (a/self.k1 + b/self.k2) * (self.game == 0)
        # sick cells turn healthy
        case2 = 0 * (self.game == self.statemax)
        # infected cells get more infected?
        case3 = (s/(a+b+1).astype(float) + self.g) * \
                ((self.game!=0) & (self.game!=self.statemax))

        # So here's a decision:
        # - Do we cap the game state at statemax or let it roll over, i.e. mod?
        # here I'm just capping it.
        case3 = np.minimum(case3, self.maxarr)
        self.game = (case1 + case2 + case3).astype(int)
        #self.game = np.mod((case1 + case2 + case3).astype(int), self.statemax)

        self.im.set_array(self.game)
        return self.im,

    def run(self):
        anim = animation.FuncAnimation(self.fig, self.step, interval=20,
                                       init_func=self._setup_plot)#, blit=True)
        plt.show()

if __name__ == "__main__":
    bzr = BZReaction()
    bzr.run()
