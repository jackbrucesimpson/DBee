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

        combined_day_night_bee_ids = experiment.merge_day_night_beeids(day_grouped_beeids, night_grouped_beeids)

        random.seed(1)
        print("starting day/night loop")
        for i, day_night_period_bee_ids in enumerate(combined_day_night_bee_ids):
            print("Day {}".format(i))
            bee_id_dict = experiment.retrieve_bee_id_path(combined_day_night_bee_ids[i])
            shuffled_day_beeids, shuffled_night_beeids = experiment.shuffle_day_night_beeids(combined_day_night_bee_ids[i], day_grouped_beeids[i], 100)
            day_spread = experiment.generate_heatmaps(day_grouped_beeids[i], bee_id_dict, 40, 20, 'day_{}_'.format(i))
            night_spread = experiment.generate_heatmaps(night_grouped_beeids[i], bee_id_dict, 40, 20, 'night_{}_'.format(i))
            print(day_spread, night_spread)

            for j, shuffled_day in enumerate(shuffled_day_beeids):
                shuffled_day_spread = experiment.generate_heatmaps(shuffled_day_beeids[j], bee_id_dict, 40, 20, 'shuffled_day_{}_{}_'.format(i, j))
                shuffled_night_spread = experiment.generate_heatmaps(shuffled_night_beeids[j], bee_id_dict, 40, 20, 'shuffled_night_{}_{}_'.format(i, j))


        #import time

        #t0 = time.time()
        #experiment.retrieve_bee_id_path(x)
        #t1 = time.time()

        #total = t1-t0
        #print(total)

        #shuffled_day_beeids_seed_dict, shuffled_night_beeids_seed_dict = experiment.merge_shuffle_day_night_beeids(day_grouped_beeids, night_grouped_beeids, 10)
        #experiment.generate_heatmaps(day_grouped_beeids[0][0:10], 40, 20, 'day_1_')
        #experiment.generate_heatmaps(night_grouped_beeids[0], 40, 20, 'night_1_')
        #experiment.generate_heatmaps(shuffled_day_beeids_seed_dict[0][0][:100], 40, 20, 'shuffle_1')

if __name__ == "__main__":
    main()
