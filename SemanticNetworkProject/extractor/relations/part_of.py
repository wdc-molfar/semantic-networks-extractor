from . import base
from .. import phrases_resolver

_rel = "part_of" #TODO: use enum?

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
    pass

class RootWithOfPassivePartOfSourceRelationExtractor(base.SourceRelationExtractor):
    """Extracts part_of relations from dependencies by passive source token with of."""
    _deps = {"nsubj:pass"}
    _lemmas = {"make"}
    pass