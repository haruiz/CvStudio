import typing

from dao import db, AnnotationEntity, LabelEntity, DatasetEntryEntity
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
                    .insert_many(rows, fields=["entry", "label", "points", "kind"]) \
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
        lbl = LabelEntity.alias()
        query = (
            anns.select(
                anns.id.alias("annot_id"),
                anns.entry.alias("annot_entry"),
                anns.kind.alias("annot_kind"),
                anns.points.alias("annot_points"),
                lbl.id.alias("label_id"),
                lbl.name.alias("label_name"),
                lbl.color.alias("label_color")
            )
                .join(lbl, on=(anns.label == lbl.id), join_type="LEFT")
                .where(anns.entry == entity_id)
        )

        cursor = query.dicts().execute()
        result = []
        for row in cursor:
            ann_vo = AnnotaVO()
            ann_vo.id = row["annot_id"]
            ann_vo.entry = row["annot_entry"]
            ann_vo.kind = row["annot_kind"]
            ann_vo.points = row["annot_points"]
            ann_vo.label = None
            if row["label_id"]:
                label = LabelVO()
                label.id = row["label_id"]
                label.name = row["label_name"]
                label.color = row["label_color"]
                ann_vo.label = label
            result.append(ann_vo)

        return result

    @db.connection_context()
    def fetch_all_by_dataset(self, dataset_id: int = None):
        ann = AnnotationEntity.alias("a")
        ds_entry = DatasetEntryEntity.alias("i")
        lbl = LabelEntity.alias("l")

        query = (
            ann.select(
                ds_entry.file_path.alias("image"),
                ann.kind.alias("annot_kind"),
                ann.points.alias("annot_points"),
                lbl.name.alias("label_name"),
                lbl.color.alias("label_color")
            )
                .join(ds_entry, on=(ann.entry == ds_entry.id))
                .join(lbl, on=(ann.label == lbl.id), join_type="LEFT")
                .where(ds_entry.dataset == dataset_id)
        )
        cursor = query.dicts().execute()
        result = []
        for row in cursor:
            result.append(row)

        return result
