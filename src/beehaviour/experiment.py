#!/usr/bin/env python

import datetime
import random

from .database import query_db, add_list_to_where_statement

class Experiment:
    def __init__(self, hive_id):
        self.hive_id = hive_id

    def retrieve_hour_blocks_in_experiment(self, hive_id):
        hours_query_result = query_db(table='bees', cols=['HourBin'], distinct=True, where_str='HiveID={}'.format(hive_id))

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
        for each_group_hours in time_period_list_datetimes:
            beeids_in_time_group = []
            where_str = add_list_to_where_statement(colname_cond = "HourBin IN", group_list=[str(time) for time in each_group_hours])
            hours_query_result = query_db(table='bees', cols=['BeeID'], where_str=where_str)

            for bee_row in hours_query_result:
                beeids_in_time_group.append(bee_row['BeeID'])

            group_beeids.append(beeids_in_time_group)

        return group_beeids

    def merge_shuffle_day_night_beeids(self, day_grouped_beeids, night_grouped_beeids, shuffle_iterations):
        combined_day_night_bee_ids = []
        for i, time_grouped_ids in enumerate(day_grouped_beeids):
            try:
                group_day_night = day_grouped_beeids[i] + night_grouped_beeids[i]
                combined_day_night_bee_ids.append(group_day_night)
            except Exception:
                break

        shuffled_day_beeids_seed_dict = {}
        shuffled_night_beeids_seed_dict = {}
        for i in range(shuffle_iterations):
            random.seed(i)
            shuffled_day_beeids_seed_dict[i] = []
            shuffled_night_beeids_seed_dict[i] = []

            for j, combined_grouped_ids in enumerate(combined_day_night_bee_ids):
                random.shuffle(combined_grouped_ids)
                random_shuffled_day = combined_grouped_ids[:len(day_grouped_beeids[j])]
                random_shuffled_night = combined_grouped_ids[len(day_grouped_beeids[j]):]

                shuffled_day_beeids_seed_dict[i].append(random_shuffled_day)
                shuffled_night_beeids_seed_dict[i].append(random_shuffled_night)

        return (shuffled_day_beeids_seed_dict, shuffled_night_beeids_seed_dict)

def main():
    pass

if __name__ == "__main__":
    main()
