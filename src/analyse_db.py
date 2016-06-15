#!/usr/bin/env python

import sys
import datetime
import random
random.seed(1)
import pandas as pd

from beehaviour.experiment import Experiment

def parse_experiment_numbers(experiment_numbers_str):
    experiment_numbers_list_str = experiment_numbers_str.split(',')
    experiment_numbers = [int(number) for number in experiment_numbers_list_str]
    return experiment_numbers

def main():
    all_hive_ids = parse_experiment_numbers(sys.argv[1])

    experiments_object_list = []
    for hive_id in all_hive_ids:
        experiment = Experiment(hive_id)
        hour_blocks_in_experiment = experiment.retrieve_hour_blocks_in_experiment(hive_id)
        day_hour_bins, night_hour_bins = experiment.group_hours_by_night_day(hour_blocks_in_experiment)

        day_grouped_beeids = experiment.retrieve_beeids_in_time_period(day_hour_bins)
        night_grouped_beeids = experiment.retrieve_beeids_in_time_period(night_hour_bins)

        combined_day_night_bee_ids = experiment.merge_day_night_beeids(day_grouped_beeids, night_grouped_beeids)

        output = {'spread':[], 'speed':[], 'is_day':[], 'day_num':[], 'is_real_result':[]}
        for i, day_night_period_bee_ids in enumerate(combined_day_night_bee_ids):
            print('Period', i)

            bee_id_dict = experiment.retrieve_process_bees(combined_day_night_bee_ids[i])
            shuffled_day_beeids, shuffled_night_beeids = experiment.shuffle_day_night_beeids(combined_day_night_bee_ids[i], day_grouped_beeids[i], 100)

            day_spread = experiment.generate_heatmaps(day_grouped_beeids[i], bee_id_dict, 'day_{}_'.format(i))
            night_spread = experiment.generate_heatmaps(night_grouped_beeids[i], bee_id_dict, 'night_{}_'.format(i))
            day_speed = experiment.generate_speeds(day_grouped_beeids[i], bee_id_dict)
            night_speed = experiment.generate_speeds(night_grouped_beeids[i], bee_id_dict)

            print(day_spread, night_spread, day_speed, night_speed)
            output['spread'].extend([day_spread, night_spread])
            output['speed'].extend([day_speed, night_speed])
            output['is_day'].extend([1, 0])
            output['day_num'].extend([i, i])
            output['is_real_result'].extend([1, 1])

            for j, shuffled_day in enumerate(shuffled_day_beeids):
                shuffled_day_spread = experiment.generate_heatmaps(shuffled_day_beeids[j], bee_id_dict, 'shuffled_day_{}_{}_'.format(i, j))
                shuffled_night_spread = experiment.generate_heatmaps(shuffled_night_beeids[j], bee_id_dict, 'shuffled_night_{}_{}_'.format(i, j))
                shuffled_day_speed = experiment.generate_speeds(shuffled_day_beeids[j], bee_id_dict)
                shuffled_night_speed = experiment.generate_speeds(shuffled_night_beeids[j], bee_id_dict)

                output['spread'].extend([shuffled_day_spread, shuffled_night_spread])
                output['speed'].extend([shuffled_day_speed, shuffled_night_speed])
                output['is_day'].extend([1, 0])
                output['day_num'].extend([i, i])
                output['is_real_result'].extend([0, 0])

        output_df = pd.DataFrame(output)
        output_df.to_csv('/Users/jack/Research/DBee/results/{}_output.csv'.format(hive_id))

if __name__ == "__main__":
    main()
