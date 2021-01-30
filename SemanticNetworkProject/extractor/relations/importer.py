from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
from inspect import isclass, isabstract
from typing import Iterable
from . import base

class RelationsExtractors(base.AbstractRelationExtractor):
    """Extracts presetted relations from dependencies."""
    _extractors: Iterable[base.RelationExtractor]

    @classmethod
    def _get_extractors_from_module_name(cls, module_name: str):
        module = import_module(f"{__name__.rpartition('.')[0]}.{module_name}")
        extractors = []
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if(isclass(attribute) and issubclass(attribute, base.RelationExtractor) and not isabstract(attribute)):
                extractors.append(attribute)
        return extractors

    @classmethod
    def use_all_relations(cls):
        cls._extractors = []
        package_dir = Path(__file__).resolve().parent
        for (_, module_name, _) in iter_modules([package_dir]):
            if(module_name == __name__.rpartition('.')[2] or module_name == base.__name__.rpartition('.')[2]): continue
            cls._extractors.extend(cls._get_extractors_from_module_name(module_name))

    @classmethod
    def use_relations(cls, module_names: Iterable[str]):
        cls._extractors = []
        for module_name in module_names:
            cls._extractors.extend(cls._get_extractors_from_module_name(module_name))

    @classmethod
    def extract(cls, sentence, edge, resolver: base.PhrasesResolver) -> Iterable[base.Relation]:
        rels = set()
        for extractor in cls._extractors:
            rels.update(extractor.extract(sentence, edge, resolver))
        return rels