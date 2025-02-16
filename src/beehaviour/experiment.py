#!/usr/bin/env python

import datetime
import random
import numpy as np
import math
import copy
from scipy import ndimage
import networkx as nx
import statsmodels.api as sm

from .db import DB
from .graphics import Graphics
from .bee import Bee
from .logdata import LogData

class Experiment:
    def __init__(self, hive_id):
        self.hive_id = hive_id
        self.output_dir = '../results/'

        self.num_x_cells = 40
        self.num_y_cells = 20
        self.x_bins = 3840/self.num_x_cells
        self.y_bins = 2160/self.num_y_cells
        self.frames_per_window = 25
        self.min_angle_speed = 30
        self.tag_confidence_percentage = 0.8
        self.min_tracked_for_classification = 100
        self.min_time_tracked = 25 * 5

        self.plotnum = 0

        self.logger = LogData()

        hour_blocks_in_experiment = self.retrieve_hour_blocks_in_experiment(hive_id)
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

        return (day_hours, night_hours)

    def retrieve_bees_in_time_period(self, time_period_list_datetimes):
        group_bees = []
        db = DB()
        #print(time_period_list_datetimes)
        for each_group_hours in time_period_list_datetimes:
            #print(each_group_hours, '\n')
            bees_in_time_group = []
            query_statement = db.query_string(table='bees', cols=['BeeID', 'TagID', 'TagConfidence', 'LengthTracked'], group_condition='HourBin IN', group_list=[str(time) for time in each_group_hours])
            #print(query_statement)
            hours_query_result = db.query(query_statement)
            for bee_row in hours_query_result:#[:100]: ##### change
                if bee_row['TagConfidence'] > self.tag_confidence_percentage:
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
        bee_id_dict, day_downsampled_bee_locations, night_downsampled_bee_locations = self.retrieve_process_bees(day_bees, night_bees)

        day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy = self.generate_heatmaps(day_bees, bee_id_dict, 'day_{}'.format(day_num))
        night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy = self.generate_heatmaps(night_bees, bee_id_dict, 'night_{}'.format(day_num))

        #print(day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy, '\n')

        day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds = self.generate_speeds(day_bees, bee_id_dict, 'day_{}'.format(day_num))
        night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds = self.generate_speeds(night_bees, bee_id_dict, 'night_{}'.format(day_num))

        day_percent_idle_all_tracked, day_percent_idle_min_tracked = self.idle_percentage(day_bees, bee_id_dict, 'day_{}'.format(day_num))
        night_percent_idle_all_tracked, night_percent_idle_min_tracked = self.idle_percentage(night_bees, bee_id_dict, 'night_{}'.format(day_num))

        day_list_node_degree, day_list_density, day_list_clustering = self.identify_relationships(day_downsampled_bee_locations, 'day_{}'.format(day_num))
        night_list_node_degree, night_list_density, night_list_clustering = self.identify_relationships(night_downsampled_bee_locations, 'night_{}'.format(day_num))

        #self.generate_angles(day_beeids, bee_id_dict, 'day_{}'.format(day_num))
        #self.generate_angles(night_beeids, bee_id_dict, 'night_{}'.format(day_num))

        self.logger.log_output(day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy,
                        night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy,
                        day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds,
                        night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds,
                        day_list_node_degree, day_list_density, day_list_clustering, night_list_node_degree, night_list_density, night_list_clustering,
                        day_percent_idle_all_tracked, day_percent_idle_min_tracked, night_percent_idle_all_tracked, night_percent_idle_min_tracked,
                        day_num, 'real')

        #test_circadian: True=shuffles day and night; False=shuffles tag types
        self.permutation_tests(day_bees, night_bees, day_downsampled_bee_locations, night_downsampled_bee_locations, bee_id_dict, day_num, 100, test_circadian=False)

    def permutation_tests(self, day_bees, night_bees, day_downsampled_bee_locations, night_downsampled_bee_locations, bee_id_d, day_num, num_iterations, test_circadian):
        combined_day_night_bees = day_bees + night_bees
        combined_locations_day_night_bees = day_downsampled_bee_locations + night_downsampled_bee_locations

        day_bees_grouped_by_tag = {0:[], 1:[], 2:[], 3:[]}
        night_bees_grouped_by_tag = {0:[], 1:[], 2:[], 3:[]}
        for each_bee in day_bees:
            bee_id = each_bee.bee_id
            bee_id = each_bee.bee_id
            bee = bee_id_d[bee_id]
            day_bees_grouped_by_tag[bee.tag_id].append(bee)
        for each_bee in night_bees:
            bee_id = each_bee.bee_id
            bee_id = each_bee.bee_id
            bee = bee_id_d[bee_id]
            night_bees_grouped_by_tag[bee.tag_id].append(bee)

        for i in range(num_iterations):
            bee_id_dict = copy.deepcopy(bee_id_d)

            if test_circadian:
                random.shuffle(combined_day_night_bees)
                shuffled_day_bees = combined_day_night_bees[:len(day_bees)]
                shuffled_night_bees = combined_day_night_bees[len(day_bees):]

                random.shuffle(combined_locations_day_night_bees)
                shuffled_day_locations_bees = combined_locations_day_night_bees[:len(day_downsampled_bee_locations)]
                shuffled_night_locations_bees = combined_locations_day_night_bees[len(day_downsampled_bee_locations):]

            else:
                random.shuffle(day_bees)
                random.shuffle(night_bees)
                shuffled_day_bees = day_bees
                shuffled_night_bees = night_bees

                shuffled_day_locations_bees = day_downsampled_bee_locations
                shuffled_night_locations_bees = night_downsampled_bee_locations

                num_bees_iterated = 0
                for tag_type in day_bees_grouped_by_tag:
                    for each_bee in day_bees[num_bees_iterated:len(day_bees_grouped_by_tag[tag_type])]:
                        bee_id = each_bee.bee_id
                        bee_id = each_bee.bee_id
                        bee = bee_id_dict[bee_id]
                        bee.tag_id = tag_type
                    num_bees_iterated += len(day_bees_grouped_by_tag[tag_type])

                num_bees_iterated = 0
                for tag_type in night_bees_grouped_by_tag:
                    for each_bee in night_bees[num_bees_iterated:len(night_bees_grouped_by_tag[tag_type])]:
                        bee_id = each_bee.bee_id
                        bee_id = each_bee.bee_id
                        bee = bee_id_dict[bee_id]
                        bee.tag_id = tag_type
                    num_bees_iterated += len(night_bees_grouped_by_tag[tag_type])

            day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy = self.generate_heatmaps(shuffled_day_bees, bee_id_dict, 'shuffled_spread_day_{}_{}'.format(day_num, i))
            night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy = self.generate_heatmaps(shuffled_night_bees, bee_id_dict, 'shuffled_spread_night_{}_{}'.format(day_num, i))
            day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds = self.generate_speeds(shuffled_day_bees, bee_id_dict, 'shuffled_speed_day_{}_{}'.format(day_num, i))
            night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds = self.generate_speeds(shuffled_night_bees, bee_id_dict, 'shuffled_speed_night_{}_{}'.format(day_num, i))

            day_percent_idle_all_tracked, day_percent_idle_min_tracked = self.idle_percentage(shuffled_day_bees, bee_id_dict, 'shuffled_percent_idle_day_{}_{}'.format(day_num, i))
            night_percent_idle_all_tracked, night_percent_idle_min_tracked = self.idle_percentage(shuffled_night_bees, bee_id_dict, 'shuffled_percent_idle_night_{}_{}'.format(day_num, i))

            day_list_node_degree, day_list_density, day_list_clustering = self.identify_relationships(shuffled_day_locations_bees, 'shuffled_network_day_{}_{}'.format(day_num, i))
            night_list_node_degree, night_list_density, night_list_clustering = self.identify_relationships(shuffled_night_locations_bees, 'shuffled_network_night_{}_{}'.format(day_num, i))

            self.logger.log_output(day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy,
                            night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy,
                            day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds,
                            night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds,
                            day_list_node_degree, day_list_density, day_list_clustering, night_list_node_degree, night_list_density, night_list_clustering,
                            day_percent_idle_all_tracked, day_percent_idle_min_tracked, night_percent_idle_all_tracked, night_percent_idle_min_tracked,
                            day_num, 'shuffled')

            if test_circadian:
                bootstrapped_day_bees = np.random.choice(day_bees, len(day_bees), replace=True)
                bootstrapped_night_bees = np.random.choice(night_bees, len(night_bees), replace=True)

                bootstrapped_day_locations_bees = np.random.choice(day_downsampled_bee_locations, len(day_downsampled_bee_locations), replace=True)
                bootstrapped_night_locations_bees = np.random.choice(night_downsampled_bee_locations, len(night_downsampled_bee_locations), replace=True)

            else:
                bootstrapped_day_bees = []
                bootstrapped_night_bees = []

                bootstrapped_day_locations_bees = day_downsampled_bee_locations
                bootstrapped_night_locations_bees = night_downsampled_bee_locations

                for tag_type in day_bees_grouped_by_tag:
                    bootstrapped_tags = np.random.choice(day_bees_grouped_by_tag[tag_type], len(day_bees_grouped_by_tag[tag_type]), replace=True)
                    bootstrapped_day_bees.extend(bootstrapped_tags)

                for tag_type in night_bees_grouped_by_tag:
                    bootstrapped_tags = np.random.choice(day_bees_grouped_by_tag[tag_type], len(day_bees_grouped_by_tag[tag_type]), replace=True)
                    bootstrapped_night_bees.extend(bootstrapped_tags)

            day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy = self.generate_heatmaps(bootstrapped_day_bees, bee_id_dict, 'bootstrapped_spread_day_{}_{}'.format(day_num, i))
            night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy = self.generate_heatmaps(bootstrapped_night_bees, bee_id_dict, 'bootstrapped_spread_night_{}_{}'.format(day_num, i))

            day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds = self.generate_speeds(bootstrapped_day_bees, bee_id_dict, 'bootstrapped_speed_day_{}_{}'.format(day_num, i))
            night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds = self.generate_speeds(bootstrapped_night_bees, bee_id_dict, 'bootstrapped_speed_night_{}_{}'.format(day_num, i))

            day_percent_idle_all_tracked, day_percent_idle_min_tracked = self.idle_percentage(bootstrapped_day_bees, bee_id_dict, 'bootstrapped_percent_idle_day_{}_{}'.format(day_num, i))
            night_percent_idle_all_tracked, night_percent_idle_min_tracked = self.idle_percentage(bootstrapped_night_bees, bee_id_dict, 'bootstrapped_percent_idle_night_{}_{}'.format(day_num, i))

            day_list_node_degree, day_list_density, day_list_clustering = self.identify_relationships(bootstrapped_day_locations_bees, 'bootstrapped_network_day_{}_{}'.format(day_num, i))
            night_list_node_degree, night_list_density, night_list_clustering = self.identify_relationships(bootstrapped_night_locations_bees, 'bootstrapped_network_night_{}_{}'.format(day_num, i))

            self.logger.log_output(day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy,
                            night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy,
                            day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds,
                            night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds,
                            day_list_node_degree, day_list_density, day_list_clustering, night_list_node_degree, night_list_density, night_list_clustering,
                            day_percent_idle_all_tracked, day_percent_idle_min_tracked, night_percent_idle_all_tracked, night_percent_idle_min_tracked,
                            day_num, 'bootstrapped')

    def retrieve_process_bees(self, day_bees, night_bees):
        day_bee_ids = [bee.bee_id for bee in day_bees]
        night_bee_ids = [bee.bee_id for bee in night_bees]

        bee_id_dict = {bee.bee_id: bee for bee in (day_bees + night_bees) }
        #list_bee_ids = list(bee_id_dict.keys())

        def day_night_db_retrieve_analyse(list_bee_ids):
            time_period_locations_by_frame = {}
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
                    # for finding close interactions
                    #bee_id_dict[bee_id].frame_xy[row['Frame']] = (row['X'], row['Y'])

                    if row['Frame'] in time_period_locations_by_frame.keys():
                        time_period_locations_by_frame[row['Frame']].append((row['X'], row['Y']))
                    else:
                        time_period_locations_by_frame[row['Frame']] = [(row['X'], row['Y'])]

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
                            bee_id_dict[bee_id].seconds_tracked += 1
                            if current_speed >= self.min_angle_speed:
                                angle = Experiment.absolute_angle_degree(row['X'], row['Y'], bee_id_dict[bee_id].last_x, bee_id_dict[bee_id].last_y)
                                bee_id_dict[bee_id].list_angles.append(angle)
                            else:
                                bee_id_dict[bee_id].seconds_idle += 1

                            bee_id_dict[bee_id].path_length = 1
                            bee_id_dict[bee_id].last_x = row['X']
                            bee_id_dict[bee_id].last_y = row['Y']


                    else:
                        bee_id_dict[bee_id].last_path_id = row['PathID']
                        bee_id_dict[bee_id].path_length = 1
                        bee_id_dict[bee_id].last_x = row['X']
                        bee_id_dict[bee_id].last_y = row['Y']

            db.close()

            downsampled_bee_locations = []
            frames_list = list(time_period_locations_by_frame.keys())
            frames_list.sort()
            for i, frame in enumerate(frames_list):
                if i % 1000 == 0:
                    downsampled_bee_locations.append(time_period_locations_by_frame[frame])

            return downsampled_bee_locations

        day_downsampled_bee_locations = day_night_db_retrieve_analyse(day_bee_ids)
        night_downsampled_bee_locations = day_night_db_retrieve_analyse(night_bee_ids)

        return (bee_id_dict, day_downsampled_bee_locations, night_downsampled_bee_locations)

    def identify_relationships(self, downsampled_bee_locations, plot_title):
        list_avg_node_degree, list_density, list_avg_clustering = ([],[],[])
        for bees_in_frame in downsampled_bee_locations:
            bee_xy_list_nearby_bee_xy = {}
            for bee_xy in bees_in_frame:
                bee_xy_list_nearby_bee_xy[bee_xy] = []
                for other_bees_xy in bees_in_frame:
                    if bee_xy != other_bees_xy and Experiment.calc_distance(bee_xy[0], bee_xy[1], other_bees_xy[0], other_bees_xy[1]) < 200:
                        bee_xy_list_nearby_bee_xy[bee_xy].append(other_bees_xy)

            all_relations, direct_relations = self.group_bees_by_relationship(bee_xy_list_nearby_bee_xy)
            G=nx.Graph()
            for rel_group in direct_relations:
                G.add_nodes_from(rel_group)
                for bee_xy in rel_group:
                    for other_bees_xy in rel_group:
                        if bee_xy != other_bees_xy:
                            G.add_edge(bee_xy, other_bees_xy)

            degree_list = list(G.degree().values())
            avg_node_degree = sum(degree_list)/len(G.degree())
            density = nx.density(G)
            avg_clustering = nx.average_clustering(G)

            list_avg_node_degree.append(avg_node_degree)
            list_density.append(density)
            list_avg_clustering.append(avg_clustering)

        return (list_avg_node_degree, list_density, list_avg_clustering)


    def group_bees_by_relationship(self, bee_xy_list_nearby_bee_xy):
        all_relationships_in_frame = []
        direct_relationships_in_frame = []
        for bee_xy in bee_xy_list_nearby_bee_xy.keys():
            all_relationships  = [bee_xy]
            direct_relationships = set()
            for other_bees_xy in bee_xy_list_nearby_bee_xy.keys():
                if bee_xy != other_bees_xy:
                    s1 = set([bee_xy]+bee_xy_list_nearby_bee_xy[bee_xy])
                    s2 = set([other_bees_xy]+bee_xy_list_nearby_bee_xy[other_bees_xy])
                    intersect_sets = s1.intersection(s2)
                    if len(intersect_sets) > 0:
                        all_relationships.append(other_bees_xy)
                    direct_relationships = direct_relationships.union(intersect_sets)

            bee_xy_not_present_in_all_relationships_in_frame = True
            bee_xy_not_present_in_direct_relationships_in_frame = True
            for rel_group in all_relationships_in_frame:
                if bee_xy in rel_group:
                    bee_xy_not_present_in_all_relationships_in_frame = False
            for rel_group in direct_relationships_in_frame:
                if bee_xy in rel_group:
                    bee_xy_not_present_in_direct_relationships_in_frame = False

            if bee_xy_not_present_in_all_relationships_in_frame:
                all_relationships_in_frame.append(all_relationships)
            if bee_xy_not_present_in_direct_relationships_in_frame:
                if len(direct_relationships) == 0:
                    direct_relationships = direct_relationships.union(set([bee_xy]))
                direct_relationships_in_frame.append(list(direct_relationships))

        return(all_relationships_in_frame, direct_relationships_in_frame)

    def generate_heatmaps(self, list_bees, bee_id_dict, plot_title):
        all_tracked_individuals_heatmaps = {0: np.zeros((self.num_y_cells, self.num_x_cells)),
                                            1: np.zeros((self.num_y_cells, self.num_x_cells)),
                                            2: np.zeros((self.num_y_cells, self.num_x_cells)),
                                            3: np.zeros((self.num_y_cells, self.num_x_cells)),
                                            'All': np.zeros((self.num_y_cells, self.num_x_cells))}
        all_tracked_all_xy_points_heatmaps = copy.deepcopy(all_tracked_individuals_heatmaps)
        min_tracked_individuals_heatmaps = copy.deepcopy(all_tracked_individuals_heatmaps)
        min_tracked_all_xy_points_heatmaps = copy.deepcopy(all_tracked_individuals_heatmaps)

        #print([bee.bee_id for bee in list_bees], '\n')

        for each_bee in list_bees:
            bee_id = each_bee.bee_id
            bee = bee_id_dict[bee_id]
            for yx_coord in bee.cells_visited:
                y, x = yx_coord
                all_tracked_individuals_heatmaps[bee.tag_id][yx_coord] += 1
                all_tracked_individuals_heatmaps['All'][yx_coord] += 1
                all_tracked_all_xy_points_heatmaps[bee.tag_id][yx_coord] += bee.cells_visited[yx_coord]
                all_tracked_all_xy_points_heatmaps['All'][yx_coord] += bee.cells_visited[yx_coord]

                if bee.length_tracked > self.min_time_tracked:
                    #print('if', bee.length_tracked)
                    min_tracked_individuals_heatmaps[bee.tag_id][yx_coord] += 1
                    min_tracked_individuals_heatmaps['All'][yx_coord] += 1
                    min_tracked_all_xy_points_heatmaps[bee.tag_id][yx_coord] += bee.cells_visited[yx_coord]
                    min_tracked_all_xy_points_heatmaps['All'][yx_coord] += bee.cells_visited[yx_coord]

        heatmap_dictionaries_list = [all_tracked_individuals_heatmaps, all_tracked_all_xy_points_heatmaps, min_tracked_individuals_heatmaps, min_tracked_all_xy_points_heatmaps]

        spread_heatmap_dicts  = [{},{},{},{}]

        for tag_group in heatmap_dictionaries_list[0]:
            for i, hm_dictionary in enumerate(heatmap_dictionaries_list):
                norm_heatmap = heatmap_dictionaries_list[i][tag_group] / heatmap_dictionaries_list[i][tag_group].sum()
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

            if bee.length_tracked > self.min_time_tracked:
                min_tracked_speeds[bee.tag_id].extend(bee.list_speeds)
                min_tracked_speeds['All'].extend(bee.list_speeds)

        mean_all_tracked_speeds, mean_min_tracked_speeds, median_all_tracked_speeds, median_min_tracked_speeds = ({}, {}, {}, {})
        for tag_id in all_tracked_speeds:
            mean_all_tracked_speeds[tag_id] = np.mean(all_tracked_speeds[tag_id])
            mean_min_tracked_speeds[tag_id] = np.mean(min_tracked_speeds[tag_id])
            median_all_tracked_speeds[tag_id] = np.median(all_tracked_speeds[tag_id])
            median_min_tracked_speeds[tag_id] = np.median(min_tracked_speeds[tag_id])

        return [mean_all_tracked_speeds, mean_min_tracked_speeds, median_all_tracked_speeds, median_min_tracked_speeds]

    def idle_percentage(self, list_bees, bee_id_dict, plot_title):
        # list, first element is incrementing time idle, second is incremented total time track
        all_tracked_idle_total = {0: [0,0],
                                1: [0,0],
                                2: [0,0],
                                3: [0,0],
                                'All': [0,0]}
        min_tracked_idle_total = copy.deepcopy(all_tracked_idle_total)

        for each_bee in list_bees:
            bee_id = each_bee.bee_id
            bee = bee_id_dict[bee_id]
            all_tracked_idle_total[bee.tag_id][0] += (bee.seconds_idle)
            all_tracked_idle_total[bee.tag_id][1] += (bee.seconds_tracked)
            all_tracked_idle_total['All'][0] += (bee.seconds_idle)
            all_tracked_idle_total['All'][1] += (bee.seconds_tracked)

            if bee.length_tracked > self.min_time_tracked:
                min_tracked_idle_total[bee.tag_id][0] += (bee.seconds_idle)
                min_tracked_idle_total[bee.tag_id][1] += (bee.seconds_tracked)
                min_tracked_idle_total['All'][0] += (bee.seconds_idle)
                min_tracked_idle_total['All'][1] += (bee.seconds_tracked)

        percent_idle_all_tracked, percent_idle_min_tracked = ({}, {})
        for tag_id in all_tracked_idle_total:
            if all_tracked_idle_total[tag_id][1] != 0:
                percent_idle_all_tracked[tag_id] = all_tracked_idle_total[tag_id][0] / all_tracked_idle_total[tag_id][1]
            else:
                percent_idle_all_tracked[tag_id] = 0
            if min_tracked_idle_total[tag_id][1] != 0:
                percent_idle_min_tracked[tag_id] = min_tracked_idle_total[tag_id][0] / min_tracked_idle_total[tag_id][1]
            else:
                percent_idle_min_tracked[tag_id] = 0

        return [percent_idle_all_tracked, percent_idle_min_tracked]

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

def main():
    pass

if __name__ == "__main__":
    main()
