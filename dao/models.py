from peewee import *

db = SqliteDatabase("studio.db",pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,  # 64MB
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 0})


class BaseModel(Model):
    class Meta:
        database = db

class DatasetEntity(BaseModel):
    name = CharField()
    description = TextField()
    folder = TextField()
    date = DateField()
    data_type = CharField()


def create_tables():
    with db:
        db.create_tables([DatasetEntity])
