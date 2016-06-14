#!/usr/bin/env python

import datetime
import random
import numpy as np
import math
from scipy import ndimage
from multiprocessing import Pool

from .database import query_db
from .graphics import Graphics
from .bee import Bee

class Experiment:
    def __init__(self, hive_id):
        self.hive_id = hive_id
        self.num_x_cells = 40
        self.num_y_cells = 20
        self.x_bins = 3840/self.num_x_cells
        self.y_bins = 2160/self.num_y_cells
        self.frames_per_window = 25
        self.min_angle_speed = 10

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

            group_beeids.append(beeids_in_time_group) #[:100]

        return group_beeids

    def merge_day_night_beeids(self, day_grouped_beeids, night_grouped_beeids):
        combined_day_night_bee_ids = []
        for i, time_grouped_ids in enumerate(day_grouped_beeids):
            try:
                group_day_night = day_grouped_beeids[i] + night_grouped_beeids[i]
                combined_day_night_bee_ids.append(group_day_night)
            except Exception:
                break

        return combined_day_night_bee_ids

    def shuffle_day_night_beeids(self, day_night_period_bee_ids, day_grouped_beeids, shuffle_iterations):
        shuffled_day_beeids = []
        shuffled_night_beeids = []
        for i in range(shuffle_iterations):
            random.shuffle(day_night_period_bee_ids)
            shuffled_day_beeids.append(day_night_period_bee_ids[:len(day_grouped_beeids)])
            shuffled_night_beeids.append(day_night_period_bee_ids[len(day_grouped_beeids):])

        return (shuffled_day_beeids, shuffled_night_beeids)

    def retrieve_process_bees(self, list_bee_ids):
        bee_id_dict = {bee_id:Bee(bee_id) for bee_id in list_bee_ids}

        for i in range(0, len(list_bee_ids),100):
            subset_bee_ids = list_bee_ids[i:i+100]
            coord_rows = query_db(table='bee_coords, paths', cols=['paths.BeeID', 'bee_coords.PathID', 'bee_coords.Frame', 'bee_coords.X', 'bee_coords.Y'], where='bee_coords.PathID = paths.PathID', group_condition='AND BeeID IN', group_list=subset_bee_ids, order='ORDER BY Frame ASC')

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
                        if current_speed > self.min_angle_speed:
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

        Graphics.plot_heatmaps(normalised_individual_heatmap, 0.01, plot_title, '/Users/jack/Research/DBee/results/' + plot_title + 'individual.png')
        Graphics.plot_heatmaps(normalised_all_xy_heatmap, 0.01, plot_title, '/Users/jack/Research/DBee/results/' + plot_title + 'xy.png')

        return spread

    def generate_speeds(self, list_bee_ids, bee_id_dict):
        all_speeds = []
        for bee_id in list_bee_ids:
            bee = bee_id_dict[bee_id]
            all_speeds.extend(bee.list_speeds)

        return np.mean(all_speeds)

    def generate_angles(self, list_bee_ids, bee_id_dict):
        all_angles = []
        for bee_id in list_bee_ids:
            bee = bee_id_dict[bee_id]
            all_speeds.extend(bee.list_angles)

        return all_angles

def main():
    pass
    #query_db(table='bees', cols=['HourBin'], where='HiveID=1', group_condition='AND HiveID IN', group_list=[1,2,3])
    #query_db(table='bees', cols=['HourBin'], where='HiveID=1')
    #query_db(table='bees', cols=['HourBin'], group_condition='HiveID IN', group_list=[1,2,3])

    #query_db(table='paths', cols=['*'], where='BeeID IN', subquery='select beeid from bees where beeid=0')

    #query_db(table='paths', cols=['*'], where='BeeID IN', subquery='select beeid from bees where beeid IN', subquery_list=[0,1])

    #SELECT ID, NAME, AGE, AMOUNT
        #FROM CUSTOMERS, ORDERS
        #WHERE  CUSTOMERS.ID = ORDERS.CUSTOMER_ID;

    #select BeeID, paths.PathID, Frame, X, Y from bee_coords, paths WHERE bee_coords.PathID = paths.PathID AND PathID IN (select PathID from paths where BeeID=1);

    #select paths.BeeID, bee_coords.PathID, bee_coords.Frame, bee_coords.X, bee_coords.Y from bee_coords, paths WHERE bee_coords.PathID = paths.PathID AND BeeID IN (0);

    #select * from paths where beeid in (select beeid from bees where beeid=0);

    #select * from paths where beeid in (select beeid from bees where beeid=0);

    #beeid

    #query_db(table, cols, distinct=False, fetchall=True, where='', join_operator='', group_condition='', group_list=[], subquery_where='', subquery_list=[]):

    #coordinate_rows =query_db(table='bee_coords', cols=['PathID', 'Frame', 'X', 'Y'], where='PathID IN', subquery='SELECT PathID FROM paths WHERE BeeID IN', subquery_list=[0,1])

    #print(x)

    #select paths.BeeID, bee_coords.PathID, bee_coords.Frame, bee_coords.X, bee_coords.Y from bee_coords, paths WHERE bee_coords.PathID = paths.PathID AND BeeID IN (0);

    #coord_rows = query_db(table='bee_coords, paths', cols=['paths.BeeID', 'bee_coords.PathID',
                        #'bee_coords.Frame', 'bee_coords.X', 'bee_coords.Y'],
                        #where='bee_coords.PathID = paths.PathID', group_condition='AND BeeID IN', group_list=list_bee_ids, order='ORDER BY Frame ASC')


if __name__ == "__main__":
    main()
