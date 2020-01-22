from orm_util import *

# 用metaclass实现一个ORM框架
# 最基本的字段类，负责保存数据库中的字段名和字段类型
db = DBConnection(host=settings.setting_dict['host'], port=settings.setting_dict['port'],
                  user=settings.setting_dict['username'], passwd=settings.setting_dict['password'],
                  database=settings.setting_dict['database'], charset=settings.setting_dict['charset'])


class Field(object):
    def __init__(self, name, column_type, null, default, primary, foreign, auto_increment):
        self.name = name
        self.column_type = column_type
        self.null = null
        self.default = default
        self.primary = primary
        self.foreign = foreign
        self.auto_increment = auto_increment
        self.value = None

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)

    # 让子类重写的方法
    def print_value(self):
        pass


# 继承自字段类的字符串字段类，具有字符串类型的字段
class StringField(Field):
    def __init__(self, name, null=True, default=None, primary=False, foreign=False, auto_increment=False):
        super(StringField, self).__init__(name, "VARCHAR(100)", null, default, primary, foreign, auto_increment)

    def print_value(self):
        if self.value:
            return "\"%s\"" % self.value
        else:
            return None


# 继承自字段类的整数型字段类，具有整数类型的字段
class IntegerField(Field):
    def __init__(self, name, null=True, default=None, primary=False, foreign=False, auto_increment=False):
        super(IntegerField, self).__init__(name, "BIGINT", null, default, primary, foreign, auto_increment)

    def print_value(self):
        if self.value:
            return "%d" % self.value
        else:
            return None


class DoubleField(Field):
    def __init__(self, name, null=True, default=None, primary=False, foreign=False, auto_increment=False):
        super(DoubleField, self).__init__(name, "DOUBLE", null, default, primary, foreign, auto_increment)

    def print_value(self):
        if self.value:
            return "%f" % self.value
        else:
            return None


# 元类
class ModelMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        if name == 'Model':
            return type.__new__(mcs, name, bases, attrs)
        print('Found model: %s' % name)
        mappings = dict()
        for k, v in attrs.items():
            # print("\"%s\": %s" % (k, v))
            if isinstance(v, Field):
                print('Found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
        for k in mappings.keys():
            attrs.pop(k)
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        return type.__new__(mcs, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)
        for k in self.__mappings__.keys():
            self.__mappings__[k].value = self[k]

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute %s" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def save(self):
        fields = []
        params = []
        args = []
        for k, v in self.__mappings__.items():
            fields.append(v.name)
            params.append(v.print_value())
            args.append(getattr(self, k, None))
        sql = "INSERT INTO %s (%s) VALUES (%s);" % (self.__table__, ", ".join(fields), ", ".join(params))
        print('SQL: %s' % sql)
        print('ARGS: %s' % str(args))
        try:
            db.cursor.execute(sql)
            db.conn.commit()
        except Error:
            db.conn.rollback()

    def get_by_id(self, record_id):
        sql = "SELECT * FROM %s WHERE %s=%s;" % (self.__table__, self.__mappings__['id'].name, record_id)
        try:
            db.cursor.execute(sql)
            db.conn.commit()
        except Error as e:
            print(e)
            db.conn.rollback()
        result = db.cursor.fetchone()
        # print(result)
        return type(self.__class__.__name__, (Model, dict), result)

    def get_all(self):
        sql = "SELECT * FROM %s;" % self.__table__
        results = []
        try:
            db.cursor.execute(sql)
            db.conn.commit()
        except Error:
            db.conn.rollback()
        results = db.cursor.fetchall()
        object_list = []
        if results:
            print("查询结果:")
            print(results)
            for result in results:
                object_list.append(type(self.__class__.__name__, (Model, dict), result))
        return object_list
