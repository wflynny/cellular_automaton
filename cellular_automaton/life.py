#!/usr/bin/python
import sys
import argparse
import numpy as np
from scipy.signal import convolve2d
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class GameofLife(object):
    def __init__(self):
        self._parse_args()
        self._setup()

    def _parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--width', type=int, default=50)
        parser.add_argument('--height', type=int, default=50)
        parser.add_argument('--seed', type=int)
        #parser.add_argument('--loc', choices=range(9), type=int, default=4)
        parser.add_argument('--wrap', action='store_true')
        parser.add_argument('species', type=int)
        args = parser.parse_args()

        #if args.species > 2*(args.width/10 - 2) + 2*(args.height/10 - 2):
        if args.species > 8:
            sys.exit("Too many species for game dimensions")

        self.__dict__.update(**vars(args))

    def _setup(self):
        #np.random.seed(self.seed if self.seed else 0)

        # initial board setup
        N = self.species
        self.game = np.zeros((N, self.height, self.width), dtype=int)

        rads = [0] if self.species == 1 else [(self.species+3)/4] * N
        start_t = -3*np.pi/4
        zs = [rad*(np.cos(2*i*np.pi/N + start_t) + 1j *
                   np.sin(2*i*np.pi/N + start_t)) for i, rad in enumerate(rads)]
        locs = zip(np.real(zs), np.imag(zs))

        for k, (i, j) in enumerate(locs, start=1):
            r = np.random.rand(10, 10)
            i = np.round((i + self.width/20. - 0.5)*10)
            j = np.round((j + self.height/20. - 0.5)*10)
            self.game[k-1, i:i+10, j:j+10] = (r > 0.5) * k

        # convolution params
        in2 = np.array([[1,1,1], [1,0,1], [1,1,1]])
        self.convolution_params = dict(mode='same', in2=in2)
        if not self.wrap:
            self.convolution_params.update(dict(boundary='fill', fillvalue=0))
        else:
            self.convolution_params.update(dict(boundary='wrap'))

        # plot setup
        self.fig, self.ax = plt.subplots()
        self.ax.set_xticks([]); self.ax.set_yticks([])

    def _setup_plot(self):
        self.im = self.ax.imshow(self.game.sum(axis=0),
                                 interpolation='nearest', cmap='binary')
        return self.im,

    def step(self, i):
        # convolution for multiple species could work in 2 ways:
        # - each species steps forward in time independently and the future
        #   populations interact somehow
        # - species evolve depending on interactions with other species but this
        #   is challenging.

        # convolute each species (layer) independently
        for k in range(self.species):
            count = convolve2d(self.game[k], **self.convolution_params).astype(int)

            self.game[k] = (k+1)*((count == 3*(k+1)) | ((self.game[k] != 0) & (count == 2*(k+1))))

        #
        #summed = self.game.sum(axis=0)
        maxxed = self.game.min(axis=0)
        #x, y = np.where(summed > self.species)
        if self.species > 1:
            #summed[x, y] = np.random.choice(np.arange(1, k+1), size=x.shape)
            for k in range(self.species):
                x, y = np.where(maxxed > self.game[k])
                self.game[k, x, y] = 0


                #self.game[k][(summed == k+1)] = k+1

        #if (summed > self.species).any():
        #    x, y = np.where(summed > self.species)
        #    z = np.array([convolve2d((summed == k+1), np.ones(3,3), boundary=self.wrap)[summed > self.species]
        #         for k in range(self.species)])
        #    zz = z.argmax(axis=0)
        #    game[zz, x, y] = zz + 1

        # merge into single layer
        self.im.set_array(self.game.max(axis=0))
        return self.im,

    def run(self):
        anim = animation.FuncAnimation(self.fig, self.step, interval=100,
                                       init_func=self._setup_plot, blit=True)
        plt.show()

if __name__ == "__main__":
    gol = GameofLife()
    #gol._setup_plot()
    #plt.show()
    gol.run()
