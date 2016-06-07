#!/usr/bin/env python

import math

class Metrics:
    @staticmethod
    def calc_distance(x1, y1, x2, y2):
        x_dist = (x2 - x1)
        y_dist = (y2 - y1)
        return math.sqrt(x_dist * x_dist + y_dist * y_dist)

    @staticmethod
    def draw_heatmaps(self, bees_in_time_period, day_period, num_x_cells, num_y_cells, output_dir, que):
        x_bins = 3840/num_x_cells
        y_bins = 2160/num_y_cells

        heatmap_names = ['All', 'Treatment', 'Control', 'Queen']

        centre_dict = {'All': [], 'Treatment': [], 'Control': [], 'Queen': []};
        spread_dict = {'All': [], 'Treatment': [], 'Control': [], 'Queen': []};


        for j, each_time_period in enumerate(bees_in_time_period):
            all_heatmap = np.zeros((num_y_cells,num_x_cells))
            circle1_heatmap = np.zeros((num_y_cells,num_x_cells))
            line2_heatmap = np.zeros((num_y_cells,num_x_cells))
            queen3_heatmap = np.zeros((num_y_cells,num_x_cells))
            list_of_individual_heatmaps = [all_heatmap, circle1_heatmap, line2_heatmap, queen3_heatmap]
            list_of_mean_centres = [None, None, None, None]

            all_xy_heatmap = np.zeros((num_y_cells,num_x_cells))
            circle1_xy_heatmap = np.zeros((num_y_cells,num_x_cells))
            line2_xy_heatmap = np.zeros((num_y_cells,num_x_cells))
            queen3_xy_heatmap = np.zeros((num_y_cells,num_x_cells))
            list_of_all_xy_heatmaps = [all_xy_heatmap, circle1_xy_heatmap, line2_xy_heatmap, queen3_xy_heatmap]

            #print(len(each_time_period))
            for each_bee in each_time_period:
                bee_type = each_bee.tag
                cells_visited = []
                x_coords = each_bee.coords[0].tolist()
                y_coords = each_bee.coords[1].tolist()

                for i, value in enumerate(x_coords):
                    x = int(x_coords[i] / x_bins)
                    y = int(y_coords[i] / y_bins)
                    list_of_all_xy_heatmaps[0][y, x] += 1
                    list_of_all_xy_heatmaps[bee_type][y, x] += 1
                    if [y, x] not in cells_visited:
                        list_of_individual_heatmaps[0][y, x] += 1
                        list_of_individual_heatmaps[bee_type][y, x] += 1
                        cells_visited.append([y, x])

            for ii, heatmap in enumerate(list_of_individual_heatmaps):
                if heatmap.sum() == 0:
                    centre_dict[heatmap_names[ii]].append((np.nan,np.nan))
                    spread_dict[heatmap_names[ii]].append(np.nan)
                    continue
                normalised_heatmap = heatmap / heatmap.sum()
                plt.figure()
                plt.imshow(normalised_heatmap, interpolation="nearest", vmin = 0, vmax = 0.01)
                centre = ndimage.measurements.center_of_mass(heatmap)
                spread = 0
                for y_c in range(0, heatmap.shape[0]):
                    for x_c in range(0, heatmap.shape[1]):
                        spread += Bee.calc_distance(x_c, y_c, centre[1], centre[0]) * (normalised_heatmap)[y_c, x_c]

                plt.plot([centre[1]], [centre[0]], 'ko', markersize=6)
                plt.xlabel("Bottom of frame")
                plt.ylabel("Left side of frame")
                plt.colorbar()
                plt.title(heatmap_names[ii] + ' ' + day_period + ' ' + str(j) + ' Spread: ' + str(round(spread)))
                plt.axis([0, num_x_cells-1, num_y_cells-1, 0])
                saved_file_name = output_dir + str(j) + '_' + day_period + '_individual_' + heatmap_names[ii] + '.png'
                plt.savefig(saved_file_name)
                plt.clf()
                plt.close()

                centre_dict[heatmap_names[ii]].append(centre)
                spread_dict[heatmap_names[ii]].append(spread)


            for ii, heatmap in enumerate(list_of_all_xy_heatmaps):
                if heatmap.sum() == 0:
                    continue
                plt.figure()
                plt.imshow(heatmap / heatmap.sum(), interpolation="nearest", vmin = 0, vmax = 0.005) # 0.01
                plt.xlabel("Bottom of frame")
                plt.ylabel("Left side of frame")
                plt.colorbar()
                plt.title(heatmap_names[ii] + ' ' + day_period + ' ' + str(j))
                saved_file_name = output_dir + str(j) + '_' + day_period + '_xy_' + heatmap_names[ii] + '.png'
                plt.savefig(saved_file_name)
                plt.clf()
                plt.close()



def main():
    pass

if __name__ == "__main__":
    main()
