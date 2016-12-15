#!/usr/bin/env python3

import numpy as np
import pandas as pd

class LogData:
    '''Handles missing data while logging and writing output'''
    def __init__(self):
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

                        'mean_node_degree': [],
                        'median_node_degree': [],
                        'mean_density': [],
                        'median_density': [],
                        'mean_clustering': [],
                        'median_clustering': [],

                        'diff_mean_node_degree': [],
                        'diff_median_node_degree': [],
                        'diff_mean_density': [],
                        'diff_median_density': [],
                        'diff_mean_clustering': [],
                        'diff_median_clustering': [],

                        'percent_idle_all_tracked': [],
                        'percent_idle_min_tracked': [],

                        'diff_percent_idle_all_tracked': [],
                        'diff_percent_idle_min_tracked': [],

                        'day_num': [],
                        'time_period': [],
                        'result_type': [],
                        'tag_type': []}

    def log_output(self, day_spread_all_tracked_individuals, day_spread_all_tracked_all_xy, day_spread_min_tracked_individuals, day_spread_min_tracked_all_xy,
                    night_spread_all_tracked_individuals, night_spread_all_tracked_all_xy, night_spread_min_tracked_individuals, night_spread_min_tracked_all_xy,
                    day_mean_all_tracked_speeds, day_mean_min_tracked_speeds, day_median_all_tracked_speeds, day_median_min_tracked_speeds,
                    night_mean_all_tracked_speeds, night_mean_min_tracked_speeds, night_median_all_tracked_speeds, night_median_min_tracked_speeds,
                    day_list_node_degree, day_list_density, day_list_clustering, night_list_node_degree, night_list_density, night_list_clustering,
                    day_percent_idle_all_tracked, day_percent_idle_min_tracked, night_percent_idle_all_tracked, night_percent_idle_min_tracked,
                    day_num, result_type):

        for tag_type in day_spread_all_tracked_individuals:

            self.output['spread_all_tracked_individuals'].extend([night_spread_all_tracked_individuals[tag_type], day_spread_all_tracked_individuals[tag_type]])
            self.output['spread_all_tracked_all_xy'].extend([night_spread_all_tracked_all_xy[tag_type], day_spread_all_tracked_all_xy[tag_type]])
            self.output['spread_min_tracked_individuals'].extend([night_spread_min_tracked_individuals[tag_type], day_spread_min_tracked_individuals[tag_type]])
            self.output['spread_min_tracked_all_xy'].extend([night_spread_min_tracked_all_xy[tag_type], day_spread_min_tracked_all_xy[tag_type]])

            self.output['diff_spread_all_tracked_individuals'].extend([day_spread_all_tracked_individuals[tag_type] - night_spread_all_tracked_individuals[tag_type], np.nan])
            self.output['diff_spread_all_tracked_all_xy'].extend([day_spread_all_tracked_all_xy[tag_type] - night_spread_all_tracked_all_xy[tag_type], np.nan])
            self.output['diff_spread_min_tracked_individuals'].extend([day_spread_min_tracked_individuals[tag_type] - night_spread_min_tracked_individuals[tag_type], np.nan])
            self.output['diff_spread_min_tracked_all_xy'].extend([day_spread_min_tracked_all_xy[tag_type] - night_spread_min_tracked_all_xy[tag_type], np.nan])

            self.output['mean_all_tracked_speeds'].extend([night_mean_all_tracked_speeds[tag_type], day_mean_all_tracked_speeds[tag_type]])
            self.output['mean_min_tracked_speeds'].extend([night_mean_min_tracked_speeds[tag_type], day_mean_min_tracked_speeds[tag_type]])
            self.output['median_all_tracked_speeds'].extend([night_median_all_tracked_speeds[tag_type], day_median_all_tracked_speeds[tag_type]])
            self.output['median_min_tracked_speeds'].extend([night_median_min_tracked_speeds[tag_type], day_median_min_tracked_speeds[tag_type]])

            self.output['diff_mean_all_tracked_speeds'].extend([day_mean_all_tracked_speeds[tag_type] - night_mean_all_tracked_speeds[tag_type], np.nan])
            self.output['diff_mean_min_tracked_speeds'].extend([day_mean_min_tracked_speeds[tag_type] - night_mean_min_tracked_speeds[tag_type], np.nan])
            self.output['diff_median_all_tracked_speeds'].extend([day_median_all_tracked_speeds[tag_type] - night_median_all_tracked_speeds[tag_type], np.nan])
            self.output['diff_median_min_tracked_speeds'].extend([day_median_min_tracked_speeds[tag_type] - night_median_min_tracked_speeds[tag_type], np.nan])

            self.output['mean_node_degree'].extend([np.mean(day_list_node_degree), np.mean(night_list_node_degree)])
            self.output['median_node_degree'].extend([np.median(day_list_node_degree), np.median(night_list_node_degree)])
            self.output['mean_density'].extend([np.mean(day_list_density), np.mean(night_list_density)])
            self.output['median_density'].extend([np.median(day_list_density), np.median(night_list_density)])
            self.output['mean_clustering'].extend([np.mean(day_list_clustering), np.mean(night_list_clustering)])
            self.output['median_clustering'].extend([np.median(day_list_clustering), np.median(night_list_clustering)])

            self.output['diff_mean_node_degree'].extend([np.mean(day_list_node_degree) - np.mean(night_list_node_degree), np.nan])
            self.output['diff_median_node_degree'].extend([np.median(day_list_node_degree) - np.median(night_list_node_degree), np.nan])
            self.output['diff_mean_density'].extend([np.mean(day_list_density) - np.mean(night_list_density), np.nan])
            self.output['diff_median_density'].extend([np.median(day_list_density) - np.median(night_list_density), np.nan])
            self.output['diff_mean_clustering'].extend([np.mean(day_list_clustering) - np.mean(night_list_clustering), np.nan])
            self.output['diff_median_clustering'].extend([np.median(day_list_clustering) - np.median(night_list_clustering), np.nan])

            self.output['percent_idle_all_tracked'].extend([night_percent_idle_all_tracked[tag_type], day_percent_idle_all_tracked[tag_type]])
            self.output['percent_idle_min_tracked'].extend([night_percent_idle_min_tracked[tag_type], day_percent_idle_min_tracked[tag_type]])

            self.output['diff_percent_idle_all_tracked'].extend([day_percent_idle_all_tracked[tag_type] - night_percent_idle_all_tracked[tag_type], np.nan])
            self.output['diff_percent_idle_min_tracked'].extend([day_percent_idle_min_tracked[tag_type] - night_percent_idle_min_tracked[tag_type], np.nan])

            self.output['day_num'].extend([day_num, day_num])
            self.output['time_period'].extend(['night', 'day'])
            self.output['result_type'].extend([result_type, result_type])
            self.output['tag_type'].extend([tag_type, tag_type])

        return None

def main():
    pass

if __name__ == "__main__":
    main()
