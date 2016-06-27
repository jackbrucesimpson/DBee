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

    def log_output(self, ):
        '''Checks for missing data as it takes dictionary of weather metrics, date and time period (hour is optional) and adds it to output dictionary'''
        self.output['date'].append(date)
        self.output['time_period'].append(time_period)
        self.output['hour'].append(hour)

        for metric in weather_metrics.keys():
            if metric in self.output.keys():
                self.output[metric].append(weather_metrics[metric])
            else:
                self.output[metric] = [np.nan] * (len(self.output['time_period']) - 1)
                self.output[metric].append(weather_metrics[metric])

        metrics_to_update = set(self.output.keys()) - set(weather_metrics.keys())
        for metric in metrics_to_update:
            self.output[metric].extend((len(self.output['date']) - len(self.output[metric])) * [np.nan])

        return None

    def write_output(self, path_filename):
        '''Checks for missing data and then writes output to csv'''
        for column in self.output.keys():
            if len(self.output[column]) < len(self.output['date']):
                self.output[column].extend((len(self.output['date']) - len(self.output[column])) * [np.nan])

        if not path_filename.endswith('csv'):
            path_filename += '.csv'

        output_df = pd.DataFrame(self.output)
        output_df.to_csv(path_filename, index=False)

def main():
    pass

if __name__ == "__main__":
    main()
