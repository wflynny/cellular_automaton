import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider
from matplotlib.Collections import RegularPolygonCollection
from mpl_toolkit import make_axes_locatable

class RectangularGrid(BaseGrid):
    def __init__(self):
        BaseGrid.__init__(self)

    def init_image(self, first_frame_arr):
        self.fig, self.ax = plt.subplots()
        self.ax.set_axis_off()

        self.im = self.ax.imshow(first_frame_arr, cmap=cmap, vmin=self.statemin,
                                 vmax=self.statmax, interpolation='lanczos')
        return self.im,

    def update_imate(self, new_frame_arr):
        self.im.set_array(new_frame_arr)
        return self.im,

class HexagonalGrid(BaseGrid):
    def __init__(self):
        # should store cell centers but calculate
        BaseGrid.__init__(self)

    #def init_image(self, first_frame_arr):
    #    self.fig, self.ax = plt.subplots()
    #    self.ax.set_axis_off()

    #    self.im = self.ax.imshow(first_frame_arr, cmap=cmap, vmin=self.statemin,
    #                             vmax=self.statmax, interpolation='lanczos')
    #    return self.im,

class BaseGrid(object):
    def __init__(self, height, width, Nstates, fps=30, cmap='inferno'):
        self.height = height
        self.width = width

        self.Nstates = Nstates
        self.statemin = 0
        self.statemax = Nstates - 1

        self.fps = fps
        self.refresh_interval = int(1000/fps)

        self.cmap = cmap

        self.sliders = []

    def init_image(self, first_frame_arr):
        raise NotImplementedError

    def update_image(self, new_frame_arr):
        raise NotImplementedError

    def add_slider(self, var, label, valmin, valmax):
        if self.sliders == []:
            divider = make_axes_locatable(self.ax)
        else:
            divider = make_axes_locatable(self.sliders[-1].get_axes())

        sax = divider.append_axes("bottom", size="2%", pad=0.025)
        new = Slider(sax, label, valmin, valmax, valinit=var, valfmt='%0.1f')

        @staticmethod
        def update_slider(value, var=var, slider=new):
            var = value
            slider.valtext.set_text('{:.1f}'.format(value))
            self.fig.canvas.draw()

        new.on_changed(update_slider, [var, new])
        self.sliders.append(new)

    def animate(self, update_func):
        anim = animate.FuncAnimation(self.fig, update_func,
                                     interval=self.refresh_interval)

