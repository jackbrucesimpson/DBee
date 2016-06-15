#!/usr/bin/env python

import pymysql
import gc
import os

class DB:
    _db_con = None
    _db_cur = None

    def __init__(self):
        password = os.environ.get("DBPW", None)
        self._db_con = pymysql.connect(host='localhost', port=3306, user='root', passwd=password, db='beedb')

    def last_insert_id(self):
        query_string = "SELECT LAST_INSERT_ID()"
        query_result = self.query(query_string, fetchall=False)
        insert_id = query_result['LAST_INSERT_ID()']

        return insert_id

    def query(self, query, fetchall=True): #, params
        try:
            self._db_cur = self._db_con.cursor(pymysql.cursors.DictCursor)
            self._db_cur.execute(query)
            if fetchall:
                query_result = self._db_cur.fetchall()
            else:
                query_result = self._db_cur.fetchone()

            self._db_cur.close()
            return query_result

        except Exception as e:
            print("query failed")
            print(str(e))
            self.close()
            gc.collect()
            return "Query failed"

    def modify(self, insert):
        try:
            self._db_cur = self._db_con.cursor(pymysql.cursors.DictCursor)
            self._db_cur.execute(insert)
            self._db_cur.close()
            return None

        except Exception as e:
            print('insert failed')
            print(str(e))
            self.close()
            gc.collect()
            return "Insert failed"

    def commit(self):
        try:
            self._db_con.commit()
        except Exception as e:
            print("Commit failed")
            print(str(e))
            self.close()
            gc.collect()

    def close(self):
        self._db_con.close()
        gc.collect()

    def commit_close(self):
        try:
            self._db_con.commit()
            self._db_con.close()
        except Exception as e:
            print("Commit failed")
            print(str(e))
            self.close()
            gc.collect()

    def query_string(self, table, cols, distinct=False, where='', group_condition='', group_list=[], subquery='', subquery_list=[], order=''):

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
        return query_string

    def insert_string(self, table, cols, values):
        str_colnames = ''
        for colname in cols:
            str_colnames += ', ' + colname
        str_colnames = str_colnames[2:] # remove extra comma at start

        str_values = ''
        for value in values:
            str_values += ', ({})'.format(str(value)[1:-1])
        str_values = str_values[2:]
        insert_string = "INSERT INTO {} ({}) VALUES {};".format(table, str_colnames, str_values)

        return insert_string

    def update_string(self, table, cols, values, where, group_condition='', group_list=[]):

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

        update_string = "UPDATE {} SET {} WHERE {}".format(table, str_set_values, where_statement)

        return update_string

    def delete_string(self, table, where, group_condition='', group_list=[]):

        where_statement = ''
        if len(where) > 0:
            where_statement += ' ' + where

        if len(group_condition) > 0:
            where_statement += ' {} ({})'.format(group_condition, str(group_list)[1:-1])

        delete_string = "DELETE FROM {} WHERE {}".format(table, where_statement)

        return delete_string

def main():
    pass

if __name__ == '__main__':
    main()
