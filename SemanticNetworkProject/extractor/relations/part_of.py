from . import base
from .. import phrases_resolver
from ..settings import get_is_enhanced

_rel = "part_of"

class RootPartOfSourceRelationExtractor(base.SpecialRootSourceRelationExtractor):
    """Extracts part_of relations from dependencies by source token."""
    _rel = _rel
    _deps = {"nsubj"}
    _lemmas = {"have", "contain", "include"}
    _second_dep = "obj"

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

class DivideIntoPartOfSourceRelationExtractor(base.SpecialRootWithCaseSourceRelationExtractor):
    """Extracts part_of relations from dependencies by divide into root."""
    _rel = _rel
    _deps = {"obj"}
    _lemmas = {"divide", "partition", "cut", "break", "chop"}
    _second_dep = "obl"
    _case = "into"

class DivideToPartOfSourceRelationExtractor(base.SpecialRootWithCaseSourceRelationExtractor):#Is it used?
    """Extracts part_of relations from dependencies by divide to root."""
    _rel = _rel
    _deps = {"obj"}
    _lemmas = {"divide", "partition", "cut", "break", "chop"}
    _second_dep = "obl"
    _case = "to"

class DividedIntoPartOfSourceRelationExtractor(base.SpecialRootWithCaseSourceRelationExtractor):
    """Extracts part_of relations from dependencies by divided into root."""
    _rel = _rel
    _deps = {"nsubj:pass"}
    _lemmas = {"divide", "partition", "cut", "break", "chop"}
    _second_dep = "obl"
    _case = "into"

class DividedToPartOfSourceRelationExtractor(base.SpecialRootWithCaseSourceRelationExtractor):
    """Extracts part_of relations from dependencies by divided to root."""
    _rel = _rel
    _deps = {"nsubj:pass"}
    _lemmas = {"divide", "partition", "cut", "break", "chop"}
    _second_dep = "obl"
    _case = "to"

class NmodOfPartOfDependencyRelationExtractor(base.SpecialNmodDependencyRelationExtractor):
    """Extracts part_of relations from dependencies by nmod:of relation."""
    _rel = _rel
    _enhanced_deps = {"nmod:of"}
    _inverse_source_lemmas = {"family", "arrangement", "group", "operation", "property", "set", "union",
                                "intersection", "use", "combination", "aggregation", "sum", "function"}
    
    @classmethod
    def _extract(cls, sentence, edge, resolver):
        rels = super()._extract(sentence, edge, resolver)
        if(sentence.token[edge.source-1].lemma in cls._inverse_source_lemmas):
            inversed_rels = set()
            for rel in rels: inversed_rels.add(base.Relation(rel.target, rel.rel, rel.source))
            return inversed_rels
        else: return rels        

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
