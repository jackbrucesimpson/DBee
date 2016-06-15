#!/usr/bin/env python

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

class Graphics:
    @staticmethod
    def plot_heatmaps(heatmap, vmax, title, filename):
        plt.figure()
        plt.imshow(heatmap, interpolation="nearest", vmin=0, vmax=vmax)
        plt.xlabel("Bottom of frame")
        plt.ylabel("Left side of frame")
        plt.colorbar()
        plt.title(title)
        plt.savefig(filename)
        plt.clf()
        plt.close()

    @staticmethod
    def plot_day_night_spread(data, title, filename):
        pass

    @staticmethod
    def plot_day_night_speed(real_day_speed_means, real_night_speed_means, title, filename):
        pass

def main():
    pass

if __name__ == "__main__":
    main()
