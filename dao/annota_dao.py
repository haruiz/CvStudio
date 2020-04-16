import typing

from peewee import *

from dao import db, AnnotationEntity, LabelEntity, DatasetEntryEntity
from vo import AnnotaVO, LabelVO


class AnnotaDao:
    def __init__(self):
        pass

    @db.connection_context()
    def save(self, entity_id, entry: typing.Any):
        if isinstance(entry, AnnotaVO):
            vo = entry
            return AnnotationEntity.create(
                entry=vo.entry,
                label=vo.label,
                points=vo.points,
                kind=vo.kind
            )
        elif isinstance(entry, list):
            with db.atomic():
                query = (AnnotationEntity
                         .delete()
                         .where(AnnotationEntity.entry == entity_id))
                query.execute()
                rows = [
                    (vo.entry,
                     vo.label,
                     vo.points,
                     vo.kind)
                    for vo in entry]
                # AnnotationEntity \
                #     .insert_many(rows, fields=["entry", "label", "points", "kind"]) \
                #     .execute()
                for batch in chunked(rows, 100):
                    AnnotationEntity \
                        .insert_many(batch, fields=["entry", "label", "points", "kind"]) \
                        .execute()

    @db.connection_context()
    def delete(self, entity_id: int):
        query = (AnnotationEntity
                 .delete()
                 .where(AnnotationEntity.entry == entity_id))
        return query.execute()

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
                .join(lbl, on=(anns.label == lbl.id), join_type=JOIN.LEFT_OUTER)
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
    def get_label(self, entity_id: int):
        dse = DatasetEntryEntity.alias()
        lbl = LabelEntity.alias()
        query = (
            dse
                .select(lbl.name)
                .join(lbl, on=(dse.label == lbl.id))
                .where(dse.id == entity_id)
        )
        result = list(query.dicts().execute())
        return result[0]["name"] if len(result) > 0 else None

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
                .join(lbl, on=(ann.label == lbl.id), join_type=JOIN.LEFT_OUTER)
                .where(ds_entry.dataset == dataset_id)
        )
        cursor = query.dicts().execute()
        result = []
        for row in cursor:
            result.append(row)

        return result

    @db.connection_context()
    def fetch_boxes(self, dataset_id: int = None):
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
                .join(lbl, on=(ann.label == lbl.id), join_type=JOIN.LEFT_OUTER)
                .where((ann.label.is_null(False)) & (ds_entry.dataset == dataset_id) & (ann.kind == "box"))
        )
        cursor = query.dicts().execute()
        result = []
        for row in cursor:
            result.append(row)
        return result

    @db.connection_context()
    def fetch_polygons(self, dataset_id: int = None):
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
                .join(lbl, on=(ann.label == lbl.id), join_type=JOIN.LEFT_OUTER)
                .where((ann.label.is_null(False)) & (ds_entry.dataset == dataset_id) & (ann.kind == "polygon"))
        )
        cursor = query.dicts().execute()
        result = []
        for row in cursor:
            result.append(row)
        return result


    @db.connection_context()
    def fetch_labels(self, dataset_id: int = None):
        e = DatasetEntryEntity.alias("e")
        l = LabelEntity.alias("l")
        query = (
            e.select(
                e.file_path.alias("image"),
                l.name.alias("label")
            )
            .join(l, on=(e.label == l.id))
            .where((e.dataset_id == dataset_id) & (e.label.is_null(False)))
        )
        cursor = query.dicts().execute()
        result = []
        for row in cursor:
            result.append(row)

        return result
