from .db import DB

def query_db(table, cols, distinct=False, fetchall=True, where='', group_condition='', group_list=[], subquery='', subquery_list=[], order=''):
    """Query database columns with optional where statement and option to fetch multiple rows (default) or single row.

    Args:
        table: Table to query.
        cols: Column names with values of interest.
        distinct: Only retrieves distinct rows, defaults to False.
        fetchall: Default of True, fetches all relevant rows, False fetches only a single row.
        where: Where conditional, defaults to ''.
        group_condition: condition to check against list, defaults to ''.
        group_list: list to check values in.
        subquery: subquery where statement, defaults to ''.
        subquery_list: list to check values in.
        order: string to order results by, defaults to ''.

    Example:
        query_db(table='bees', cols=['HourBin'], where='HiveID=1', group_condition='AND HiveID IN', group_list=[1,2,3])
        query_db(table='paths', cols=['*'], where='BeeID IN', subquery='select beeid from bees where beeid IN', subquery_list=[0,1])
        query_db(table='bee_coords, paths', cols=['paths.BeeID', 'bee_coords.PathID', 'bee_coords.Frame',
                    'bee_coords.X', 'bee_coords.Y'], where='bee_coords.PathID = paths.PathID',
                    group_condition='AND BeeID IN', group_list=list_bee_ids, order='ORDER BY Frame ASC')

    Returns:
        List of dictionaries referring to column names unless fetchall is False, then it just returns a single dictionary"""

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
        where_statement += ' {} ({})'.format(group_condition, str(group_list)[1:-1])

    if len(subquery) > 0:
        where_statement += ' ' + ' (' + subquery
        if len(subquery_list) > 0:
            where_statement += ' ({})'.format(str(subquery_list)[1:-1])
        where_statement += ')'

    if len(order) > 0:
        where_statement += ' ' + order

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
            str_values += ', ({})'.format(str(value)[1:-1])
        str_values = str_values[2:]
        insert_string = "INSERT INTO {} ({}) VALUES {};".format(table, str_colnames, str_values)

        db.modify(insert_string)

    db.close_cursor()
    db.close_conn()

    return None


def update_db(table, cols, values, where, group_condition='', group_list=[]):
    """Updates columns from table with values where conditions are met

    Args:
        table: Table to insert rows into.
        cols: Column names into which the values will be inserted.
        values: A list of lists containing the values to insert.
        where: where condition to update rows.
        group_condition: where condition to compare to list of values.
        group_list: list of values used for where condition.

    Example:
        update_db(table='bees', cols=['BeeID', 'TagID'], values=['1', 2], where='BeeID=1 AND', group_condition='TagID IN', group_list=['1',2,3,4,5,6])

    Returns:
        None"""

    # zip and selection of value done to preserve quotation marks in string
    str_set_values = ''
    combine_cols_values = list(zip(cols, values))
    for col_value_tup in combine_cols_values:
        str_set_values += ', {}={}'.format(col_value_tup[0], str(list(col_value_tup[1:]))[1:-1])
    str_set_values = str_set_values[2:]

    where_statement = ''
    if len(where) > 0:
        where_statement += ' ' + where

    if len(group_condition) > 0:
        where_statement += ' {} ({})'.format(group_condition, str(group_list)[1:-1])

    db = DB()
    db.cursor()
    update_string = "UPDATE {} SET {} WHERE {}".format(table, str_set_values, where_statement)
    db.modify(update_string)
    db.close_cursor()
    db.close_conn()

    return None

def delete_db(table, where, group_condition='', group_list=[]):
    """Deletes rows from table where conditions are met

    Args:
        table: Table to insert rows into.
        where: where condition to update rows.
        group_condition: where condition to compare to list of values.
        group_list: list of values used for where condition.

    Example:
        delete_db(table='bees', where='BeeID=1 AND', group_condition='TagID IN', group_list=['1',2,3])

    Returns:
        None"""

    where_statement = ''
    if len(where) > 0:
        where_statement += ' ' + where

    if len(group_condition) > 0:
        where_statement += ' {} ({})'.format(group_condition, str(group_list)[1:-1])

    db = DB()
    db.cursor()
    delete_string = "DELETE FROM {} WHERE {}".format(table, where_statement)
    db.modify(delete_string)
    db.close_cursor()
    db.close_conn()

    return None
