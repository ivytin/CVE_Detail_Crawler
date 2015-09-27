#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'arvin'

import mysql.connector as connector
from mysql.connector.errors import Error as OperationError


class MySql:
    """ mysql operation class

    include common operating function such as query, update

    Attributes:
        host: mysql server host target
        port: mysql host port
        user: mysql user name
        password: mysql user password
        charset: mysql charset
        database: mysql scheme selected
        conn: mysql connection
        cursor: mysql cursor
    """

    def __init__(self, host, user, password, database, port=3306, charset='utf8'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.charset = charset
        self.database = database

        self.conn = connector.connect(user=self.user, password=self.password,
                                      host=self.host, database=self.database)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.close()

    # def select_db(self, db):
    #     try:
    #         self.conn.database(db)
    #     except OperationError, e:
    #         print 'Mysql error:', e

    def query(self, sql):
        try:
            n = self.cursor.execute(sql)
            return n
        except OperationError, e:
            print 'Mysql execute error: %s\n' % sql, e

    def fetch_row(self):
        result = self.cursor.fetchone()
        return result

    def fetch_all(self):
        result = self.cursor.fetchall()
        desc = self.cursor.description
        d = []
        for inv in result:
            _d = {}
            for i in xrange(len(inv)):
                _d[desc[i][0]] = str(inv[i])
            d.append(_d)
        print d
        return d

    def insert(self, table_name, data):
        columns = data.keys()
        _prefix = ''.join(['INSERT INTO `', table_name, '`'])
        _fields = ','.join([''.join(['`', column, '`']) for column in columns])
        _value = ','.join(['%s' for i in xrange(len(columns))])
        _sql = ''.join([_prefix, '(', _fields, ') VALUES (', _value, ')'])
        _params = [data[key] for key in columns]
        return self.cursor.execute(_sql, tuple(_params))

    def update(self, tbname, data, condition):
        _fields = []
        _prefix = ''.join(['UPDATE `', tbname, '`', 'SET'])
        for key in data.keys():
            _fields.append('%s = %s' %(key, data[key]))
        _sql = ''.join([_prefix, _fields, 'WHERE', condition])

        return self.cursor.execute(_sql)

    def delete(self, tbname, condition):
        _prefix = ''.join(['DELETE FROM `', tbname, '`', 'WHERE'])
        _sql = ''.join([_prefix, condition])
        return self.cursor.execute(_sql)

    def get_last_insert_id(self):
        return self.cursor.lastrowid

    def row_count(self):
        return self.cursor.rowcount

    def commit(self):
        self.conn.commit()

    def roll_back(self):
        self.conn.rollback()

    def close(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    n = MySql('127.0.0.1', 'root', 'tanxiao123', 'test', 3306)
    # tbname = 'map'
    # a = ({'id': 3, 'x': 3, 'y': 3},
    #      {'id': 4, 'x': 4, 'y': 4},
    #      {'id': 5, 'x': 5, 'y': 5}
    #      )
    #
    # for d in a:
    #     n.insert(tbname, d)
    #
    # n.commit()
    n.query('SELECT * FROM `map`')
    d = n.fetch_all()
    print d

