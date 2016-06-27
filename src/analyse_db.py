#!/usr/bin/env python3

import sys
import datetime
import random
import numpy as np
import pandas as pd

from beehaviour.experiment import Experiment

np.random.seed(1)

def parse_experiment_numbers(experiment_numbers_str):
    experiment_numbers_list_str = experiment_numbers_str.split(',')
    experiment_numbers = [int(number) for number in experiment_numbers_list_str]
    return experiment_numbers

def main():
    all_hive_ids = parse_experiment_numbers(sys.argv[1])

    for hive_id in all_hive_ids:
        experiment = Experiment(hive_id)

        for day_num, day_grouped_bees in enumerate(experiment.day_grouped_bees):
            experiment.calculate_day_night_metrics(day_num)

        output_df = pd.DataFrame(experiment.output)
        output_df.to_csv('{}{}_output.csv'.format(experiment.output_dir, experiment.hive_id))

if __name__ == "__main__":
    main()
