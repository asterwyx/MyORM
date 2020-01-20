# -*- coding: UTF-8 -*-
# 这个文件是模块主体，提供各种工具函数

import re
import meta_class
from pymysql import *
import settings
import json


class DBConnection(object):
    def __init__(self, host, port, user, passwd, database, charset):
        self.conn = Connect(host=host, port=port, user=user, passwd=passwd, db=database, charset=charset)
        self.cursor = self.conn.cursor()


# 全局数据连接变量用于配置
set_db = DBConnection(host=settings.setting_dict['host'], port=settings.setting_dict['port'],
                      user=settings.setting_dict['username'], passwd=settings.setting_dict['password'],
                      database=settings.setting_dict['database'], charset=settings.setting_dict['charset'])


# 用来从数据库读取已经存在的表建立类的函数，从数据库自动映射，这个函数采用增量映射，只会更新修改过的表
def map_from_database():
    sql = "SHOW CREATE TABLE *;"
    set_db.cursor.execute(sql)
    results = set_db.cursor.fetchall()
    for row in results:
        t_name = row[0]
        print(t_name)
    try:
        model_file = open(file=settings.model_path, mode='a+', encoding='utf8')
        model_structure_file = open(file=settings.model_structure_path, mode='a+', encoding='utf8')
        model_structure = json.load(model_structure_file)
        table_desc_list = model_structure['structure']
        for row in results:
            t_name = row[0]
            sql = "SHOW CREATE TABLE %s;" % t_name
            set_db.cursor.execute(sql)
            structure = set_db.cursor.fetchone()
            for table_desc in table_desc_list:
                if structure['Table'] == table_desc['name']:
                    if structure['Create Table'] == table_desc['create']:
                        break  # 跳出该表的新鲜度对比循环，且不做任何更改
                    else:
                        table_desc['create'] = structure['Create Table']  # 更新表的结构
                        # 重新生成类
                        model_file.seek(0, 0)  # 文件指针复原
                        # 找到model.py文件中对应的类的定义
                        for i in range(0, table_desc['serial']):
                            while True:
                                sentence = model_file.readline()
                                if not sentence or sentence == "# start":
                                    break
                        # 现在文件指针指向类的定义的开头
                        sentence = 



    except FileNotFoundError:
        return None
    finally:
        model_file.close()
        model_structure_file.close()


# 将model.py文件中的类映射到数据库，同样采用增量映射
def map_to_database():
    pass

# 为了将类和数据库中的表进行比较，还需要创建一个文件储存类形成的表的结构和model.py同步更新
