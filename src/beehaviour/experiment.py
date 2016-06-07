#!/usr/bin/env python

import datetime
import random
import numpy as np

from .database import query_db
from .graphics import Graphics

class Experiment:
    def __init__(self, hive_id):
        self.hive_id = hive_id

    @staticmethod
    def calc_distance(x1, y1, x2, y2):
        x_dist = (x2 - x1)
        y_dist = (y2 - y1)
        return math.sqrt(x_dist * x_dist + y_dist * y_dist)

    def retrieve_hour_blocks_in_experiment(self, hive_id):
        hours_query_result = query_db(table='bees', cols=['HourBin'], distinct=True, where='HiveID={}'.format(hive_id))

        experiment_hours = []
        for hour_row in hours_query_result:
            experiment_hours.append(hour_row['HourBin'])

        experiment_hours.sort()
        return experiment_hours

    def group_hours_by_night_day(self, sorted_date_times):
        is_day = False
        night_hours = []
        day_hours = []
        current_hours_group = []

        for each_date_time in sorted_date_times:
            each_hour = each_date_time.time().hour
            if each_hour in [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23]:
                if is_day == True:
                    day_hours.append(current_hours_group)
                    is_day = False
                    current_hours_group = [each_date_time]
                else:
                    current_hours_group.append(each_date_time)
            else:
                if is_day == False:
                    night_hours.append(current_hours_group)
                    is_day = True
                    current_hours_group = [each_date_time]
                else:
                    current_hours_group.append(each_date_time)

        if is_day:
            day_hours.append(current_hours_group)
        else:
            night_hours.append(current_hours_group)

        return (day_hours, night_hours)

    def retrieve_beeids_in_time_period(self, time_period_list_datetimes):
        group_beeids = []
        for each_group_hours in time_period_list_datetimes:
            beeids_in_time_group = []
            hours_query_result = query_db(table='bees', cols=['BeeID'], group_condition='HourBin IN', group_list=[str(time) for time in each_group_hours])

            for bee_row in hours_query_result:
                beeids_in_time_group.append(bee_row['BeeID'])

            group_beeids.append(beeids_in_time_group)

        return group_beeids

    def merge_shuffle_day_night_beeids(self, day_grouped_beeids, night_grouped_beeids, shuffle_iterations):
        combined_day_night_bee_ids = []
        for i, time_grouped_ids in enumerate(day_grouped_beeids):
            try:
                group_day_night = day_grouped_beeids[i] + night_grouped_beeids[i]
                combined_day_night_bee_ids.append(group_day_night)
            except Exception:
                break

        shuffled_day_beeids_seed_dict = {}
        shuffled_night_beeids_seed_dict = {}
        for i in range(shuffle_iterations):
            random.seed(i)
            shuffled_day_beeids_seed_dict[i] = []
            shuffled_night_beeids_seed_dict[i] = []

            for j, combined_grouped_ids in enumerate(combined_day_night_bee_ids):
                random.shuffle(combined_grouped_ids)
                random_shuffled_day = combined_grouped_ids[:len(day_grouped_beeids[j])]
                random_shuffled_night = combined_grouped_ids[len(day_grouped_beeids[j]):]

                shuffled_day_beeids_seed_dict[i].append(random_shuffled_day)
                shuffled_night_beeids_seed_dict[i].append(random_shuffled_night)

        return (shuffled_day_beeids_seed_dict, shuffled_night_beeids_seed_dict)

    def retrieve_bee_id_path(self, bee_id):
        coord_rows = query_db(table='bee_coords', cols=['PathID', 'Frame', 'X', 'Y'], where='PathID IN', subquery='SELECT PathID FROM paths WHERE BeeID={}'.format(bee_id))
        coord_rows_sorted = sorted(coord_rows, key=lambda k: k['Frame'])

        coord_path_lists = {'X':[],'Y':[]}
        x_coords = []
        y_coords = []
        current_path_id = coord_rows_sorted[0]['PathID']
        for row in coord_rows_sorted:
            if row['PathID'] == current_path_id:
                x_coords.append(row['X'])
                y_coords.append(row['Y'])
            else:
                coord_path_lists['X'].append(x_coords)
                coord_path_lists['Y'].append(y_coords)
                x_coords = [row['X']]
                y_coords = [row['Y']]
                current_path_id = row['PathID']

        coord_path_lists['X'].append(x_coords)
        coord_path_lists['Y'].append(y_coords)

        return coord_path_lists

    def generate_heatmaps(self, list_bee_ids, num_x_cells, num_y_cells, plot_title):
        x_bins = 3840/num_x_cells
        y_bins = 2160/num_y_cells
        cells_visited = []

        individual_heatmap = np.zeros((num_y_cells,num_x_cells))
        all_xy_heatmap = np.zeros((num_y_cells,num_x_cells))

        for bee_id in list_bee_ids:
            coord_path_lists = self.retrieve_bee_id_path(bee_id)
            for i, x_paths_list in enumerate(coord_path_lists['X']):
                for j, x_coord in enumerate(coord_path_lists['X'][i]):
                    x = int(coord_path_lists['X'][i][j] / x_bins)
                    y = int(coord_path_lists['Y'][i][j] / y_bins)
                    all_xy_heatmap[y, x] += 1
                    if [y, x] not in cells_visited:
                        individual_heatmap[y, x] += 1
                        cells_visited.append([y, x])

        if individual_heatmap.sum() == 0:
            return None
            #centre = append.((np.nan,np.nan))
            #spread = append.((np.nan))

        individual_heatmap[individual_heatmap < 1] = 1
        all_xy_heatmap[all_xy_heatmap < 1] = 1
        normalised_individual_heatmap = heatmap / heatmap.sum()
        normalised_all_xy_heatmap = all_xy_heatmap / heatmap.sum()

        Graphics.plot_heatmaps(normalised_individual_heatmap, 0.05, plot_title, '/Users/jack/Research/DBee/results/' + plot_title + 'individual.png')
        Graphics.plot_heatmaps(normalised_all_xy_heatmap, 0.05, plot_title, '/Users/jack/Research/DBee/results/' + plot_title + 'xy.png')

    #def x():
        #Metrics.generate_heatmaps

def main():
    pass
    #query_db(table='bees', cols=['HourBin'], where='HiveID=1', group_condition='AND HiveID IN', group_list=[1,2,3])
    #query_db(table='bees', cols=['HourBin'], where='HiveID=1')
    #query_db(table='bees', cols=['HourBin'], group_condition='HiveID IN', group_list=[1,2,3])

    #query_db(table='paths', cols=['*'], where='BeeID IN', subquery='select beeid from bees where beeid=0')

    #query_db(table='paths', cols=['*'], where='BeeID IN', subquery='select beeid from bees where beeid IN', subquery_list=[0,1])

    #select * from paths where beeid in (select beeid from bees where beeid=0);

    #beeid

    #query_db(table, cols, distinct=False, fetchall=True, where='', join_operator='', group_condition='', group_list=[], subquery_where='', subquery_list=[]):

    #coordinate_rows =query_db(table='bee_coords', cols=['PathID', 'Frame', 'X', 'Y'], where='PathID IN', subquery='SELECT PathID FROM paths WHERE BeeID IN', subquery_list=[0,1])

    #print(x)



if __name__ == "__main__":
    main()
