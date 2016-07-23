#!/usr/bin/env python

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

class Graphics:
    @staticmethod
    def plot_heatmaps(heatmap, vmax, title, filename):
        plt.figure()
        #plt.imshow(heatmap, interpolation="nearest", vmin=0, vmax=vmax)
        plt.imshow(heatmap, interpolation="nearest")
        plt.xlabel("Bottom of frame")
        plt.ylabel("Left side of frame")
        plt.colorbar()
        plt.title(title)
        plt.savefig(filename)
        plt.clf()
        plt.close()

    @staticmethod
    def create_histogram(list_of_values, title, filename):
        plt.figure()
        plt.hist(list_of_values, bins=100)
        plt.xlabel("Values")
        plt.ylabel("Frequency")
        plt.title(title)
        plt.savefig(filename)
        plt.clf()
        plt.close()

    @staticmethod
    def plot_values_over_time(list_of_values, title, filename):
        plt.figure()
        plt.plot(list(range(len(list_of_values))), list_of_values)
        plt.xlabel("Frame")
        plt.ylabel("Value")
        plt.title(title)
        plt.savefig(filename)
        plt.clf()
        plt.close()
        title, filename

    @staticmethod
    def create_angles_hist(angles):
        C = 360
        N = C / 20
        each_bin = C / N
        angle_counts = np.zeros(N)

        for each_angle in angles:
            bin_index = int(each_angle / each_bin)
            if bin_index == len(angle_counts):
                bin_index = len(angle_counts) - 1
            angle_counts[bin_index] += 1

        max_count = angle_counts.max()
        normalised = angle_counts / max_count
        return normalised

    @staticmethod
    def draw_circular_hist(angles, plot_title, output_file):
        C = 360
        N = C / 20
        each_bin = C / N

        bottom = 0
        max_height = angles.max()

        theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
        radii = angles
        width = (2*np.pi) / N

        plt.figure()
        ax = plt.subplot(111, polar=True)
        #ax.set_theta_zero_location("W")
        #ax.set_theta_direction(-1)
        bars = ax.bar(theta, radii, width=width, bottom=bottom)
        #ax.set_theta_zero_location("W")

        for r, bar in zip(radii, bars):
            bar.set_facecolor(plt.cm.jet(r))
            bar.set_alpha(0.8)

        #plt.ylim([0, 0.2])
        #plt.ylim([0, 400])

        plt.title(plot_title)
        plt.savefig(output_file)
        plt.clf()
        plt.close()

def main():
    pass

if __name__ == "__main__":
    main()
