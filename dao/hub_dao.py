import itertools

from dao import db,HubEntity,HubModelEntity, IntegrityError
from vo import HubVO,HubModelVO


class HubDao:
    def __init__(self):
        pass

    @db.atomic()
    def save(self, vo: HubVO):
        hub =HubEntity.create(
            path=vo.path,
            author=vo.author
        )
        id =hub.get_id()
        data = [(m.name, id) for m in vo.models]
        HubModelEntity\
        .insert_many(data,
         fields=[HubModelEntity.name,
                 HubModelEntity.hub]).execute()
        return id

    @db.connection_context()
    def fetch_all(self):
        h = HubEntity.alias()
        hm = HubModelEntity.alias()
        query = (hm.select(h.path.alias("repo"), hm.name.alias("model_name")).join(h, on=(hm.hub_id == h.id)))
        cursor = query.dicts().execute()
        groups = itertools.groupby(list(cursor), lambda row: row["repo"])
        rows = []
        for key, values in groups:
            hub = HubVO()
            hub.path = key
            for val in values:
                model_hub = HubModelVO()
                model_hub.name = val["model_name"]
                hub.models.append(model_hub)
            rows.append(hub)
        return rows


