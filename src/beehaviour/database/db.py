

import pymysql
import gc
import os

class DB:
    _db_con = None
    _db_cur = None

    def __init__(self):
        password = os.environ.get("DBPW", None)
        self._db_con = pymysql.connect(host='localhost', port=3306, user='root', passwd=password, db='beedb')

    def cursor(self):
        try:
            self._db_cur = self._db_con.cursor(pymysql.cursors.DictCursor)
        except Exception as e:
            print("Cursor failed")
            print(str(e))
            self.close_conn()
            gc.collect()
            return "Cursor failed"

    def query(self, query): #, params
        try:
            self._db_cur.execute(query)
            return self._db_cur
        except Exception as e:
            print("query failed")
            print(str(e))
            self.close_cursor()
            self.close_conn()
            gc.collect()
            return "Query failed"

    def modify(self, insert):
        try:
            self._db_cur.execute(insert)
            self._db_con.commit()
        except Exception as e:
            print('insert failed')
            print(str(e))
            self.close_cursor()
            self.close_conn()
            gc.collect()
            return "Insert failed"

    def close_cursor(self):
        self._db_cur.close()

    def close_conn(self):
        self._db_con.close()
        gc.collect()

def main():
    pass

if __name__ == '__main__':
    main()
