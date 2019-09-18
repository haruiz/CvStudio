from datetime import  datetime

import typing

from dao import db,AnnotationEntity
from vo import  AnnotaVO
from peewee import *

class AnnotaDao:
    def __init__(self):
        pass

    @db.connection_context()
    def save(self,param: typing.Any):
        if isinstance(param,AnnotaVO):
            vo = param
            return AnnotationEntity.create(
                entry=vo.entry,
                label=vo.label,
                points=vo.points,
                kind=vo.kind
            )
        elif isinstance(param,list):
            with db.atomic():
                rows=[
                    (vo.entry,
                     vo.label,
                     vo.points,
                     vo.kind)
                    for vo in param]
                AnnotationEntity \
                    .insert_many(rows, fields=
                        ["entry",
                         "label",
                         "points",
                         "kind"]).execute()

    @db.connection_context()
    def delete(self, entity_id: int):
        query =(AnnotationEntity
                .delete()
                .where(AnnotationEntity.entry == entity_id))
        query.execute()

    @db.connection_context()
    def fetch_all(self,entity_id: int):
        query=(AnnotationEntity
               .select()
               .where(AnnotationEntity.entry == entity_id))
        cursor = query.dicts().execute()
        result=[]
        for ds in list(cursor):
            vo=AnnotaVO()
            result.append(vo)
            for k,v in ds.items():
                setattr(vo,k,v)
        return result


