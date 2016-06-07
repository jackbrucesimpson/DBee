#!/usr/bin/env python

import sys
import datetime
import random

from beehaviour.experiment import Experiment
from beehaviour.db_utils import parse_experiment_numbers
from beehaviour.metrics import Metrics

from beehaviour.database import insert_db

def main():

    all_hive_ids = parse_experiment_numbers(sys.argv[1])

    experiments_object_list = []
    for hive_id in all_hive_ids:
        experiment = Experiment(hive_id)
        hour_blocks_in_experiment = experiment.retrieve_hour_blocks_in_experiment(hive_id)
        day_hour_bins, night_hour_bins = experiment.group_hours_by_night_day(hour_blocks_in_experiment)

        day_grouped_beeids = experiment.retrieve_beeids_in_time_period(day_hour_bins)
        night_grouped_beeids = experiment.retrieve_beeids_in_time_period(night_hour_bins)

        shuffled_day_beeids_seed_dict, shuffled_night_beeids_seed_dict = experiment.merge_shuffle_day_night_beeids(day_grouped_beeids, night_grouped_beeids, 100)

        print(shuffled_day_beeids_seed_dict.keys())

        

    '''
    day_experiments_beeids = {}
    night_experiments_beeids = {}
    for experiment_num in all_hive_ids:
        hour_blocks_in_experiment = retrieve_hour_blocks_in_experiment(experiment_num)
        day_hour_bins, night_hour_bins = group_hours_by_night_day(hour_blocks_in_experiment)

        day_experiments_beeids[experiment_num] = retrieve_beeids_in_time_period(day_hour_bins)
        night_experiments_beeids[experiment_num] = retrieve_beeids_in_time_period(night_hour_bins)

    print(len(night_experiments_beeids[3]))
    print(len(day_experiments_beeids[3]))

    #merge_time_period_beeids(day_experiments_beeids)
    #merge_time_period_beeids(night_experiments_beeids)

    '''


if __name__ == "__main__":
    main()
