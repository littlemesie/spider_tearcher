# coding:utf-8
'''
数据库配置
'''
DB_HOST = "localhost"
DB_PORT = "3306"
DB_USER = "root"
DB_PWD = "mesie1212"
DB_NAME = "tearcher"
DB_CHARSET = "utf8"
# mincached : 启动时开启的空连接数量(0代表开始时不创建连接)
DB_MIN_CACHED = 20
# maxcached : 连接池最大可共享连接数量(0代表不闲置连接池大小)
DB_MAX_CACHED = 20
# maxshared : 共享连接数允许的最大数量(0代表所有连接都是专用的)如果达到了最大数量,被请求为共享的连接将会被共享使用
DB_MAX_SHARED = 40
# maxconnecyions : 创建连接池的最大数量(0代表不限制)
DB_MAX_CONNECYIONS = 500
# blocking : 达到最大数量时是否阻塞(0或False代表返回一个错误<toMany......>; 其他代表阻塞直到连接数减少,连接被分配)
DB_BLOCKING = True
# maxusage : 单个连接的最大允许复用次数(0或False代表不限制的复用).当达到最大数时,连接会自动重新连接(关闭和重新打开)
DB_MAX_USAGE = 0
# setsession : 用于传递到数据库的准备会话，如 [”set name UTF-8″]
DB_SET_SESSION = None

