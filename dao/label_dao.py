from dao import db,LabelEntity,DatasetEntryEntity
from vo import LabelVO


class LabelDao:
    def __init__(self):
        pass

    @db.atomic()
    def save(self, vo: LabelVO):
        label = LabelEntity.create(
            name=vo.name,
            color=vo.color,
            dataset=vo.dataset
        )
        vo.id = label.get_id()

        return vo

    @db.connection_context()
    def fetch_all(self, ds_id):
        cursor = LabelEntity.select().where(LabelEntity.dataset == ds_id).dicts().execute()
        result = []
        for ds in list(cursor):
            vo = LabelVO()
            result.append(vo)
            for k, v in ds.items():
                setattr(vo, k, v)

        return result

    @db.atomic()
    def delete(self, id: int):
        result = LabelEntity.delete_by_id(id)
        DatasetEntryEntity.update(label=None).where(DatasetEntryEntity.label == id).execute()
        return result
