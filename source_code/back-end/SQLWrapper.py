from typing import List, Dict, Tuple
import mysql.connector


def print_sql(fn):
    def wrapper(*args, **kwargs):
        sql = fn(*args, **kwargs)
        print(sql)
        return sql
    return wrapper


class SQLWrapper:
    """
    A SQL generator
    """
    def __init__(self, conn: mysql.connector.MySQLConnection):
        if not conn.is_connected():
            conn.reconnect(attempts=3, delay=1)
        self.conn = conn
        self.cursor = conn.cursor()
        self.sql = None
        self.table = []
        self.sigma = []

        # self.andcond = { field -> List[ Tuple('=', value, type(value)) ] }
        self.andcond = {}
        self.orcond = {}

        self.result = []

    def execute_raw(self, sql: str, commit=True, *args):
        self.cursor.execute(sql, *args)
        self.sql = sql
        self.result = self.cursor.fetchall()
        if commit:
            self.conn.commit()

    def commit(self):
        self.conn.commit()

    def where(self, field, op, value, type_: str, or_hints: bool = False):
        """
        add a where condition to a query

        :param field: field name of one condition
        :param op: =, >, < or their combination
        :param value: values of the condition
        :param type_: type of the value, if 'str', a quote will be added
        :param or_hints: whether to add OR to the condition

        """
        if not value:
            return
        if or_hints:
            if field not in self.orcond:
                self.orcond[field] = []
            self.orcond[field].append(tuple([op, value, type_]))
        else:
            if field not in self.andcond:
                self.andcond[field] = []
            self.andcond[field].append(tuple([op, value, type_]))

    def like(self, field, value, type_: str):
        """
        add a like condition to a query, a special case of where

        :param field: field name of one condition
        :param value: values of the condition

        """
        if not value or value == '%%':
            return
        if field not in self.andcond:
            self.andcond[field] = []
        self.andcond[field].append(tuple(['LIKE', value, type_]))

    def query(self, table: List[str], sigma: List[str]):
        """
        specify table and sigma to be query

        :param table: table name
        :param sigma: fields selected

        """
        self.table += table
        self.sigma += sigma

    def run(self, limit: int = None, join_method: str = 'NATURAL') -> int:
        """
        acturally execute the query, with a limit of rows

        :param limit: limit on row number requested
        :param join_method: join algorithm used (NATURAL or empty)
        :return: 0 on success, database error_code on failure

        """
        if not self.sigma:
            sigma = '*'
        else:
            sigma = ', '.join(self.sigma)
        sigma = f'SELECT {sigma} '

        assert self.table, 'No table specified'
        tables = f' {join_method} JOIN '.join(self.table)
        tables = f'FROM {tables} '

        if not self.andcond and not self.orcond:
            where = ''
        else:
            where_and = ''
            where_or = ''
            cond = []
            for k, v in self.andcond.items():
                for op, val, t in v:
                    val = val if t != 'str' else f'"{val}"'
                    cond.append(f'{k} {op} {val}')
            where_and = ' AND '.join(cond)
            cond = []
            for k, v in self.orcond.items():
                for op, val, t in v:
                    val = val if t != 'str' else f'"{val}"'
                    cond.append(f'{k} {op} {val}')
            where_or += ' OR '.join(cond)

            if where_and and where_or:
                where = f'WHERE {where_and} OR {where_or} '
            else:
                where = f'WHERE {where_and}{where_or} '

        limit = f'LIMIT {limit} ' if limit is not None else ''
        self.sql = sigma + tables + where + limit + ';'

        try:
            self.cursor.execute(self.sql)
        except mysql.connector.Error as err:
            return err.errno
        else:
            self.result = self.cursor.fetchall()
            return 0

    def get(self) -> List[Tuple]:
        """
        get the result.

        :return: a list of results, each result is a tuple of requested fields
        """

        assert self.sql is not None, 'No query executed'
        return self.result

    def clear(self):
        """
        clear the query build environment

        """
        self.sql = None
        self.table = []
        self.sigma = []
        self.andcond = {}
        self.orcond = {}
        self.result = []

    def insert(self, table: str, data: List[Tuple]) -> int:
        """
        insert a row to table, insertion (even multiple rows) is atomic

        :param table: table name
        :param data: a list of tuples to be inserted, each tuple is a row
        :return: 0 on success, database error_code on failure

        """
        placeholder = ', '.join(['%s'] * len(data[0]))
        try:
            self.cursor.executemany(f'INSERT INTO {table} VALUES ({placeholder})', data)
            # one insert call should be atomic
            self.conn.commit()
        except mysql.connector.Error as err:
            self.conn.rollback()
            return err.errno
        else:
            return 0

    def update(self, table: str, primary_keys: Dict, data: Dict) -> int:
        """
        update ONE row in table

        :param table: table name
        :param primary_keys: a dict of primary keys of the table, values are the conditions to find a row
                             e.g. {'patientId': '12345'}, condition is always equality
        :param data: fields and values to be updated, e.g. {'nation': 'China'}, it will update 'nation' field to be 'China'
        :return: 0 on success, database error_code on failure
        """

        set_placeholder = ', '.join([f'{k} = %s' for k in data.keys()])
        where_placeholder = ' AND '.join([f'{k} = %s' for k in primary_keys.keys()])
        values = tuple(data.values()) + tuple(primary_keys.values())

        try:
            self.cursor.execute(f'UPDATE {table} SET {set_placeholder} WHERE {where_placeholder};', values)
            self.conn.commit()
        except mysql.connector.Error as err:
            self.conn.rollback()
            return err.errno
        else:
            return 0

