import itertools

from cvstudio.dao import db, HubEntity, HubModelEntity, IntegrityError
from cvstudio.vo import HubVO, HubModelVO


class HubDao:
    def __init__(self):
        pass

    def _save(self, vo: HubVO):
        hub = HubEntity.create(
            path=vo.path,
            author=vo.author
        )
        id = hub.get_id()
        data = [(m.name, id) for m in vo.models]
        HubModelEntity \
            .insert_many(data,
                         fields=[HubModelEntity.name,
                                 HubModelEntity.hub]).execute()
        return id

    @db.atomic()
    def save(self, vo: HubVO):
        try:
            return self._save(vo)
        except IntegrityError as e:
            raise Exception("Repository already registered") from e

    @db.atomic()
    def delete(self, id: int):
        result = HubEntity.delete_by_id(id)
        return result

    @db.atomic()
    def update(self, vo):
        HubEntity.delete_by_id(vo.id)
        return self._save(vo)

    @db.connection_context()
    def fetch_all(self):
        h = HubEntity.alias()
        hm = HubModelEntity.alias()
        query = (hm.select(h.id.alias("repo_id"), h.path.alias("repo"), hm.name.alias("model_name")).join(h, on=(
                    hm.hub_id == h.id)))
        cursor = query.dicts().execute()
        rows = []
        groups = itertools.groupby(list(cursor), lambda row: (row["repo_id"], row["repo"]))
        for repo, models in groups:
            repo_id, repo_name = repo
            hub = HubVO()
            hub.id = repo_id
            hub.path = repo_name
            for model in models:
                model_hub = HubModelVO()
                model_hub.name = model["model_name"]
                hub.models.append(model_hub)
            rows.append(hub)
        return rows
