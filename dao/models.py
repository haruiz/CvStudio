from peewee import *

db = SqliteDatabase("studio.db", pragmas={
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
    data_type = CharField(default="Images")

    class Meta:
        table_name = 'dataset'


class DatasetEntryEntity(BaseModel):
    file_path = CharField()
    file_size = CharField()
    dataset = ForeignKeyField(DatasetEntity, on_delete="CASCADE")

    class Meta:
        indexes = (
            (("file_path", "dataset"), True),
        )
        table_name = 'media'


class LabelEntity(BaseModel):
    name = CharField()
    description = CharField(null=True)
    color = CharField(null=None)
    dataset = ForeignKeyField(DatasetEntity, on_delete="CASCADE")

    class Meta:
        table_name = 'label'


class HubEntity(BaseModel):
    path = CharField(unique=True)
    author = CharField(null=True)

    class Meta:
        table_name = 'hub'


class HubModelEntity(BaseModel):
    name = CharField(unique=True)
    description = CharField(null=True)
    hub = ForeignKeyField(HubEntity)

    class Meta:
        table_name = 'hub_model'


class AnnotationEntity(BaseModel):
    entry = ForeignKeyField(DatasetEntryEntity, on_delete="CASCADE")
    label = ForeignKeyField(LabelEntity, null=True, on_delete="CASCADE")
    points = CharField()
    kind = CharField()

    class Meta:
        table_name = "annotation"


def create_tables():
    with db:
        models = [
            DatasetEntity,
            HubEntity,
            HubModelEntity,
            DatasetEntryEntity,
            LabelEntity,
            AnnotationEntity
        ]
        # db.drop_tables(models)
        db.create_tables(models)
        db.execute_sql("PRAGMA foreign_keys=ON")
