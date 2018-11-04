# -*- coding:utf-8 -*-
'''
mysql连接
'''

import MySQLdb
from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
from data import config

class MysqlUtil(object):

    # 连接MySQL
    def connection(self):
        try:
            db = MySQLdb.connect(config.DB_HOST, config.DB_USER, config.DB_PWD, config.DB_NAME, charset=config.DB_CHARSET)
            cursor = db.cursor()
            return cursor
        except Exception:
            # 数据库连接失败
            return False

    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = MysqlUtil.get_conn()
    释放连接对象;conn.close()或del conn
    """
    # 连接池对象
    pool = None
    def __init__(self):
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self.conn = MysqlUtil.get_conn()
        self.cursor = self.conn.cursor()

    @staticmethod
    def get_conn():
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        connargs = {"host": config.DB_HOST, "user": config.DB_USER, "passwd": config.DB_PWD, "db": config.DB_NAME,
                    "charset": config.DB_CHARSET}
        if MysqlUtil.pool is None:
            MysqlUtil.pool = PooledDB(creator=MySQLdb, mincached=config.DB_MIN_CACHED, maxcached=config.DB_MAX_CACHED,
                               maxshared=config.DB_MAX_SHARED, maxconnections=config.DB_MAX_CONNECYIONS,
                               blocking=config.DB_BLOCKING, maxusage=config.DB_MAX_USAGE,
                               setsession=config.DB_SET_SESSION,**connargs)
            # print MysqlUtil.pool
        return MysqlUtil.pool.connection()

    def get_all(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询sql，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = self.cursor.execute(sql)
        else:
            count = self.cursor.execute(sql, param)
        if count > 0:
            result = self.cursor.fetchall()
        else:
            result = False
        return result

    def get_one(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询sql，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self.cursor.execute(sql)
        else:
            count = self.cursor.execute(sql, param)
        if count > 0:
            result = self.cursor.fetchone()
        else:
            result = False
        return result

    def get_many(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询sql，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self.cursor.execute(sql)
        else:
            count = self.cursor.execute(sql, param)
        if count > 0:
            result = self.cursor.fetchmany(num)
        else:
            result = False
        return result

    def insert_one(self, sql, value):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的sql格式
        @param value:要插入的记录数据tuple/list
        @return: insert_id 受影响的行数
        """
        try:
            self.cursor.execute(sql, value)
            self.conn.commit()
            return self.get_insert_id()
        except:
            self.conn.rollback()
            return 0

    def insert_many(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的sql格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        try:
            count = self.cursor.executemany(sql, values)
            self.conn.commit()
            return count
        except:
            self.conn.rollback()
            return 0

    def get_insert_id(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为0
        """
        self.cursor.execute("SELECT @@IDENTITY AS id")
        result = self.cursor.fetchall()
        return result[0][0]

    def query(self, sql, param=None):
        try:
            if param is None:
                count = self.cursor.execute(sql)
                self.conn.commit()
            else:
                count = self.cursor.execute(sql, param)
                self.conn.commit()
            return count

        except:
            self.conn.rollback()
            return 0


    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: sql格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: sql格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self.conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self.conn.commit()
        else:
            self.conn.rollback()

    def dispose(self, is_end=1):
        """
        @summary: 释放连接池资源
        """
        if is_end == 1:
            self.end('commit')
        else:
            self.end('rollback');
        self.cursor.close()
        self.conn.close()

    def execute_sql(self,sql):
        """
        @summary:执行原生SQL，主要是插入、更新、删除
        :param sql: 要执行的SQL语句
        :return: 1代表成功 0代表失败
        """
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return 1
        except:
            self.conn.rollback()
            return 0
