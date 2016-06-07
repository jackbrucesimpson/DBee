#!/usr/bin/env python

import os
import datetime

from .database import insert_db, query_db
from .metrics import Metrics

CAMERA_FRAMES_PER_SEC = 25
FRAMES_IN_AN_HOUR = CAMERA_FRAMES_PER_SEC * 60 * 60

def get_next_bee_id():
    query_result = query_db(table='bees', cols=['MAX(BeeID)'], fetchall=False)

    if query_result['MAX(BeeID)'] is None:
        return(0)
    else:
        return query_result['MAX(BeeID)'] + 1

def get_next_path_id():
    query_result = query_db(table='paths', cols=['MAX(PathID)'], fetchall=False)

    if query_result['MAX(PathID)'] is None:
        return(0)
    else:
        return query_result['MAX(PathID)'] + 1

def list_all_files(file_directory):
        csv_files = []
        for file in os.listdir(file_directory):
            if file.endswith(".csv") and not file.startswith("."):
                file_number = int(file.split('.')[0])
                csv_files.append(file_number)
        csv_files.sort()
        sorted_csv_files = [file_directory + str(f) + '.csv' for f in csv_files]
        return sorted_csv_files

def process_video_metadata(meta_file):
        file_lines_list = []
        with open(meta_file) as meta_csv:
            for line in meta_csv:
                line_split = [line_cols.strip() for line_cols in line.split(' ')]
                filename = os.path.splitext(line_split[0])[0].split('/')[-1]
                start_date_time = " ".join(line_split[1:])
                start_date_time = datetime.datetime.strptime(start_date_time, '%Y %b %d %H:%M:%S')
                file_lines_list.append([filename, start_date_time])
        return file_lines_list

def current_meta(list_all_files_metadata, base_file):
    current_csv_metadata = None
    for each_meta in list_all_files_metadata:
        if each_meta[0] == base_file:
            current_csv_metadata = each_meta
    return current_csv_metadata

def create_hour_bins_in_video(video_start_datetime, max_video_frame):
    next_hour = video_start_datetime + datetime.timedelta(hours=1)
    next_hour_rounded_by_hour = next_hour.replace(minute=0, second=0)
    time_to_hour_cutoff = next_hour_rounded_by_hour - video_start_datetime
    frame_num_first_cutoff = time_to_hour_cutoff.seconds * CAMERA_FRAMES_PER_SEC
    frames_in_rest_of_video = max_video_frame - frame_num_first_cutoff
    hours_in_rest_of_video = int(frames_in_rest_of_video / FRAMES_IN_AN_HOUR)
    if frames_in_rest_of_video % FRAMES_IN_AN_HOUR != 0:
        hours_in_rest_of_video += 1

    frame_cutoff = [frame_num_first_cutoff]
    hour_bins_in_video = [next_hour_rounded_by_hour]
    for each_hour in range(0, hours_in_rest_of_video):
        frame_cutoff.append(frame_cutoff[-1] + FRAMES_IN_AN_HOUR)
        add_hour_to_bin_datehour = hour_bins_in_video[-1] + datetime.timedelta(hours=1)
        hour_bins_in_video.append(add_hour_to_bin_datehour)

    #have to convert to strings outside loop because of strange time.delta issue
    hour_bins_in_video = [str(dt) for dt in hour_bins_in_video]
    return (hour_bins_in_video, frame_cutoff)

def insert_paths_coords(df, path_id, bee_id):
    """Iterate through dataframe of an individual bee and extract paths, filling in short gaps. It will update the DB with new paths.

    Args:
        df: Dataframe of bee X, Y coordinates and frames.
        path_id: Path ID to insert into database
        bee_id: Bee ID to insert into database

    Example:
        import pandas as pd
        d = {'X':[3,3,3,3,4,5,6,6,6,190],
            'Y':[8,6,4,2,2,2,2,2,2,2],
            'Frame':[1,2,3,13,50,51,53,55,56,57]}
        df = pd.DataFrame(d)
        print(insert_paths_coords(df, 1, 2))

    Returns:
        Incremented path ID"""

    MAX_FRAME_GAP_BETWEEN_PATHS = 25
    MAX_DISTANCE_PER_FRAME = 30
    max_frame = df['Frame'].max()

    # faster to iterate over list than pandas series
    list_frames_present = df['Frame'].tolist()
    list_x_coordinates = df['X'].tolist()
    list_y_coordinates = df['Y'].tolist()

    is_new_path = True
    prev_frame_index = 0

    all_x_paths = []
    all_y_paths = []
    all_frame_num_paths = []
    start_end_path_frames = []

    x_path = []
    y_path = []
    frame_num_path = []

    for i, frame in enumerate(list_frames_present):
        if is_new_path:
            start_path = list_frames_present[i]
            finish_path = list_frames_present[i]
            is_new_path = False
            prev_frame_index = i
            x_path.append(list_x_coordinates[i])
            y_path.append(list_y_coordinates[i])
            frame_num_path.append(list_frames_present[i])
        else:
            difference_prev_frame = list_frames_present[i] - list_frames_present[prev_frame_index]
            x1 = list_x_coordinates[i]
            y1 = list_y_coordinates[i]
            x2 = list_x_coordinates[prev_frame_index]
            y2 = list_y_coordinates[prev_frame_index]

            distance_moved = Metrics.calc_distance(x1, y1, x2, y2)
            if distance_moved / difference_prev_frame > MAX_DISTANCE_PER_FRAME:
                if len(x_path) > 0:
                    all_x_paths.append(x_path)
                    all_y_paths.append(y_path)
                    all_frame_num_paths.append(frame_num_path)
                    start_end_path_frames.append((start_path, finish_path))
                break

            if difference_prev_frame == 1:
                x_path.append(list_x_coordinates[i])
                y_path.append(list_y_coordinates[i])
                frame_num_path.append(list_frames_present[i])
                prev_frame_index = i
                finish_path = list_frames_present[i]
            else:
                if difference_prev_frame < MAX_FRAME_GAP_BETWEEN_PATHS:
                    x1 = list_x_coordinates[i]
                    y1 = list_y_coordinates[i]
                    x2 = list_x_coordinates[prev_frame_index]
                    y2 = list_y_coordinates[prev_frame_index]
                    x_diff_per_frame = (x2 - x1) / difference_prev_frame
                    y_diff_per_frame = (y2 - y1) / difference_prev_frame
                    for gap in range(1, difference_prev_frame + 1):
                        x_gap_coord = x2 - x_diff_per_frame * gap
                        y_gap_coord = y2 - y_diff_per_frame * gap
                        x_path.append(x_gap_coord)
                        y_path.append(y_gap_coord)
                        frame_num_path.append(list_frames_present[prev_frame_index] + gap)

                    prev_frame_index = i
                    finish_path = list_frames_present[i]

                else:
                    all_x_paths.append(x_path)
                    all_y_paths.append(y_path)
                    all_frame_num_paths.append(frame_num_path)
                    start_end_path_frames.append((start_path, finish_path))

                    x_path = [list_x_coordinates[i]]
                    y_path = [list_y_coordinates[i]]
                    frame_num_path = [list_frames_present[i]]

                    start_path = list_frames_present[i]
                    finish_path = list_frames_present[i]
                    prev_frame_index = i

            if list_frames_present[i] == max_frame:
                if len(x_path) > 0:
                    all_x_paths.append(x_path)
                    all_y_paths.append(y_path)
                    all_frame_num_paths.append(frame_num_path)
                    start_end_path_frames.append((start_path, finish_path))

    paths_db_values = []
    bee_coords_db_values = []
    for i, x_path_group in enumerate(all_x_paths):
        paths_db_values.append([path_id, bee_id, start_end_path_frames[i][0], start_end_path_frames[i][1]])
        for j, frame in enumerate(all_frame_num_paths[i]):
            bee_coords_db_values.append([path_id, all_frame_num_paths[i][j], all_x_paths[i][j], all_y_paths[i][j]])
        path_id += 1

    insert_db(table='paths', cols=['PathID', 'BeeID', 'StartPathFrame', 'EndPathFrame'], values=paths_db_values)
    insert_db(table='bee_coords', cols=['PathID', 'Frame', 'X', 'Y'], values=bee_coords_db_values)

    return path_id

def main():
    pass

if __name__ == "__main__":
    main()
