#!/usr/bin/env python3

import sys
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from beehaviour.csv_utils import list_all_files

class VideoQC:
    def __init__(self, csv_num):
        self.csv_num = csv_num
        self.bees_num_frames_tracked = []
        self.bees_num_times_classified = []
        self.frames_num_bees = []
        self.frames_num_classified_groups = []
        self.bee_tag_percentages = []

def main():
    CSV_DIRECTORY = sys.argv[1]
    experiment_name = sys.argv[2]
    ordered_csv_files = list_all_files(CSV_DIRECTORY)

    all_csv_qc = []
    combined_csv_qc = []
    combined_qc = None

    num_csvs = len(ordered_csv_files)
    count_csvs = 0
    num_grouped_csvs = 8
    for each_csv in ordered_csv_files:
        df = pd.read_csv(each_csv, comment='#', header = 0)
        filename = each_csv.split('/')[-1]
        base_file = os.path.splitext(filename)[0]
        print(base_file)

        qc = VideoQC(base_file)

        for group_name, bee_df in df.groupby('BeeID'):
            frames_bee_tracked = len(bee_df['Frame'])
            qc.bees_num_frames_tracked.append(frames_bee_tracked)
            bees_num_classified_groups = bee_df['Tag'].value_counts()
            qc.bees_num_times_classified.append(dict(bees_num_classified_groups))

            remove_zero_tags = bee_df[bee_df['Tag'] > 0]
            num_tags_classified = len(remove_zero_tags['Tag'])
            if num_tags_classified > 0:
                tag_identity = remove_zero_tags['Tag'].value_counts().idxmax()
                tag_percentage = remove_zero_tags['Tag'].value_counts().max() / len(remove_zero_tags['Tag'])
                qc.bee_tag_percentages.append(tag_percentage)

        for group_name, frame_df in df.groupby('Frame'):
            num_bees_in_frame = len(frame_df['BeeID'])
            qc.frames_num_bees.append(num_bees_in_frame)
            frame_num_classified_groups = frame_df['Tag'].value_counts()
            qc.frames_num_classified_groups.append(dict(frame_num_classified_groups))

        all_csv_qc.append(qc)

        count_csvs += 1

        if combined_qc is None:
            combined_qc = qc
        else:
            combined_qc.bees_num_frames_tracked.extend(qc.bees_num_frames_tracked)
            combined_qc.bees_num_times_classified.extend(qc.bees_num_times_classified)
            combined_qc.frames_num_bees.extend(qc.frames_num_bees)
            combined_qc.frames_num_classified_groups.extend(qc.frames_num_classified_groups)
            combined_qc.bee_tag_percentages.extend(qc.bee_tag_percentages)

        if count_csvs % num_grouped_csvs == 0 or count_csvs == num_csvs:
            combined_csv_qc.append(combined_qc)
            combined_qc = None

    plt.figure()
    plt.yscale('log')
    plt.boxplot([qc.bees_num_frames_tracked for qc in combined_csv_qc])
    plt.xlabel("Video Group")
    plt.ylabel("Frames")
    plt.title('Frames Bee Tracked')
    plt.savefig(experiment_name + 'frames_tracked.jpg')
    plt.clf()
    plt.close()

    plt.figure()
    plt.boxplot([qc.frames_num_bees for qc in combined_csv_qc])
    plt.xlabel("Video Group")
    plt.ylabel("Number of Bees")
    plt.title('Number of Bees Per Frame')
    plt.savefig(experiment_name + '_num_bees.jpg')
    plt.clf()
    plt.close()

    plt.figure()
    plt.boxplot([qc.bee_tag_percentages for qc in combined_csv_qc])
    plt.xlabel("Video Group")
    plt.ylabel("Confidence")
    plt.title('Bee Tag Classification Confidence')
    plt.savefig(experiment_name + '_classify.jpg')
    plt.clf()
    plt.close()

if __name__ == "__main__":
    main()
