from meta_class import *


# 为了方便对类进行修改，在类的开头和结尾使用特殊注释，不要修改这些注释和它们的位置


# start
class Statistics(Model):
    __table__ = "statistics"
    id = IntegerField(name="id", null=False, primary=True, auto_increment=True)
    class_id = IntegerField(name="class_id", null=False, )
    average = DoubleField(name="average", null=False, )
    rank = IntegerField(name="rank", null=False, )
    name = StringField(name="name", null=False, )
# end


# start
class StudentData(Model):
    __table__ = "student_data"
    id = IntegerField(name="id", null=False, primary=True, auto_increment=True)
    age = IntegerField(name="age", null=False, )
# end


student1 = StudentData(id=1, age=18)
student1.save()
student2 = StudentData(id=2, age=19)
student2.save()
print(type(student2))
print(student1.id, student1.age)
student3 = student2.get_by_id(2)
print(student3)
print(student3.id, student3.age)
# student3.save()
record_list = student2.get_all()
print(record_list)
