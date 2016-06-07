#!/usr/bin/env python

def parse_experiment_numbers(experiment_numbers_str):
    experiment_numbers_list_str = experiment_numbers_str.split(',')
    experiment_numbers = [int(number) for number in experiment_numbers_list_str]
    return experiment_numbers

def main():
    pass

if __name__ == "__main__":
    main()
