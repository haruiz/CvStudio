from datetime import datetime

from peewee import IntegrityError, fn, JOIN, chunked

from cvstudio.dao import DatasetEntity, DatasetEntryEntity, db
from cvstudio.vo import DatasetVO, DatasetEntryVO


class DatasetDao:
    def __init__(self):
        super(DatasetDao, self).__init__()

    @db.connection_context()
    def save(self, vo: DatasetVO):
        try:
            if vo.id is None:
                now = datetime.now()
                ds = DatasetEntity.create(
                    name=vo.name,
                    description=vo.description,
                    date=now.isoformat(),
                )
                vo.id = ds.get_id()
            else:
                ds = DatasetEntity.get_by_id(vo.id)
                if ds:
                    ds.name = vo.name
                    ds.description = vo.description
                    ds.save()
        except IntegrityError as ex:
            raise ex

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
    def count(self):
        return DatasetEntity.select().count()

    @db.connection_context()
    def fetch_all_by_id(self, ds_id):
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

    @db.connection_context()
    def fetch_all_with_size(self, page_number, items_per_page):
        ds = DatasetEntity.alias("ds")
        m = DatasetEntryEntity.alias("m")
        query = (
            ds.select(
                ds.id,
                ds.name,
                fn.SUM(m.file_size).alias("size"),
                fn.COUNT(ds.id).alias("count"),
            )
            .join(m, JOIN.LEFT_OUTER, on=ds.id == m.dataset_id)
            .group_by(ds.id)
            .order_by(ds.id)
            .paginate(page_number, items_per_page)
                .dicts()
        )
        query_results = query.execute()
        result = []
        for ds in query_results:
            vo = DatasetVO()
            result.append(vo)
            for k, v in ds.items():
                setattr(vo, k, v)
        return result

    @db.connection_context()
    def delete(self, ds_id: int):
        result = DatasetEntity.delete_by_id(ds_id)
        return result

    # files methods
    @db.connection_context()
    def add_files(self, entries: [DatasetEntryVO]):
        try:
            entries = [vo.to_array() for vo in entries]
            for batch in chunked(entries, 100):
                DatasetEntryEntity.insert_many(batch).execute()
        except IntegrityError as ex:
            raise Exception(
                f"one or more files have already been loaded into this dataset: {ex}"
            )

    @db.connection_context()
    def count_files(self, dataset_id):
        return (
            DatasetEntryEntity.select()
            .where(DatasetEntryEntity.dataset == dataset_id)
            .count()
        )

    @db.connection_context()
    def fetch_files_by_page(self, dataset_id, page_number, items_per_page):
        query = (
            DatasetEntryEntity.select()
            .where(DatasetEntryEntity.dataset == dataset_id)
            .order_by(DatasetEntryEntity.id)
            .paginate(page_number, items_per_page)
            .dicts()
        )
        query_results = query.execute()
        result = []
        for ds in list(query_results):
            vo = DatasetEntryVO()
            result.append(vo)
            for k, v in ds.items():
                setattr(vo, k, v)
        return result

    @db.connection_context()
    def fetch_all_files(self, ds_id):
        query = (
            DatasetEntryEntity
            .select()
            .where(DatasetEntryEntity.dataset == ds_id)
            .dicts()
        )
        cursor = query.execute()
        result = []
        for ds in list(cursor):
            vo = DatasetEntryVO()
            result.append(vo)
            for k, v in ds.items():
                setattr(vo, k, v)
        return result

    @db.connection_context()
    def delete_file(self, entry_id):
        return DatasetEntryEntity.delete_by_id(entry_id)

