from datetime import  datetime
from dao import db,DatasetEntity,IntegrityError
from vo import DatasetVO

class DatasetDao():
    def __init__(self):
        pass

    @db.connection_context()
    def save(self, vo: DatasetVO):
        try:
            now=datetime.now()
            ds = DatasetEntity.create(
                name = vo.name,
                folder= vo.folder,
                description= vo.description,
                data_type = vo.data_type,
                date=now.isoformat()
            )
            vo.id = ds.get_id()
        except IntegrityError as e:
            print(e)

    @db.connection_context()
    def fetch_all(self):
        try:
            results = DatasetEntity.select().dicts().execute()
            datasets = []
            for ds in list(results):
                vo=DatasetVO()
                datasets.append(vo)
                for k,v in ds.items():
                    setattr(vo,k,v)
            return datasets
        except Exception as e:
            print(e)

    @db.connection_context()
    def delete(self, id: int):
        try:
            results=DatasetEntity.delete_by_id(id)
            return results
        except Exception as e:
            print(e)
