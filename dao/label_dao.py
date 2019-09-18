import itertools

from dao import db,HubEntity,HubModelEntity,IntegrityError,LabelEntity
from vo import LabelVo


class LabelDao:
    def __init__(self):
        pass

    @db.atomic()
    def save(self, vo: LabelVo):
        label = LabelEntity.create(
            name=vo.name,
            color=vo.color,
            dataset=vo.dataset
        )
        return label

    @db.connection_context()
    def fetch_all(self, ds_id):
        cursor=LabelEntity.select().where(LabelEntity.dataset == ds_id).dicts().execute()
        result=[]
        for ds in list(cursor):
            vo=LabelVo()
            result.append(vo)
            for k,v in ds.items():
                setattr(vo,k,v)
        return result

    @db.connection_context()
    def delete(self, id: int):
        results=LabelEntity.delete_by_id(id)
        return results



