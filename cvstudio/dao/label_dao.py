from cvstudio.dao import db, LabelEntity, DatasetEntryEntity
from cvstudio.vo import LabelVO


class LabelDao:
    def __init__(self):
        pass

    @db.atomic()
    def save(self, vo: LabelVO):
        label = LabelEntity.create(
            name=vo.name.title(), color=vo.color, dataset=vo.dataset
        )
        vo.id = label.get_id()
        return vo

    @db.connection_context()
    def fetch_all(self, ds_id):
        cursor = (
            LabelEntity.select().where(LabelEntity.dataset == ds_id).dicts().execute()
        )
        result = []
        for ds in list(cursor):
            vo = LabelVO()
            result.append(vo)
            for k, v in ds.items():
                setattr(vo, k, v)
        return result

    @db.connection_context()
    def find_by_name(self, ds_id, label_name):
        query = LabelEntity.select().where(
            (LabelEntity.dataset == ds_id) & (LabelEntity.name == label_name)
        )
        # print(query)
        cursor = query.dicts().execute()
        result = list(cursor)
        vo = LabelVO()
        if len(result) > 0:
            row = result[0]
            for k, v in row.items():
                setattr(vo, k, v)
            return vo
        return None

    @db.atomic()
    def delete(self, id: int):
        result = LabelEntity.delete_by_id(id)
        DatasetEntryEntity.update(label=None).where(
            DatasetEntryEntity.label == id
        ).execute()
        return result
