#!/usr/bin/env python

from .database import DB

def parse_experiment_numbers(experiment_numbers_str):
    experiment_numbers_list_str = experiment_numbers_str.split(',')
    experiment_numbers = [int(number) for number in experiment_numbers_list_str]
    return experiment_numbers

def temp_table_comparison(create_temp_table, insert_list, temp_select):

    db = DB()

    db.cursor()
    db.modify(create_temp_table)
    db.close_cursor()

    print(create_temp_table)
    print(insert_list)

    db.cursor()
    for i in range(0, len(insert_list), 50000):
        subset_values = insert_list[i:i+50000]

        str_values = ''
        for value in subset_values:
            str_values += ', ' + '(' + str(value) + ')'
        str_values = str_values[2:]
        #print(str_values)
        insert_string = "INSERT INTO CurrentBeeIDs (BeeID) VALUES {};".format(str_values)
        db.modify(insert_string)
    db.close_cursor()

    #query_string = "SELECT * from CurrentBeeIDs;"
    query_string = temp_select
    db.cursor()
    query_result = db.query(query_string).fetchall()

    db.close_cursor()
    db.close_conn()

    print(query_result)


def main():
    pass

if __name__ == "__main__":
    main()
