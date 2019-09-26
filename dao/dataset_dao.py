from peewee import *

from datetime import datetime
from dao import db, DatasetEntity, DatasetEntryEntity
from util import MiscUtilities
from vo import DatasetVO,DatasetEntryVO,LabelVO


class DatasetDao:
    def __init__(self):
        pass

    @db.connection_context()
    def save(self, vo: DatasetVO):
        try:
            if vo.id is None:
                now = datetime.now()
                ds = DatasetEntity.create(
                    name=vo.name,
                    folder=vo.folder,
                    description=vo.description,
                    data_type=vo.data_type,
                    date=now.isoformat()
                )
                vo.id = ds.get_id()
            else:
                ds = DatasetEntity.get_by_id(vo.id)
                if ds:
                    ds.name = vo.name
                    ds.description = vo.description
                    ds.save()
        except IntegrityError as e:
            print(e)

    @db.connection_context()
    def fetch_all(self):
        cursor = DatasetEntity.select().dicts().execute()
        result = []
        for ds in list(cursor):
            vo = DatasetVO()
            result.append(vo)
            for k, v in ds.items():
                setattr(vo, k, v)

        return result

    @db.connection_context()
    def delete(self, id: int):
        results = DatasetEntity.delete_by_id(id)

        return results

    @db.atomic()
    def tag_entries(self, entries: [DatasetEntryVO], label: LabelVO):
        ids = [vo.id for vo in entries]
        for chunk in MiscUtilities.chunk(ids, 100):
            rows=(DatasetEntryEntity
                        .update(label = label.id)
                            .where(DatasetEntryEntity.id.in_(list(chunk))).execute())

    @db.atomic()
    def add_entries(self, entries: [DatasetEntryVO]):
        try:
            entries = [vo.to_array() for vo in entries]
            for batch in chunked(entries, 100):
                DatasetEntryEntity.insert_many(batch).execute()
        except IntegrityError as ex:
            raise Exception("one or more files have already been loaded into this dataset")

    @db.connection_context()
    def delete_entry(self, id):
        return DatasetEntryEntity.delete_by_id(id)

    @db.connection_context()
    def fetch_all_with_size(self):
        ds = DatasetEntity.alias("ds")
        m = DatasetEntryEntity.alias("m")
        query = (
            ds.select(
                ds.id,
                ds.name,
                ds.data_type,
                fn.SUM(m.file_size).alias("size")
            ).join(
                m,
                JOIN.LEFT_OUTER,
                on=ds.id == m.dataset_id
            ).group_by(ds.id)
        )
        query_results = list(query.dicts().execute())
        result = []
        for ds in query_results:
            vo = DatasetVO()
            result.append(vo)
            for k, v in ds.items():
                setattr(vo, k, v)

        return result

    @db.connection_context()
    def fetch_entries(self, ds_id):
        query = DatasetEntryEntity \
            .select() \
            .where(DatasetEntryEntity.dataset == ds_id)
        cursor = query.dicts().execute()
        result = []
        for ds in list(cursor):
            vo = DatasetEntryVO()
            result.append(vo)
            for k, v in ds.items():
                setattr(vo, k, v)

        return result
