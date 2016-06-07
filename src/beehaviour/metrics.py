#!/usr/bin/env python

import math
import numpy as np

class Metrics:
    @staticmethod
    def calc_distance(x1, y1, x2, y2):
        x_dist = (x2 - x1)
        y_dist = (y2 - y1)
        return math.sqrt(x_dist * x_dist + y_dist * y_dist)

    @staticmethod
    def generate_heatmaps(beeid_grouped_by_time_period, day_period, num_x_cells, num_y_cells):
        x_bins = 3840/num_x_cells
        y_bins = 2160/num_y_cells

        where_str = add_list_to_where_statement(colname_cond = "HourBin IN", group_list=[str(time) for time in each_group_hours])
        hours_query_result = query_db(table='bees', cols=['BeeID'], where_str=where_str)

        for time_period_beeids in beeid_grouped_by_time_period:
            query_db(table='bees', cols=['BeeID'], where_str=where_str)

        individual_heatmap = np.zeros((num_y_cells,num_x_cells))
        all_xy_heatmap = np.zeros((num_y_cells,num_x_cells))

        for each_bee in each_time_period:
            bee_type = each_bee.tag
            cells_visited = []
            x_coords = each_bee.coords[0].tolist()
            y_coords = each_bee.coords[1].tolist()

            for i, value in enumerate(x_coords):
                x = int(x_coords[i] / x_bins)
                y = int(y_coords[i] / y_bins)
                all_xy_heatmap[y, x] += 1
                if [y, x] not in cells_visited:
                    individual_heatmap[y, x] += 1
                    cells_visited.append([y, x])

        if individual_heatmap.sum() == 0 or all_xy_heatmap.sum() == 0:
            centre = append.((np.nan,np.nan))
            spread = append.((np.nan))

        individual_heatmap[individual_heatmap < 1] = 1
        all_xy_heatmap[all_xy_heatmap < 1] = 1
        normalised_individual_heatmap = heatmap / heatmap.sum()
        normalised_all_xy_heatmap = all_xy_heatmap / heatmap.sum()

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
