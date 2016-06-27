#!/usr/bin/env python

import datetime
import random
import numpy as np
import math
import copy
from scipy import ndimage

from .db import DB
from .graphics import Graphics
from .bee import Bee

class Experiment:
    def __init__(self, hive_id):
        self.hive_id = hive_id
        self.output_dir = '/Users/jack/Research/DBee/results/'

        self.num_x_cells = 40
        self.num_y_cells = 20
        self.x_bins = 3840/self.num_x_cells
        self.y_bins = 2160/self.num_y_cells
        self.frames_per_window = 25
        self.min_angle_speed = 60
        self.tag_confidence_percentage = 0.8
        self.min_tracked_for_classification = 100
        self.min_time_tracked = 25 * 5

        # time_period = 'day', 'night'
        # result_type = 'real', 'shuffled', 'bootstrapped'
        # tag_type = 0: unclassified, 1: circle treatment, 2: rectangle control, 3: blank queen, 'All': All tags
        self.output = {'spread_all_tracked_individuals': [],
                        'spread_all_tracked_all_xy': [],
                        'spread_min_tracked_individuals': [],
                        'spread_min_tracked_all_xy': [],
                        'diff_spread_all_tracked_individuals': [],
                        'diff_spread_all_tracked_all_xy': [],
                        'diff_spread_min_tracked_individuals': [],
                        'diff_spread_min_tracked_all_xy': [],
                        'mean_all_tracked_speeds': [],
                        'mean_min_tracked_speeds': [],
                        'median_all_tracked_speeds': [],
                        'median_min_tracked_speeds': [],
                        'diff_mean_all_tracked_speeds': [],
                        'diff_mean_min_tracked_speeds': [],
                        'diff_median_all_tracked_speeds': [],
                        'diff_median_min_tracked_speeds': [],
                        'day_num': [],
                        'time_period': [],
                        'result_type': [],
                        'tag_type': []}

        hour_blocks_in_experiment = self.retrieve_hour_blocks_in_experiment(hive_id)
        #print(hive_id)
        #print(hour_blocks_in_experiment)
        day_hour_bins, night_hour_bins = self.group_hours_by_night_day(hour_blocks_in_experiment)

        self.day_grouped_bees = self.retrieve_bees_in_time_period(day_hour_bins)
        self.night_grouped_bees = self.retrieve_bees_in_time_period(night_hour_bins)

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

        #print(sorted_date_times)

        for each_date_time in sorted_date_times:
            each_hour = each_date_time.time().hour
            #print(each_hour)
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

        #print(night_hours)
        return (day_hours, night_hours)

    def retrieve_bees_in_time_period(self, time_period_list_datetimes):
        group_bees = []
        db = DB()
        #print(time_period_list_datetimes)
        for each_group_hours in time_period_list_datetimes:
            #print(each_group_hours)
            bees_in_time_group = []
            query_statement = db.query_string(table='bees', cols=['BeeID', 'TagID', 'TagConfidence', 'LengthTracked'], group_condition='HourBin IN', group_list=[str(time) for time in each_group_hours])
            #print(query_statement)
            hours_query_result = db.query(query_statement)
            for bee_row in hours_query_result:#[:100]: ##### change
                #print()
                if bee_row['TagConfidence'] > self.tag_confidence_percentage and bee_row['LengthTracked'] > self.min_tracked_for_classification:
                    bee = Bee(bee_row['BeeID'], bee_row['TagID'], bee_row['LengthTracked'])
                    bees_in_time_group.append(bee)
                else:
                    bee = Bee(bee_row['BeeID'], 0, bee_row['LengthTracked'])
                    bees_in_time_group.append(bee)

            group_bees.append(bees_in_time_group)

        db.close()
        return group_bees

    def calculate_day_night_metrics(self, day_num):
        print('Period', day_num)
        day_bees = self.day_grouped_bees[day_num]
        night_bees = self.night_grouped_bees[day_num]
        combined_day_night_bees = day_bees + night_bees
        bee_id_dict = self.retrieve_process_bees(combined_day_night_bees)

        day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy = self.generate_heatmaps(day_bees, bee_id_dict, 'day_{}'.format(day_num))
        night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy = self.generate_heatmaps(night_bees, bee_id_dict, 'night_{}'.format(day_num))

        day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds = self.generate_speeds(day_bees, bee_id_dict, 'day_{}'.format(day_num))
        night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds = self.generate_speeds(night_bees, bee_id_dict, 'night_{}'.format(day_num))

        #self.generate_angles(day_beeids, bee_id_dict, 'day_{}'.format(day_num))
        #self.generate_angles(night_beeids, bee_id_dict, 'night_{}'.format(day_num))

        self.log_output(day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy,
                        night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy,
                        day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds,
                        night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds,
                        day_num, 'real')

        self.permutation_tests(day_bees, night_bees, combined_day_night_bees, bee_id_dict, day_num, 1000)

    def permutation_tests(self, day_bees, night_bees, combined_day_night_bees, bee_id_dict, day_num, num_iterations):
        for i in range(num_iterations):
            shuffled_day_bees = np.random.choice(combined_day_night_bees, len(day_bees), replace=True)
            shuffled_night_bees = np.random.choice(combined_day_night_bees, len(night_bees), replace=True)

            day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy = self.generate_heatmaps(shuffled_day_bees, bee_id_dict, 'shuffled_spread_day_{}_{}'.format(day_num, i))
            night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy = self.generate_heatmaps(shuffled_night_bees, bee_id_dict, 'shuffled_spread_night_{}_{}'.format(day_num, i))
            day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds = self.generate_speeds(shuffled_day_bees, bee_id_dict, 'shuffled_speed_day_{}_{}'.format(day_num, i))
            night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds = self.generate_speeds(shuffled_night_bees, bee_id_dict, 'shuffled_speed_night_{}_{}'.format(day_num, i))

            self.log_output(day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy,
                            night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy,
                            day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds,
                            night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds,
                            day_num, 'shuffled')

            bootstrapped_day_bees = np.random.choice(day_bees, len(day_bees), replace=True)
            bootstrapped_night_bees = np.random.choice(night_bees, len(night_bees), replace=True)

            day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy = self.generate_heatmaps(bootstrapped_day_bees, bee_id_dict, 'shuffled_spread_day_{}_{}'.format(day_num, i))
            night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy = self.generate_heatmaps(bootstrapped_night_bees, bee_id_dict, 'shuffled_spread_night_{}_{}'.format(day_num, i))
            day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds = self.generate_speeds(bootstrapped_day_bees, bee_id_dict, 'shuffled_speed_day_{}_{}'.format(day_num, i))
            night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds = self.generate_speeds(bootstrapped_night_bees, bee_id_dict, 'shuffled_speed_night_{}_{}'.format(day_num, i))

            self.log_output(day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy,
                            night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy,
                            day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds,
                            night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds,
                            day_num, 'bootstrapped')

    def retrieve_process_bees(self, list_bees):
        bee_id_dict = {bee.bee_id: bee for bee in list_bees}
        list_bee_ids = list(bee_id_dict.keys())

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

    def generate_heatmaps(self, list_bees, bee_id_dict, plot_title):
        all_tracked_individuals_heatmaps = {0: np.zeros((self.num_y_cells, self.num_x_cells)),
                                            1: np.zeros((self.num_y_cells, self.num_x_cells)),
                                            2: np.zeros((self.num_y_cells, self.num_x_cells)),
                                            3: np.zeros((self.num_y_cells, self.num_x_cells)),
                                            'All': np.zeros((self.num_y_cells, self.num_x_cells))}
        all_tracked_all_xy_points_heatmaps = copy.deepcopy(all_tracked_individuals_heatmaps)
        min_tracked_individuals_heatmaps = copy.deepcopy(all_tracked_individuals_heatmaps)
        min_tracked_all_xy_points_heatmaps = copy.deepcopy(all_tracked_individuals_heatmaps)

        for each_bee in list_bees:
            bee_id = each_bee.bee_id
            bee = bee_id_dict[bee_id]
            for yx_coord in bee.cells_visited:
                y, x = yx_coord
                all_tracked_individuals_heatmaps[bee.tag_id] += 1
                all_tracked_individuals_heatmaps['All'] += 1
                all_tracked_all_xy_points_heatmaps[bee.tag_id] += bee.cells_visited[yx_coord]
                all_tracked_all_xy_points_heatmaps['All'] += bee.cells_visited[yx_coord]

                if bee.path_length > self.min_time_tracked:
                    min_tracked_individuals_heatmaps[bee.tag_id] += 1
                    min_tracked_individuals_heatmaps['All'] += 1
                    min_tracked_all_xy_points_heatmaps[bee.tag_id] += bee.cells_visited[yx_coord]
                    min_tracked_all_xy_points_heatmaps['All'] += bee.cells_visited[yx_coord]

        spread_heatmap_dicts  = [{},{},{},{}]
        for i, heatmap_tag_dict in enumerate([all_tracked_individuals_heatmaps, all_tracked_all_xy_points_heatmaps, min_tracked_individuals_heatmaps, min_tracked_all_xy_points_heatmaps]):
            for tag_group in heatmap_tag_dict:
                norm_heatmap = heatmap_tag_dict[tag_group] / heatmap_tag_dict[tag_group].sum()
                centre = ndimage.measurements.center_of_mass(norm_heatmap)
                spread = 0
                for y_c in range(0, norm_heatmap.shape[0]):
                    for x_c in range(0, norm_heatmap.shape[1]):
                        spread += Experiment.calc_distance(x_c, y_c, centre[1], centre[0]) * norm_heatmap[y_c, x_c]

                spread_heatmap_dicts[i][tag_group] = spread

        return spread_heatmap_dicts

    def generate_speeds(self, list_bees, bee_id_dict, plot_title):
        all_tracked_speeds = {0: [],
                                1: [],
                                2: [],
                                3: [],
                                'All': []}
        min_tracked_speeds = copy.deepcopy(all_tracked_speeds)

        for each_bee in list_bees:
            bee_id = each_bee.bee_id
            bee = bee_id_dict[bee_id]
            all_tracked_speeds[bee.tag_id].extend(bee.list_speeds)
            all_tracked_speeds['All'].extend(bee.list_speeds)

            if bee.path_length > self.min_time_tracked:
                min_tracked_speeds[bee.tag_id].extend(bee.list_speeds)
                min_tracked_speeds['All'].extend(bee.list_speeds)

        mean_all_tracked_speeds, mean_min_tracked_speeds, median_all_tracked_speeds, median_min_tracked_speeds = ({}, {}, {}, {})
        for tag_id in all_tracked_speeds:
            mean_all_tracked_speeds[tag_id] = np.mean(all_tracked_speeds[tag_id])
            mean_min_tracked_speeds[tag_id] = np.mean(min_tracked_speeds[tag_id])
            median_all_tracked_speeds[tag_id] = np.median(all_tracked_speeds[tag_id])
            median_min_tracked_speeds[tag_id] = np.median(min_tracked_speeds[tag_id])

        return [mean_all_tracked_speeds, mean_min_tracked_speeds, median_all_tracked_speeds, median_min_tracked_speeds]

    def generate_angles(self, list_bees, bee_id_dict, plot_title):
        all_tracked_angles = {0: np.zeros(360 / 20),
                                1: np.zeros(360 / 20),
                                2: np.zeros(360 / 20),
                                3: np.zeros(360 / 20),
                                'All': np.zeros(360 / 20)}
        min_tracked_angles = copy.deepcopy(all_tracked_speeds)

        for each_bee in list_bees:
            bee_id = each_bee.bee_id
            bee = bee_id_dict[bee_id]
            if len(bee.list_angles) > 0:
                angles_hist = Graphics.create_angles_hist(bee.list_angles)
                all_tracked_angles[bee.tag_id] += angles_hist
                all_tracked_angles['All'] += angles_hist
                if bee.path_length > self.min_time_tracked:
                    min_tracked_angles[bee.tag_id] += angles_hist
                    min_tracked_angles['All'] += angles_hist

        return None

    def log_output(self, day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy,
                    night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy,
                    day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds,
                    night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds,
                    day_num, result_type):

        for tag_type in day_spread_all_tracked_individuals:

            self.output['spread_all_tracked_individuals'].extend([night_spread_all_tracked_individuals[tag_type], day_spread_all_tracked_individuals[tag_type]])
            self.output['spread_all_tracked_all_xy'].extend([night_spread_all_tracked_all_xy[tag_type], day_spread_all_tracked_all_xy[tag_type]])
            self.output['spread_min_tracked_individuals'].extend([night_spread_min_tracked_individuals[tag_type], day_spread_min_tracked_individuals[tag_type]])
            self.output['spread_min_tracked_all_xy'].extend([night_spread_min_tracked_all_xy[tag_type], day_spread_min_tracked_all_xy[tag_type]])

            self.output['diff_spread_all_tracked_individuals'].extend([abs(day_spread_all_tracked_individuals[tag_type] - night_spread_all_tracked_individuals[tag_type]), np.nan])
            self.output['diff_spread_all_tracked_all_xy'].extend([abs(day_spread_all_tracked_all_xy[tag_type] - night_spread_all_tracked_all_xy[tag_type]), np.nan])
            self.output['diff_spread_min_tracked_individuals'].extend([abs(day_spread_min_tracked_individuals[tag_type] - night_spread_min_tracked_individuals[tag_type]), np.nan])
            self.output['diff_spread_min_tracked_all_xy'].extend([abs(day_spread_min_tracked_all_xy[tag_type] - night_spread_min_tracked_all_xy[tag_type]), np.nan])

            self.output['mean_all_tracked_speeds'].extend([night_mean_all_tracked_speeds[tag_type], day_mean_all_tracked_speeds[tag_type]])
            self.output['mean_min_tracked_speeds'].extend([night_mean_min_tracked_speeds[tag_type], day_mean_min_tracked_speeds[tag_type]])
            self.output['median_all_tracked_speeds'].extend([night_median_all_tracked_speeds[tag_type], day_median_all_tracked_speeds[tag_type]])
            self.output['median_min_tracked_speeds'].extend([night_median_min_tracked_speeds[tag_type], day_median_min_tracked_speeds[tag_type]])

            self.output['diff_mean_all_tracked_speeds'].extend([abs(day_mean_all_tracked_speeds[tag_type] - night_mean_all_tracked_speeds[tag_type]), np.nan])
            self.output['diff_mean_min_tracked_speeds'].extend([abs(day_mean_min_tracked_speeds[tag_type] - night_mean_min_tracked_speeds[tag_type]), np.nan])
            self.output['diff_median_all_tracked_speeds'].extend([abs(day_median_all_tracked_speeds[tag_type] - night_median_all_tracked_speeds[tag_type]), np.nan])
            self.output['diff_median_min_tracked_speeds'].extend([abs(day_median_min_tracked_speeds[tag_type] - night_median_min_tracked_speeds[tag_type]), np.nan])

            self.output['day_num'].extend([day_num, day_num])
            self.output['time_period'].extend(['night', 'day'])
            self.output['result_type'].extend([result_type, result_type])
            self.output['tag_type'].extend([tag_type, tag_type])

        return None

def main():
    pass

if __name__ == "__main__":
    main()
