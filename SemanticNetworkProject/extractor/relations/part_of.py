from . import base
from .. import phrases_resolver
from ..settings import get_is_enhanced

_rel = "part_of"

def _check_dep_lemma(sentence, dep_dict, dep, lemma) -> bool:
    if(dep not in dep_dict): return False
    target_list = dep_dict[dep]
    for targetID in target_list:
        token = sentence.token[targetID]
        if(token.lemma == lemma): return True
    return False

class RootPartOfSourceRelationExtractor(base.SourceRelationExtractor):
    """Extracts part_of relations from dependencies by source token."""
    _deps = {"nsubj"}
    _lemmas = {"have", "contain", "include"}
    
    @classmethod
    def _extract(cls, sentence, edge, resolver):
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

class RootWithOfPartOfSourceRelationExtractor(base.SourceRelationExtractor):
    """Extracts part_of relations from dependencies by source token with of."""
    _deps = {"nsubj"}
    _lemmas = {"consist"}
    
    @classmethod
    def _extract(cls, sentence, edge, resolver):
        dep_dict = resolver.source_edges_dict[edge.source-1]
        if(get_is_enhanced()):
            if("obl:of" not in dep_dict): return []
            obj_list = dep_dict["obl:of"]
        else:
            if("obl" not in dep_dict): return []
            obj_list = dep_dict["obl"]
            has_of = False
            for obj_tokenID in obj_list:
                if(obj_tokenID not in resolver.source_edges_dict): continue
                obj_dep_dict = resolver.source_edges_dict[obj_tokenID]
                if(_check_dep_lemma(sentence, obj_dep_dict, "case", "of")): break
            else: return []

        rel_targets = resolver.get_resolved_phrases(sentence, edge.target-1)
        rels = set()
        for rel_sourceID in obj_list:
            rel_sources = resolver.get_resolved_phrases(sentence, rel_sourceID)
            for rel_target in rel_targets:
                for rel_source in rel_sources:
                    rels.add(base.Relation(rel_source, _rel, rel_target))
        return rels

class RootWithOfPassivePartOfSourceRelationExtractor(RootWithOfPartOfSourceRelationExtractor):
    """Extracts part_of relations from dependencies by passive source token with of."""
    _deps = {"nsubj:pass"}
    _lemmas = {"make"}
    
class NmodOfDependencyRelationExtractor(base.DependencyRelationExtractor):
    """Extracts part_of relations from dependencies by nmod:of relation."""
    _deps = {"nmod"}
    _enhanced_deps = {"nmod:of"}
    _blacklist_source_lemmas = {"family", "arrangement", "group", "operation", "property", "set", "union",
                                "intersection", "use", "combination", "aggregation", "sum", "function"}
    
    @classmethod
    def _extract(cls, sentence, edge, resolver):
        if(sentence.token[edge.source-1].lemma in cls._blacklist_source_lemmas): return []

        if(not get_is_enhanced()):
            dep_dict = resolver.source_edges_dict[edge.target-1]
            if(not _check_dep_lemma(sentence, dep_dict, "case", "of")): return []
         
        rels = set()   
        rel_sources = resolver.get_resolved_phrases(sentence, edge.source-1)
        rel_targets = resolver.get_resolved_phrases(sentence, edge.target-1)
        for rel_source in rel_sources:
            for rel_target in rel_targets:
                rels.add(base.Relation(rel_source, _rel, rel_target))
        return rels