#!/usr/bin/env python

import sys
import datetime
import random

from database import DB

def parse_experiment_numbers(experiment_numbers_str):
    experiment_numbers_list_str = experiment_numbers_str.split(',')
    experiment_numbers = [int(number) for number in experiment_numbers_list_str]
    return experiment_numbers




class Experiment:
    def __init__(self, experiment_id):
        self.experiment_id = experiment_id

    def retrieve_hour_blocks_in_experiment(self, experiment_num):
        db = DB()
        db.cursor()
        query_string = "SELECT DISTINCT HourBin FROM bees WHERE ExperimentNum={}".format(experiment_num)
        hours_query_result = db.query(query_string).fetchall()
        db.close_cursor()
        db.close_conn()

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
        db = DB()
        for each_group_hours in time_period_list_datetimes:
            beeids_in_time_group = []
            str_each_group_hours = str([str(time) for time in each_group_hours])[1:-1]
            db.cursor()
            query_string = "SELECT BeeID FROM bees WHERE HourBin IN ({})".format(str_each_group_hours)
            hours_query_result = db.query(query_string).fetchall()
            db.close_cursor()

            for bee_row in hours_query_result:
                beeids_in_time_group.append(bee_row['BeeID'])

            group_beeids.append(beeids_in_time_group)

        db.close_conn()

        return group_beeids

    def merge_day_night_beeids(self, day_grouped_beeids, night_grouped_beeids):
        combined_day_night_bee_ids = []
        for i, time_grouped_ids in enumerate(day_grouped_beeids):
            try:
                group_day_night = day_grouped_beeids[i] + night_grouped_beeids[i]
                combined_day_night_bee_ids.append(group_day_night)
            except Exception:
                pass
        return combined_day_night_bee_ids

    def shuffle_bee_ids(self, combined_day_night_bee_ids):
        random_day_grouped_beeids = []
        random_night_grouped_beeids = []

        for time_grouped_ids in combined_day_night_bee_ids:
            print(time_grouped_ids[0])
            random.shuffle(time_grouped_ids)
            print(time_grouped_ids[0], '\n')
            half_len = int(len(time_grouped_ids)/2)
            random_day_grouped_beeids.append(time_grouped_ids[:half_len])
            random_night_grouped_beeids.append(time_grouped_ids[half_len:])




def main():
    experiment_numbers = parse_experiment_numbers(sys.argv[1])

    experiments_object_list = []
    for experiment_num in experiment_numbers:
        experiment = Experiment(experiment_num)
        hour_blocks_in_experiment = experiment.retrieve_hour_blocks_in_experiment(experiment_num)
        day_hour_bins, night_hour_bins = experiment.group_hours_by_night_day(hour_blocks_in_experiment)

        day_grouped_beeids = experiment.retrieve_beeids_in_time_period(day_hour_bins)
        night_grouped_beeids = experiment.retrieve_beeids_in_time_period(night_hour_bins)

        combined_day_night_bee_ids = experiment.merge_day_night_beeids(day_grouped_beeids, night_grouped_beeids)

        for i in range(1000):


        experiment.shuffle_bee_ids(combined_day_night_bee_ids, seed)


        #experiments_object_list.append(experiment)


    '''
    day_experiments_beeids = {}
    night_experiments_beeids = {}
    for experiment_num in experiment_numbers:
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
