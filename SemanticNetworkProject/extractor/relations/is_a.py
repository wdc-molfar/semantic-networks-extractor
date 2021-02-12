from . import base
from .. import phrases_resolver
from ..settings import get_is_enhanced

_rel = "is_a"

class RootIsASourceRelationExtractor(base.SpecialRootSourceRelationExtractor):
    """Extracts is_a relations from dependencies by source token."""
    _rel = _rel
    _deps = {"nsubj:pass"}
    _lemmas = {"call", "name"}
    _second_dep = "obj"

#class NounsNmodIsADependencyRelationExtractor(base.DependencyRelationExtractor):
#    """Extracts is_a relations from dependencies by nsubj dependency."""
#    _deps = {"nsubj"}

#    @classmethod
#    def _check(cls, sentence, edge, resolver) -> bool:
#        if(not super()._check(sentence, edge, resolver)): return False
#        return sentence.token[edge.source-1].pos.startswith("NN") and sentence.token[edge.target-1].pos.startswith("NN")

#    @classmethod
#    def _extract(cls, sentence, edge, resolver):
#        rels = set()
#        #invert
#        rel_sources = resolver.get_resolved_phrases(sentence, edge.target-1)
#        rel_targets = resolver.get_resolved_phrases(sentence, edge.source-1)
#        for rel_source in rel_sources:
#            for rel_target in rel_targets:
#                rels.add(base.Relation(rel_source, _rel, rel_target))
#        return rels