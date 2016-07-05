#!/usr/bin/env python3

import os
import numpy as np
import sys
sys.path.insert(0, '/Users/jack/Research')

from beehaviour.experiment import Experiment
from forecast import Weather, LogData

def main():
    hive_id = int(sys.argv[1])

    experiment = Experiment(hive_id)
    hour_blocks_in_experiment = experiment.retrieve_hour_blocks_in_experiment(hive_id)

    first_night = hour_blocks_in_experiment[0].strftime("%Y-%m-%d")

    api_key = os.environ.get("WEATHER_API_KEY", None)
    latitude, longitude = (-35.280317, 149.111644)
    weather = Weather(api_key, latitude, longitude)
    logger = LogData()

    parsed_days = []
    for date_time in hour_blocks_in_experiment:
        date_time_str = date_time.strftime("%Y-%m-%d")
        if date_time_str not in parsed_days:
            print(date_time_str)
            if date_time_str != first_night:
                forecast = weather.retrieve_forecast(date_time_str)
                hourly_weather = weather.retrieve_weather_by_hour(forecast)
                night_weather, day_weather = weather.summarise_night_day(hourly_weather, np.mean)
                logger.log_output(night_weather, date_time_str, 'night')
                logger.log_output(day_weather, date_time_str, 'day')

            parsed_days.append(date_time_str)

    logger.write_output('/Users/jack/Research/DBee/results/{}_weather.csv'.format(hive_id))

if __name__ == "__main__":
    main()
