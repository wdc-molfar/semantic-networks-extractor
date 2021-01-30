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
                if("case" not in obj_dep_dict): continue
                case_list = obj_dep_dict["case"]
                for caseID in case_list:
                    case_token = sentence.token[caseID]
                    if(case_token.lemma == "of"):
                        has_of = True
                        break
                if(has_of): break
            if(not has_of): return []

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
    