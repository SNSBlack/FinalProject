from peewee import *

db = SqliteDatabase("table.db")

class Person(Model):
    id = IPField()
    username = CharField()
    time = CharField()
    day = CharField()
    discipline = CharField()

    class Meta:
        database = db

Person.create_table()