# -*- coding:utf-8 -*-
# Date   : Mon Nov 05 17:42:05 2018 +0800
# Author : Rory Xiang


from pymysql import connect


def local_cursor():

    conn = connect(host='localhost', port=3306, db='xsp', user='root',
                   passwd='mysql', charset='utf8')
    cursor = conn.cursor()
    return cursor



