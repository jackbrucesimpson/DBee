from .db import DB

def insert_db(table, cols, values):
    """Inserts list of lists into the table and columns of the database. It handles string conversion and also potential crashes that can occur when writing too many rows at the same time.

    Args:
        table: Table to insert rows into.
        cols: Column names into which the values will be inserted.
        values: A list of lists containing the values to insert.

    Example:
        insert_db(table='experiment_meta', cols=['ExperimentNum', 'HiveType'], values=[[1, 2, 'a'], [3, 4, 'b'], [5,6, 'c']])

    Returns:
        None"""

    db = DB()

    str_colnames = ''
    for colname in cols:
        str_colnames += ', ' + colname
    str_colnames = str_colnames[2:] # remove extra comma at start

    db.cursor()
    for i in range(0, len(values), 50000):
        subset_values = values[i:i+50000]

        str_values = ''
        for value in subset_values:
            str_values += ', ' + '(' + str(value)[1:-1] + ')'
        str_values = str_values[2:]
        insert_string = "INSERT INTO {} ({}) VALUES {};".format(table, str_colnames, str_values)

        db.modify(insert_string)

    db.close_cursor()
    db.close_conn()

def query_db(table, cols, distinct=False, fetchall=True, where='', group_condition='', group_list=[], subquery='', subquery_list=[]):

    if distinct:
        distinct = 'DISTINCT'
    else:
        distinct = ''

    str_colnames = ''
    for colname in cols:
        str_colnames += ', ' + colname
    str_colnames = str_colnames[2:] # remove extra comma at start

    where_statement = ''
    if len(where) > 0 or len(group_condition) > 0 or len(subquery) > 0:
        where_statement += 'WHERE'

    if len(where) > 0:
        where_statement += ' ' + where

    if len(group_condition) > 0:
        where_statement += ' ' + group_condition + ' (' + str(group_list)[1:-1] + ')'

    if len(subquery) > 0:
        where_statement += ' ' + ' (' + subquery
        if len(subquery_list) > 0:
            where_statement += ' ' + '(' + str(subquery_list)[1:-1] + ')'
        where_statement += ')'

    query_string = "SELECT {} {} FROM {} {};".format(distinct, str_colnames, table, where_statement)

    db = DB()
    db.cursor()
    if fetchall:
        query_result = db.query(query_string).fetchall()
    else:
        query_result = db.query(query_string).fetchone()

    db.close_cursor()
    db.close_conn()

    return query_result

def add_list_to_where_statement(colname_cond, group_list, current_where_str='', joining_str_cond=''):
    """Extends a where conditional string with a list which you want to check a column being/not being in.

    Args:
        colname_cond: Column name and condition about list it is being compared to.
        group_list: List of values to compare to column values.
        current_where_str: String with current version of where statement (defaults to empty).
        joining_str_cond: String with joining condition (defaults to empty).

    Example:
        add_list_to_where_statement(colname_cond = "ExperimentNum IN", group_list=[1,2,3,4,5,6,7,8,9,10], current_where_str = "ExperimentNum = 1", joining_str_cond = 'AND')

    Example Returns:
        ExperimentNum = 1 AND ExperimentNum IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

    Returns:
        String where statement"""

    current_where_str += ' ' + joining_str_cond + ' ' + colname_cond + ' (' + str(group_list)[1:-1] + ')'
    return current_where_str
