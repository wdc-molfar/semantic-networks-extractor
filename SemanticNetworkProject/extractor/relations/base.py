from abc import ABC, abstractclassmethod
from typing import Iterable, Set, NamedTuple
from ..phrases_resolver import PhrasesResolver
from ..settings import get_is_enhanced

class Relation(NamedTuple):
    source: str
    rel: str
    target: str

class AbstractRelationExtractor(ABC):
    """Extracts relations from dependencies."""
    @abstractclassmethod
    def extract(cls, sentence, edge, resolver: PhrasesResolver) -> Iterable[Relation]:
        pass

class RelationExtractor(AbstractRelationExtractor):
    """Extracts specific relations from dependencies."""
    _deps: Set[str]
    _enhanced_deps: Set[str]

    @classmethod
    def static_init(cls):
        if(not hasattr(cls, "_enhanced_deps")):
            cls._enhanced_deps = cls._deps
    
    @classmethod
    def _check(cls, sentence, edge, resolver: PhrasesResolver) -> bool:
        return edge.dep in cls._enhanced_deps if get_is_enhanced() else edge.dep in cls._deps

    @abstractclassmethod
    def _extract(cls, sentence, edge, resolver: PhrasesResolver) -> Iterable[Relation]:
        pass

    @classmethod
    def extract(cls, sentence, edge, resolver: PhrasesResolver) -> Iterable[Relation]:
        return cls._extract(sentence, edge, resolver) if cls._check(sentence, edge, resolver) else []

class SourceRelationExtractor(RelationExtractor):
    """Extracts specific relations from dependencies by source token."""
    _lemmas: Set[str]

    @classmethod
    def _check(cls, sentence, edge, resolver):
        if(not super()._check(sentence, edge, resolver)): return False
        source_token = sentence.token[edge.source-1]
        source_lemma = source_token.lemma
        return source_lemma in cls._lemmas
    
class DependencyRelationExtractor(RelationExtractor):
    """Extracts specific relations from dependencies by dependency type."""
    pass

#class TargetRelationExtractor(RelationExtractor):
#    """Extracts specific relations from dependencies by target token."""
#    pass

def check_dep_lemma(sentence, dep_dict, dep, lemma) -> bool:
    if(dep not in dep_dict): return False
    target_list = dep_dict[dep]
    for targetID in target_list:
        token = sentence.token[targetID]
        if(token.lemma == lemma): return True
    return False

class SpecialNmodDependencyRelationExtractor(DependencyRelationExtractor):
    """Extracts part_of relations from dependencies by nmod relations."""
    _rel: str
    _deps = {"nmod"}
    _invert_source_and_target = False
    _need_enhanced_checking = False
    _not_enhanced_dep = "case"
    _not_enhanced_lemma: str
    
    @classmethod
    def static_init(cls):
        super().static_init()
        if(cls._enhanced_deps != cls._deps):
            cls._need_enhanced_checking = True
            if(len(cls._enhanced_deps) != 1): raise Exception("Class can handle only 1 'nmod' dependency type!")
            cls._not_enhanced_lemma = next(iter(cls._enhanced_deps)).rpartition(':')[2]

    @classmethod
    def _extract(cls, sentence, edge, resolver):
        if(cls._need_enhanced_checking and not get_is_enhanced()):
            dep_dict = resolver.source_edges_dict[edge.target-1]
            if(not check_dep_lemma(sentence, dep_dict, cls._not_enhanced_dep, cls._not_enhanced_lemma)): return []
         
        rels = set()   
        if(cls._invert_source_and_target):
            rel_sources = resolver.get_resolved_phrases(sentence, edge.target-1)
            rel_targets = resolver.get_resolved_phrases(sentence, edge.source-1)
        else:
            rel_sources = resolver.get_resolved_phrases(sentence, edge.source-1)
            rel_targets = resolver.get_resolved_phrases(sentence, edge.target-1)

        for rel_source in rel_sources:
            for rel_target in rel_targets:
                rels.add(Relation(rel_source, cls._rel, rel_target))
        return rels