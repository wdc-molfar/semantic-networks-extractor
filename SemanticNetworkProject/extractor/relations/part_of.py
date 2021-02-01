from . import base
from .. import phrases_resolver
from ..settings import get_is_enhanced

_rel = "part_of"

class RootPartOfSourceRelationExtractor(base.SourceRelationExtractor):
    """Extracts part_of relations from dependencies by source token."""
    _deps = {"nsubj"}
    _lemmas = {"have", "contain", "include"}
    
    @classmethod
    def _extract(cls, sentence, edge, resolver):
        if(phrases_resolver.check_word_negation(sentence, edge.source-1, resolver.source_edges_dict)): return []
        dep_dict = resolver.source_edges_dict[edge.source-1]
        if("obj" not in dep_dict): return []
        obj_list = dep_dict["obj"]
        rel_targets = resolver.get_resolved_phrases(sentence, edge.target-1)
        rels = set()
        for rel_sourceID in obj_list:
            rel_sources = resolver.get_resolved_phrases(sentence, rel_sourceID)
            for rel_target in rel_targets:
                for rel_source in rel_sources:
                    rels.add(base.Relation(rel_source, _rel, rel_target))
        return rels

class ConsistOfPartOfSourceRelationExtractor(base.SpecialRootWithCaseSourceRelationExtractor):
    """Extracts part_of relations from dependencies by consist of root."""
    _rel = _rel
    _deps = {"nsubj"}
    _lemmas = {"consist"}
    _second_dep = "obl"
    _case = "of"

class MadeOfPassivePartOfSourceRelationExtractor(base.SpecialRootWithCaseSourceRelationExtractor):
    """Extracts part_of relations from dependencies by made of root."""
    _rel = _rel
    _deps = {"nsubj:pass"}
    _lemmas = {"make"}
    _second_dep = "obl"
    _case = "of"

class UsedWithinPartOfSourceRelationExtractor(base.SpecialRootWithCaseSourceRelationExtractor):
    """Extracts part_of relations from dependencies by used within root."""
    _rel = _rel
    _deps = {"nsubj"}
    _lemmas = {"use"}
    _second_dep = "obl"
    _case = "within"
    _invert_source_and_target = True

class NmodOfPartOfDependencyRelationExtractor(base.SpecialNmodDependencyRelationExtractor):
    """Extracts part_of relations from dependencies by nmod:of relation."""
    _rel = _rel
    _enhanced_deps = {"nmod:of"}
    _blacklist_source_lemmas = {"family", "arrangement", "group", "operation", "property", "set", "union",
                                "intersection", "use", "combination", "aggregation", "sum", "function"}
    
    @classmethod
    def _extract(cls, sentence, edge, resolver):
        if(sentence.token[edge.source-1].lemma in cls._blacklist_source_lemmas): return []
        return super()._extract(sentence, edge, resolver)

class NmodPossPartOfDependencyRelationExtractor(base.SpecialNmodDependencyRelationExtractor):
    """Extracts part_of relations from dependencies by nmod:poss relation."""
    _rel = _rel
    _deps = {"nmod:poss"}

class NmodWithPartOfDependencyRelationExtractor(base.SpecialNmodDependencyRelationExtractor):
    """Extracts part_of relations from dependencies by nmod:with relation."""
    _rel = _rel
    _enhanced_deps = {"nmod:with"}
    _invert_source_and_target = True

class NmodWithinPartOfDependencyRelationExtractor(base.SpecialNmodDependencyRelationExtractor):
    """Extracts part_of relations from dependencies by nmod:within relation."""
    _rel = _rel
    _enhanced_deps = {"nmod:within"}

class NmodInPartOfDependencyRelationExtractor(base.SpecialNmodDependencyRelationExtractor):
    """Extracts part_of relations from dependencies by nmod:in relation."""
    _rel = _rel
    _enhanced_deps = {"nmod:in"}

