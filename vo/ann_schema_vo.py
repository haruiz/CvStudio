from pprint import pprint
from typing import List

from schemas import AnnotationScheme
from vo import AnnotaVO


class AnnotationSchemaVO:
    def __init__(self, image: str, annotations: List[AnnotaVO]):
        self.image = image
        self.anns = annotations

    def dump(self):
        ann_scheme = AnnotationScheme()
        result = ann_scheme.dump(self.__dict__)
        pprint(result, indent=2)
