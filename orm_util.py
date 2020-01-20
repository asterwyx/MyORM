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
def generate_string_by_field_desc(field_desc):
    field_string = ""
    field_string += "\t%s = " % field_desc['Field']
    # 由于时间问题，目前只支持三种数据类型的映射
    if field_desc['Type'] == "bigint(20)":
        field_string += "IntegerField("
    elif field_desc['Type'] == "double":
        field_string += "DoubleField("
    elif field_desc['Type'].startwith("varchar"):
        field_string += "StringField("
    else:
        pass
    if not field_desc['Null'] == "NO":
        field_string += "null=True, "
    if not field_desc['Default'] is None:
        field_string += "default=%s, " % field_desc['Default']
    if field_desc['Key'] == "PRI":
        field_string += "primary=True, "
    elif field_desc[''] == "MUL":
        field_string += "foreign=True, "
    else:
        pass
    if field_desc['Extra'] is not "":
        field_string += "auto_increment=True"
    field_string += ")\n"
    return field_string


def generate_string_by_create_desc(table_name, field_list):
    string = ""
    name_list = re.split(r"_", table_name)
    for word in name_list:
        word.capitalize()
    class_name = "".join(name_list)
    string += "class %s(Model):\n" % class_name
    for field in field_list:
        string += generate_string_by_field_desc(field)
    string += "\n"
    return string


def map_from_database():
    sql = "SHOW CREATE TABLE *;"
    set_db.cursor.execute(sql)
    results = set_db.cursor.fetchall()
    for row in results:
        t_name = row[0]
        print(t_name)
    try:
        model_file = open(file=settings.model_path, mode='rt', encoding='utf8')
        # 因为一般的代码文件都不是很大，所以这里选择直接读取整个文件，这样便于做插入
        content = model_file.readlines()
        model_file.close()  # 直接关闭文件流，之后再用书写模式打开
        model_structure_file = open(file=settings.model_structure_path, mode='a+', encoding='utf8')
        model_structure = json.load(model_structure_file)
        table_desc_list = model_structure['structure']
        for row in results:
            t_name = row[0]
            sql = "SHOW CREATE TABLE %s;" % t_name
            set_db.cursor.execute(sql)
            structure = set_db.cursor.fetchone()
            sql = "DESC %s" % t_name
            set_db.cursor.execute(sql)
            desc = set_db.cursor.fetchall()
            for table_desc in table_desc_list:
                if structure['Table'] == table_desc['name']:
                    if structure['Create Table'] == table_desc['create']:
                        break  # 跳出该表的新鲜度对比循环，且不做任何更改
                    else:
                        table_desc['create'] = structure['Create Table']  # 更新表的结构
                        table_desc['desc'] = desc
                        # 重新生成类
                        start_cursor = 0
                        # 找到model.py文件中对应的类的定义的开头
                        for i in range(0, table_desc['serial']):
                            while True:
                                sentence = content[start_cursor]
                                start_cursor += 1
                                if not sentence or sentence == "# start":
                                    break
                        # 现在文件指针指向类的定义的开头, 找到类的结尾
                        end_cursor = start_cursor
                        while content[end_cursor] != "# end":
                            end_cursor += 1
                        class_str = generate_string_by_create_desc(table_desc['name'], table_desc['desc'])
                        content.insert(start_cursor, class_str)   # 插入到原本的开头
                        # 删除原来的内容，重新拼接
                        new_content = content[:start_cursor + 1] + content[end_cursor:]
                        contents = "".join(new_content)
                        with open(file=settings.model_path, mode='wt', encoding='utf8') as model_file:
                            model_file.write(contents)
    except FileNotFoundError:
        return None
    finally:
        model_structure_file.close()


# 将model.py文件中的类映射到数据库，同样采用增量映射
def map_to_database():
    pass

# 为了将类和数据库中的表进行比较，还需要创建一个文件储存类形成的表的结构和model.py同步更新
