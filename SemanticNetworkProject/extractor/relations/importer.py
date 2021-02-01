from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
from inspect import isclass, isabstract
from typing import Iterable, Dict
from . import base
from ..settings import get_is_enhanced

class RelationsExtractors(base.AbstractRelationExtractor):
    """Extracts presetted relations from dependencies."""
    _extractors: Dict[str, Iterable[base.RelationExtractor]]
    _enhanced_extractors: Dict[str, Iterable[base.RelationExtractor]]

    @classmethod
    def _get_extractors_from_module_name(cls, module_name: str) -> Iterable[base.RelationExtractor]:
        module = import_module(f"{__name__.rpartition('.')[0]}.{module_name}")
        extractors = []
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if(isclass(attribute) and issubclass(attribute, base.RelationExtractor) and not isabstract(attribute)):
                attribute.static_init()
                extractors.append(attribute)
        return extractors
    
    @classmethod
    def _fill_extractors_from_module_name(cls, module_name: str):
        new_extractors = cls._get_extractors_from_module_name(module_name)
        for extractor in new_extractors:
            for dep in extractor._deps:
                cls._extractors.setdefault(dep, set()).add(extractor)
            for enhanced_dep in extractor._enhanced_deps:
                cls._enhanced_extractors.setdefault(enhanced_dep, set()).add(extractor)

    @classmethod
    def use_all_relations(cls):
        cls._extractors = dict()
        cls._enhanced_extractors = dict()
        package_dir = Path(__file__).resolve().parent
        for (_, module_name, _) in iter_modules([package_dir]):
            if(module_name == __name__.rpartition('.')[2] or module_name == base.__name__.rpartition('.')[2]): continue
            cls._fill_extractors_from_module_name(module_name)

    @classmethod
    def use_relations(cls, module_names: Iterable[str]):
        cls._extractors = dict()
        cls._enhanced_extractors = dict()
        for module_name in module_names:
            cls._fill_extractors_from_module_name(module_name)

    @classmethod
    def extract(cls, sentence, edge, resolver: base.PhrasesResolver) -> Iterable[base.Relation]:
        rels = set()
        extractors_dict = cls._enhanced_extractors if get_is_enhanced() else cls._extractors
        if(edge.dep in extractors_dict):
            extractors = extractors_dict[edge.dep]
            for extractor in extractors:
                rels.update(extractor.extract(sentence, edge, resolver))
        return rels