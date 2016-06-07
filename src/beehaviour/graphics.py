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


def main():
    pass

if __name__ == "__main__":
    main()
