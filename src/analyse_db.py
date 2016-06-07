#!/usr/bin/env python

import sys
import datetime
import random

from beehaviour.experiment import Experiment
from beehaviour.db_utils import parse_experiment_numbers

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

        #shuffled_day_beeids_seed_dict, shuffled_night_beeids_seed_dict = experiment.merge_shuffle_day_night_beeids(day_grouped_beeids, night_grouped_beeids, 100)

        experiment.generate_heatmaps(day_grouped_beeids[0], 40, 20, 'day_1')
        #experiment.generate_heatmaps(shuffled_day_beeids_seed_dict[0][0], 40, 20, 'shuffle_1')

        #shuffled_day_beeids_seed_dict, shuffled_night_beeids_seed_dict = experiment.merge_shuffle_day_night_beeids(day_grouped_beeids, night_grouped_beeids, 100)
        #print(shuffled_day_beeids_seed_dict.keys())
        #experiment.retrieve_bee_id_path(0)

if __name__ == "__main__":
    main()
