#!/usr/bin/env python

import sys
import os
import pandas as pd

import beehaviour.database import insert_db
from beehaviour.csv_utils import get_next_bee_id, get_next_path_id, list_all_files, process_video_metadata, current_meta, create_hour_bins_in_video, insert_paths_coords

def main():
    CSV_DIRECTORY = sys.argv[1]
    EXPERIMENT_NUMBER = int(sys.argv[2])
    HIVE_ID = int(sys.argv[3])
    HIVE_TYPE = int(sys.argv[4])
    METADATA_FILE = 'video_metadata.txt'
    NEXT_MAX_BEE_ID = get_next_bee_id()
    NEXT_MAX_PATH_ID = get_next_path_id()

    insert_db(table='experiment_meta', cols=['ExperimentNum', 'HiveType', 'HiveID'], values=[[EXPERIMENT_NUMBER, HIVE_TYPE, HIVE_ID]])

    ordered_csv_files = list_all_files(CSV_DIRECTORY)
    list_all_videos_metadata = process_video_metadata(CSV_DIRECTORY + METADATA_FILE)

    for each_csv in ordered_csv_files:
        df = pd.read_csv(each_csv, comment='#', header = 0)
        filename = each_csv.split('/')[-1]
        base_file = os.path.splitext(filename)[0]

        current_csv_metadata = current_meta(list_all_videos_metadata, base_file)
        if current_csv_metadata is None:
            sys.exit('Could not find metadata for current CSV file')
        video_start_datetime = current_csv_metadata[1]

        print('Processing experiment', EXPERIMENT_NUMBER, 'file number', base_file, 'which began on,', video_start_datetime, 'shape is', df.shape, 'and the max frame is', df['Frame'].max())

        hour_bins_video, frame_cutoff = create_hour_bins_in_video(video_start_datetime, df['Frame'].max())
        print(list(zip(hour_bins_video, frame_cutoff)))

        for i, each_cutoff in enumerate(frame_cutoff):
            bees_current_hour_df = df[df['Frame'] < each_cutoff]
            df = df[df['Frame'] > each_cutoff]
            list_bees_current_hour = []
            for group_name, bee_df in bees_current_hour_df.groupby('BeeID'):
                length_bee_tracked = len(bee_df['Frame'])
                remove_zero_tags = bee_df[bee_df['Tag'] > 0]
                num_tags_classified = len(remove_zero_tags['Tag'])
                if num_tags_classified > 0:
                    tag_identity = remove_zero_tags['Tag'].value_counts().idxmax()
                    tag_percentage = remove_zero_tags['Tag'].value_counts().max() / len(remove_zero_tags['Tag'])
                else:
                    tag_identity = 0
                    tag_percentage = 0

                insert_db(table='bees', cols=['BeeID','TagID','TagConfidence','NumTagClassified','LengthTracked','HiveID','HourBin'], values=[[NEXT_MAX_BEE_ID, tag_identity, tag_percentage, num_tags_classified, length_bee_tracked, HIVE_ID, hour_bins_video[i]]])

                NEXT_MAX_PATH_ID = insert_paths_coords(bee_df, NEXT_MAX_PATH_ID, NEXT_MAX_BEE_ID)
                NEXT_MAX_BEE_ID += 1

if __name__ == "__main__":
    main()
