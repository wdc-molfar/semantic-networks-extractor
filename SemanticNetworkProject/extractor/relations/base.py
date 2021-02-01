from abc import ABC, abstractclassmethod
from typing import Iterable, Set, NamedTuple
from ..phrases_resolver import PhrasesResolver, check_word_negation
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

class SpecialRootWithCaseSourceRelationExtractor(SourceRelationExtractor):
    """Extracts relations from dependencies by source token with case."""
    _rel: str
    _second_dep: str
    _enhanced_second_dep: str
    _case: str
    _invert_source_and_target = False
    
    @classmethod
    def static_init(cls):
        super().static_init()
        cls._enhanced_second_dep = f"{cls._second_dep}:{cls._case}"
    
    @classmethod
    def _extract(cls, sentence, edge, resolver):
        if(check_word_negation(sentence, edge.source-1, resolver.source_edges_dict)): return []
        dep_dict = resolver.source_edges_dict[edge.source-1]
        if(get_is_enhanced()):
            if(cls._enhanced_second_dep not in dep_dict): return []
            obj_list = dep_dict[cls._enhanced_second_dep]
        else:
            if(cls._second_dep not in dep_dict): return []
            obj_list = dep_dict[cls._second_dep]
            has_of = False
            for obj_tokenID in obj_list:
                if(obj_tokenID not in resolver.source_edges_dict): continue
                obj_dep_dict = resolver.source_edges_dict[obj_tokenID]
                if(check_dep_lemma(sentence, obj_dep_dict, "case", cls._case)): break
            else: return []
            
        rels = set()
        rel_targets = resolver.get_resolved_phrases(sentence, edge.target-1)
        for rel_sourceID in obj_list:
            rel_sources = resolver.get_resolved_phrases(sentence, rel_sourceID)
            for rel_target in rel_targets:
                for rel_source in rel_sources:
                    if(cls._invert_source_and_target):
                        rels.add(Relation(rel_target, cls._rel, rel_source))
                    else:
                        rels.add(Relation(rel_source, cls._rel, rel_target))
        return rels

class SpecialNmodDependencyRelationExtractor(DependencyRelationExtractor):
    """Extracts relations from dependencies by nmod relations."""
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