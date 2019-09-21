import typing

from dao import db,AnnotationEntity,LabelEntity,DatasetEntryEntity
from vo import AnnotaVO, LabelVO


class AnnotaDao:
    def __init__(self):
        pass

    @db.connection_context()
    def save(self, param: typing.Any):
        if isinstance(param, AnnotaVO):
            vo = param
            return AnnotationEntity.create(
                entry=vo.entry,
                label=vo.label,
                points=vo.points,
                kind=vo.kind
            )
        elif isinstance(param, list):
            with db.atomic():
                rows = [
                    (vo.entry,
                     vo.label,
                     vo.points,
                     vo.kind)
                    for vo in param]
                AnnotationEntity \
                    .insert_many(rows, fields= ["entry", "label", "points", "kind"]) \
                    .execute()

    @db.connection_context()
    def delete(self, entity_id: int):
        query = (AnnotationEntity
                 .delete()
                 .where(AnnotationEntity.entry == entity_id))
        query.execute()

    @db.connection_context()
    def fetch_all(self, entity_id: int):
        anns = AnnotationEntity.alias()
        lbls = LabelEntity.alias()
        query = (
            anns.select(
                anns.id.alias("annot_id"),
                anns.entry.alias("annot_entry"),
                anns.kind.alias("annot_kind"),
                anns.points.alias("annot_points"),
                lbls.id.alias("label_id"),
                lbls.name.alias("label_name"),
                lbls.color.alias("label_color")
            )
                .join(lbls, on=(anns.label == lbls.id), join_type="LEFT")
                .where(anns.entry == entity_id)
        )

        cursor = query.dicts().execute()
        result = []
        for row in cursor:
            annot = AnnotaVO()
            annot.id = row["annot_id"]
            annot.entry = row["annot_entry"]
            annot.kind = row["annot_kind"]
            annot.points = row["annot_points"]
            annot.label = None
            if row["label_id"]:
                label = LabelVO()
                label.id = row["label_id"]
                label.name = row["label_name"]
                label.color = row["label_color"]
                annot.label = label
            result.append(annot)

        return result

    @db.connection_context()
    def fetch_all_by_dataset(self,dataset_id: int = None):
        a=AnnotationEntity.alias("a")
        i = DatasetEntryEntity.alias("i")
        l=LabelEntity.alias("l")

        query=(
            a.select(
                i.file_path.alias("image"),
                a.kind.alias("annot_kind"),
                a.points.alias("annot_points"),
                l.name.alias("label_name"),
                l.color.alias("label_color")
            )
            .join(i, on=(a.entry == i.id))
            .join(l,on=(a.label == l.id),join_type="LEFT")
            .where(i.dataset == dataset_id)
        )
        cursor=query.dicts().execute()
        result=[]
        for row in cursor:
            result.append(row)
        return result
