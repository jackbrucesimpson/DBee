#!/usr/bin/env python

import datetime
import random
import numpy as np
import math
from scipy import ndimage

from .db import DB
from .graphics import Graphics
from .bee import Bee

class Experiment:
    def __init__(self, hive_id):
        self.hive_id = hive_id
        self.output_dir = '/Users/jack/Research/DBee/results/'

        # Treatment (circle 1), Control (rectangle 2), queen: (blank 3)
        self.tag_type_beeids = {1:[],2:[],3:[]}

        self.treatment_circ1_beeids = []
        self.control_rect2_beeids = []
        self.queen_blank3_beeids = []

        self.num_x_cells = 40
        self.num_y_cells = 20
        self.x_bins = 3840/self.num_x_cells
        self.y_bins = 2160/self.num_y_cells
        self.frames_per_window = 25
        self.min_angle_speed = 40

        # time_period = 'day', 'night'
        # result_type = 'real', 'shuffled', 'bootstrapped'
        self.output = {'spread':[], 'speed_mean':[], 'speed_median':[], 'time_period':[], 'day_num':[], 'result_type':[], 'spread_diff':[], 'speed_diff_mean':[], 'speed_diff_median':[]}

        hour_blocks_in_experiment = self.retrieve_hour_blocks_in_experiment(hive_id)
        day_hour_bins, night_hour_bins = self.group_hours_by_night_day(hour_blocks_in_experiment)

        self.day_grouped_beeids = self.retrieve_beeids_in_time_period(day_hour_bins)
        self.night_grouped_beeids = self.retrieve_beeids_in_time_period(night_hour_bins)

    @staticmethod
    def calc_distance(x1, y1, x2, y2):
        x_dist = (x2 - x1)
        y_dist = (y2 - y1)
        return math.sqrt(x_dist * x_dist + y_dist * y_dist)

    @staticmethod
    def absolute_angle_degree(x1, y1, x2, y2):
        deltax = x2 - x1
        deltay = y2 - y1
        rad = math.atan2(deltay, deltax)
        angle = math.degrees(rad)
        if angle < 0:
            angle += 360
        return angle

    def retrieve_hour_blocks_in_experiment(self, hive_id):
        db = DB()
        query_statement = db.query_string(table='bees', cols=['HourBin'], distinct=True, where='HiveID={}'.format(hive_id))
        hours_query_result = db.query(query_statement)
        db.close()

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
        db = DB()
        for each_group_hours in time_period_list_datetimes:
            beeids_in_time_group = []
            query_statement = db.query_string(table='bees', cols=['BeeID', 'TagID', 'TagConfidence'], group_condition='HourBin IN', group_list=[str(time) for time in each_group_hours])
            hours_query_result = db.query(query_statement)
            for bee_row in hours_query_result:#[:100]:
                beeids_in_time_group.append(bee_row['BeeID'])
                if bee_row['TagConfidence'] > 0.8:
                    self.tag_type_beeids[bee_row['TagID']].append(bee_row['BeeID'])

            group_beeids.append(beeids_in_time_group)

        db.close()
        return group_beeids

        return (shuffled_day_beeids, shuffled_night_beeids)

    def calculate_day_night_metrics(self, day_num):
        print('Period', day_num)
        day_beeids = self.day_grouped_beeids[day_num]
        night_beeids = self.night_grouped_beeids[day_num]
        combined_day_night_beeids = day_beeids + night_beeids
        bee_id_dict = self.retrieve_process_bees(combined_day_night_beeids)

        day_spread = self.generate_heatmaps(day_beeids, bee_id_dict, 'day_{}'.format(day_num))
        night_spread = self.generate_heatmaps(night_beeids, bee_id_dict, 'night_{}'.format(day_num))
        mean_day_speed, median_day_speed = self.generate_speeds(day_beeids, bee_id_dict, 'day_{}'.format(day_num))
        mean_night_speed, median_night_speed = self.generate_speeds(night_beeids, bee_id_dict, 'night_{}'.format(day_num))

        self.output['spread'].extend([night_spread, day_spread])
        self.output['speed_mean'].extend([mean_night_speed, mean_day_speed])
        self.output['speed_median'].extend([median_night_speed, median_day_speed])
        self.output['time_period'].extend(['night', 'day'])
        self.output['day_num'].extend([day_num, day_num])
        self.output['result_type'].extend(['real', 'real'])
        self.output['spread_diff'].extend([abs(day_spread - night_spread),np.nan])
        self.output['speed_diff_mean'].extend([abs(mean_day_speed - mean_night_speed),np.nan])
        self.output['speed_diff_median'].extend([abs(median_day_speed - median_night_speed),np.nan])

        self.permutation_tests(day_beeids, night_beeids, combined_day_night_beeids, day_num, num_iterations)

    def permutation_tests(self, day_beeids, night_beeids, combined_day_night_beeids, day_num, num_iterations):
        for i in range(num_iterations):
            shuffled_day_beeids = np.random.choice(combined_day_night_beeids, len(day_beeids), replace=True)
            shuffled_night_beeids = np.random.choice(combined_day_night_beeids, len(night_beeids), replace=True)

            day_spread = self.generate_heatmaps(shuffled_day_beeids, bee_id_dict, 'shuffled_spread_day_{}_{}'.format(day_num))
            night_spread = self.generate_heatmaps(shuffled_night_beeids, bee_id_dict, 'shuffled_spread_night_{}_{}'.format(day_num))
            mean_day_speed, median_day_speed = self.generate_speeds(shuffled_day_beeids, bee_id_dict, 'shuffled_speed_day_{}_{}'.format(day_num, i))
            mean_night_speed, median_night_speed = self.generate_speeds(shuffled_night_beeids, bee_id_dict, 'shuffled_speed_night_{}_{}'.format(day_num, i))

            self.output['spread'].extend([night_spread, day_spread])
            self.output['speed_mean'].extend([mean_night_speed, mean_day_speed])
            self.output['speed_median'].extend([median_night_speed, median_day_speed])
            self.output['time_period'].extend(['night', 'day'])
            self.output['day_num'].extend([day_num, day_num])
            self.output['result_type'].extend(['shuffled', 'shuffled'])
            self.output['spread_diff'].extend([abs(day_spread - night_spread),np.nan])
            self.output['speed_diff_mean'].extend([abs(mean_day_speed - mean_night_speed),np.nan])
            self.output['speed_diff_median'].extend([abs(median_day_speed - median_night_speed),np.nan])

            bootstrapped_day_beeids = np.random.choice(day_beeids, len(day_beeids), replace=True)
            bootstrapped_night_beeids = np.random.choice(night_beeids, len(night_beeids), replace=True)

            day_spread = self.generate_heatmaps(bootstrapped_day_beeids, bee_id_dict, 'shuffled_spread_day_{}_{}'.format(day_num))
            night_spread = self.generate_heatmaps(bootstrapped_night_beeids, bee_id_dict, 'shuffled_spread_night_{}_{}'.format(day_num))
            mean_day_speed, median_day_speed = self.generate_speeds(bootstrapped_day_beeids, bee_id_dict, 'shuffled_speed_day_{}_{}'.format(day_num, i))
            mean_night_speed, median_night_speed = self.generate_speeds(bootstrapped_night_beeids, bee_id_dict, 'shuffled_speed_night_{}_{}'.format(day_num, i))

            self.output['spread'].extend([night_spread, day_spread])
            self.output['speed_mean'].extend([mean_night_speed, mean_day_speed])
            self.output['speed_median'].extend([median_night_speed, median_day_speed])
            self.output['time_period'].extend(['night', 'day'])
            self.output['day_num'].extend([day_num, day_num])
            self.output['result_type'].extend(['shuffled', 'shuffled'])
            self.output['spread_diff'].extend([abs(day_spread - night_spread),np.nan])
            self.output['speed_diff_mean'].extend([abs(mean_day_speed - mean_night_speed),np.nan])
            self.output['speed_diff_median'].extend([abs(median_day_speed - median_night_speed),np.nan])

    def retrieve_process_bees(self, list_bee_ids):
        bee_id_dict = {bee_id:Bee(bee_id) for bee_id in list_bee_ids}

        db = DB()
        for i in range(0, len(list_bee_ids),200):
            subset_bee_ids = list_bee_ids[i:i+200]
            query_statement = db.query_string(table='bee_coords, paths', cols=['paths.BeeID', 'bee_coords.PathID', 'bee_coords.Frame', 'bee_coords.X', 'bee_coords.Y'], where='bee_coords.PathID = paths.PathID', group_condition='AND BeeID IN', group_list=subset_bee_ids, order='ORDER BY Frame ASC')
            coord_rows = db.query(query_statement)

            for row in coord_rows:
                bee_id = row['BeeID']
                x = int(row['X'] / self.x_bins)
                y = int(row['Y'] / self.y_bins)
                yx_coord = (y, x)
                # heatmap location
                if yx_coord in bee_id_dict[bee_id].cells_visited:
                    bee_id_dict[bee_id].cells_visited[yx_coord] += 1
                else:
                    bee_id_dict[bee_id].cells_visited[yx_coord] = 1

                # calculate speeds and angles
                if bee_id_dict[bee_id].last_path_id == row['PathID']:
                    bee_id_dict[bee_id].path_length += 1
                    if bee_id_dict[bee_id].path_length == self.frames_per_window:
                        current_speed = Experiment.calc_distance(row['X'], row['Y'], bee_id_dict[bee_id].last_x, bee_id_dict[bee_id].last_y)
                        bee_id_dict[bee_id].list_speeds.append(current_speed)
                        if current_speed >= self.min_angle_speed:
                            angle = Experiment.absolute_angle_degree(row['X'], row['Y'], bee_id_dict[bee_id].last_x, bee_id_dict[bee_id].last_y)
                            bee_id_dict[bee_id].list_angles.append(angle)

                        bee_id_dict[bee_id].path_length = 1
                        bee_id_dict[bee_id].last_x = row['X']
                        bee_id_dict[bee_id].last_y = row['Y']


                else:
                    bee_id_dict[bee_id].last_path_id = row['PathID']
                    bee_id_dict[bee_id].path_length = 1
                    bee_id_dict[bee_id].last_x = row['X']
                    bee_id_dict[bee_id].last_y = row['Y']

        db.close()
        return bee_id_dict

    def generate_heatmaps(self, list_bee_ids, bee_id_dict, plot_title):
        individual_heatmap = np.zeros((self.num_y_cells, self.num_x_cells))
        all_xy_heatmap = np.zeros((self.num_y_cells, self.num_x_cells))

        for bee_id in list_bee_ids:
            bee = bee_id_dict[bee_id]
            for yx_coord in bee.cells_visited:
                y, x = yx_coord
                all_xy_heatmap[y, x] += bee.cells_visited[yx_coord]
                individual_heatmap[y, x] += 1

        if individual_heatmap.sum() == 0:
            return None

        normalised_individual_heatmap = individual_heatmap / individual_heatmap.sum()
        normalised_all_xy_heatmap = all_xy_heatmap / all_xy_heatmap.sum()

        centre = ndimage.measurements.center_of_mass(normalised_individual_heatmap)
        spread = 0
        for y_c in range(0, normalised_individual_heatmap.shape[0]):
            for x_c in range(0, normalised_individual_heatmap.shape[1]):
                spread += Experiment.calc_distance(x_c, y_c, centre[1], centre[0]) * normalised_individual_heatmap[y_c, x_c]

        #Graphics.plot_heatmaps(normalised_individual_heatmap, 0.01, plot_title, '{}id{}_{}_hm_individual.png'.format(self.output_dir, self.hive_id, plot_title))
        #Graphics.plot_heatmaps(normalised_all_xy_heatmap, 0.01, plot_title, '{}id{}_{}_hm_xy.png'.format(self.output_dir, self.hive_id, plot_title))

        return spread

    def generate_speeds(self, list_bee_ids, bee_id_dict, plot_title):
        all_speeds = []
        for bee_id in list_bee_ids:
            bee = bee_id_dict[bee_id]
            all_speeds.extend(bee.list_speeds)

        if 'shuffled' not in plot_title:
            Graphics.create_histogram(all_speeds, plot_title, '{}id{}_{}_speeds_hist.png'.format(self.output_dir, self.hive_id, plot_title))
        return (np.mean(all_speeds), np.median(all_speeds))

    def generate_angles(self, list_bee_ids, bee_id_dict, plot_title):
        angles_of_bees = np.zeros(360 / 20)
        for bee_id in list_bee_ids:
            bee = bee_id_dict[bee_id]
            if len(bee.list_angles) > 0:
                angles_of_bees += Graphics.create_angles_hist(bee.list_angles)

        Graphics.draw_circular_hist(angles_of_bees, plot_title, '{}id_{}_{}_angles.png'.format(self.output_dir, self.hive_id, plot_title))

        return None

def main():
    pass

if __name__ == "__main__":
    main()
