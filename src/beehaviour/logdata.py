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
                        'day_num': [],
                        'time_period': [],
                        'result_type': [],
                        'tag_type': []}

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
