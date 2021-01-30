from abc import ABC, abstractclassmethod
from typing import Iterable, Set, NamedTuple
from ..phrases_resolver import PhrasesResolver

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

    @abstractclassmethod
    def _check(cls, sentence, edge, resolver: PhrasesResolver) -> bool:
        return edge.dep in cls._deps

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
    
#class DependencyRelationExtractor(RelationExtractor):
#    """Extracts specific relations from dependencies by dependency type."""
#    pass

#class TargetRelationExtractor(RelationExtractor):
#    """Extracts specific relations from dependencies by target token."""
#    pass