import pandas as pd
import numpy as np

class Experiment:
    def __init__(self, metrics, experiment_name, real_df, shuffled_df, bootstrapped_df):
        self.name = experiment_name
        self.real_df = real_df
        self.shuffled_df = shuffled_df
        self.bootstrapped_df = bootstrapped_df
        self.metrics = {m:[] for m in metrics}

    def __repr__(self):
        return 'Experiment({})'.format(self.name)

    def get_tag_df(self, tag_type):
        ''' Tag Type can be '0', '1', '2', '3', 'All' '''
        tag_df = df[df['tag_type'] == tag_type].reset_index()
        return tag_df

class OutputAnalysis:
    def __init__(self, experiment_csvs, experiment_names):
        self.experiments = {}

        for i, f in enumerate(experiment_csvs):
            df = pd.read_csv(f, comment='#', header = 0)
            real_df = df[df['result_type'] == 'real'].reset_index()
            shuffled_df = df[df['result_type'] == 'shuffled'].reset_index()
            bootstrapped_df = df[df['result_type'] == 'bootstrapped'].reset_index()
            self.experiments[experiment_names[i]] = Experiment(experiment_names[i], real_df, shuffled_df, bootstrapped_df)

    def minus_day_from_night(self,):

    def minus_tag1_from_tag2(self, tag1, tag2):


    def x(self, ):
        # how many permutations for each day of experiment: as of writing this there should be 100
        num_permutations_run = int(len(shuffled_df[shuffled_df['day_num']==0]) / 2)


extended_metrics = ['median_all_tracked_speeds', 'spread_all_tracked_all_xy', 'percent_idle_all_tracked']
shuffled_permutations = []

for shuffled_df in shuffled_result_df_list:
    num_perms = int(len(shuffled_df[shuffled_df['day_num']==0]) / 2)
    empty_lists = [[] for i in range(num_perms)]
    permutations = {}
    for m in extended_metrics:
        permutations[m] = copy.deepcopy(empty_lists)
    #permutations = {'diff_spread_all_tracked_all_xy': copy.deepcopy(empty_lists)}

    days_nums_in_experiment = list(shuffled_df['day_num'].unique())
    days_nums_in_experiment.sort()
    for day_num in days_nums_in_experiment:
        day_num_df = shuffled_df[shuffled_df['day_num'] == day_num]
        night_df = day_num_df[day_num_df['time_period'] == 'night']
        #day_df = day_num_df[day_num_df['time_period'] == 'day']

        for metric in permutations.keys():
            night_metric = list(night_df[metric])
            #day_metric = list(day_df[metric])
            for i, group in enumerate(permutations[metric]):
                permutations[metric][i].append(night_metric[i])
                #permutations[metric][i].extend([night_metric[i], day_metric[i]])

    shuffled_permutations.append(permutations)


print(shuffled_permutations[0]['diff_median_all_tracked_speeds'])
