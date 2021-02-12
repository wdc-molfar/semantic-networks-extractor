#from typing import List, Dict
from . import settings

#NodeEdgesDict = Dict[int, Dict[str, int]]

def check_dep_lemma(sentence, dep_dict, dep, lemma) -> bool:
    if(dep not in dep_dict): return False
    target_list = dep_dict[dep]
    for targetID in target_list:
        token = sentence.token[targetID]
        if(token.lemma == lemma): return True
    return False

def check_negation(sentence, dep, targetID):
    if(dep == "neg"): return True

    if(dep == "det" or dep == "advmod"):
        target_token = sentence.token[targetID]
        target_lemma = target_token.lemma
        if(target_lemma == "no" or target_lemma == "not"
           or target_lemma == "n't" or target_lemma == "never"): return True

    elif(dep == "cc:preconj"):
        target_token = sentence.token[targetID]
        target_lemma = target_token.lemma
        if(target_lemma == "neither"): return True

    return False

def check_word_negation(sentence, tokenID, source_edges_dict):
    for edge_dep, edge_targets_list in source_edges_dict[tokenID].items():
        for target_tokenID in edge_targets_list:
            if(check_negation(sentence, edge_dep, target_tokenID)): return True
    return False

class PhrasesResolver:
    """Creates phrases from dependencies."""
    def __init__(self, coref_dict):
        self.source_edges_dict = dict()
        self.target_edges_dict = dict()
        self.phrases_dict = dict()
        self.doc_coref_dict = coref_dict

    def clear(self):
        self.source_edges_dict.clear()
        self.target_edges_dict.clear()
        self.phrases_dict.clear()

    def fill_dicts(self, sentence):
        self.clear()
        for edge in getattr(sentence, settings.get_dep_type()).edge:
            self.source_edges_dict.setdefault(edge.source - 1, dict()).setdefault(edge.dep, list()).append(edge.target - 1)
            self.target_edges_dict.setdefault(edge.target - 1, dict()).setdefault(edge.dep, list()).append(edge.source - 1)
    
    def get_resolved_phrases(self, sentence, tokenID):
        if(tokenID in self.phrases_dict): return self.phrases_dict[tokenID]
        token = sentence.token[tokenID]
        clusterID = token.corefClusterID
        resolved = self.doc_coref_dict[clusterID] if clusterID != 0 else resolve_phrases(sentence, tokenID, self)
        self.phrases_dict[tokenID] = resolved
        return resolved

def __get_normalized_phrases_dicts(sentence, tokenID, resolver:PhrasesResolver, normalize = True, ignored_tokenID = -1):
    token = sentence.token[tokenID]
    normalized_word = token.lemma if normalize and token.pos.startswith("NN") and token.pos.endswith("S") else token.word.lower() if token.ner == "O" else token.word
    normalized_phrases = [{tokenID: normalized_word}]
    if(settings.get_is_enhanced()): #for "is a type of something"
        target_dict = resolver.target_edges_dict.get(tokenID, None)
        if(target_dict is not None and "fixed" in target_dict):
            for fixed_tokenID in target_dict["fixed"]:
                for fixed_targets_list in resolver.source_edges_dict[fixed_tokenID].values():
                    for fixed_target_tokenID in fixed_targets_list:
                        normalized_phrases[0][fixed_target_tokenID] = sentence.token[fixed_target_tokenID].lemma
                if(fixed_tokenID in resolver.target_edges_dict):
                    for fixed_sources_list in resolver.target_edges_dict[fixed_tokenID].values():
                        for fixed_source_tokenID in fixed_sources_list:
                            if(fixed_source_tokenID in normalized_phrases[0]): continue #cycle checking
                            new_dicts = __get_normalized_phrases_dicts(sentence, fixed_source_tokenID, resolver, False)
                            normalized_phrases = [{**current_dict, **new_dict}
                                        for current_dict in normalized_phrases
                                        for new_dict in new_dicts]

    if(tokenID not in resolver.source_edges_dict): return normalized_phrases
    for edge_dep, edge_targets_list in resolver.source_edges_dict[tokenID].items():
        for target_tokenID in edge_targets_list:
            if(target_tokenID == ignored_tokenID): continue
            if(check_negation(sentence, edge_dep, target_tokenID)): return []

            if(settings.get_is_enhanced()):
                if(next((True for normalized_dict in normalized_phrases #cycle checking
                         if target_tokenID in normalized_dict), False)):
                    continue

                if(not edge_dep.startswith("conj")):
                    target_dep_dict = resolver.target_edges_dict[target_tokenID]
                    if(next((True for target_dep in target_dep_dict #multiple roots checking
                             if target_dep.startswith('conj')), False)):
                        continue

            if(edge_dep == "amod" or edge_dep == "advmod" or edge_dep == "compound" or (edge_dep == "nummod" and not normalize)):
                new_dicts = __get_normalized_phrases_dicts(sentence, target_tokenID, resolver, False)
                normalized_phrases = [{**current_dict, **new_dict}
                                        for current_dict in normalized_phrases
                                        for new_dict in new_dicts]

            elif(edge_dep.startswith("nmod")):
                #"such as" checking
                if((settings.get_is_enhanced() and edge_dep == "nmod:such_as") or
                   check_dep_lemma(sentence, resolver.source_edges_dict[target_tokenID], "case", "such")): continue

                new_dicts = __get_normalized_phrases_dicts(sentence, target_tokenID, resolver, False)
                if(edge_dep == "nmod:poss"):
                    target_token = sentence.token[target_tokenID]
                    target_pos = target_token.pos
                    is_possessive = target_pos == "PRP$"
                    if((target_pos == "PRP" or is_possessive) and target_token.corefClusterID != 0):
                        resolved_corefs = resolver.doc_coref_dict.get(target_token.corefClusterID, None)
                        if(resolved_corefs is not None):
                            resolved_new_dicts = []
                            for new_dict in new_dicts:
                                for coref_phrase in resolved_corefs:
                                    resolved_new_dict = dict(new_dict)
                                    resolved_new_dict[target_tokenID] = coref_phrase
                                    if(is_possessive): resolved_new_dict[target_tokenID + 0.5] = "'s"
                                    resolved_new_dicts.append(resolved_new_dict)
                            new_dicts = resolved_new_dicts
                normalized_phrases = [{**current_dict, **new_dict}
                                        for current_dict in normalized_phrases
                                        for new_dict in new_dicts]
                
                target_source_dict = resolver.source_edges_dict.get(target_tokenID, None)
                if(target_source_dict is not None and "case" in target_source_dict):
                    for case_tokenID in target_source_dict["case"]:
                        for current_dict in normalized_phrases:
                            current_dict[case_tokenID] = sentence.token[case_tokenID].lemma

            elif(edge_dep.startswith("conj")):
                normalized_phrases.extend(__get_normalized_phrases_dicts(sentence, target_tokenID, resolver, normalize))
    return normalized_phrases

def resolve_phrases(sentence, tokenID, resolver: PhrasesResolver, ignored_tokenID = -1):
    phrases_dicts = __get_normalized_phrases_dicts(sentence, tokenID, resolver, ignored_tokenID=ignored_tokenID)
    phrases = [' '.join([phrase_dict[key] for key in sorted(phrase_dict)]) for phrase_dict in phrases_dicts]
    return phrases

def resolve_phrases_from_coref_dict(sentence, tokenID, coref_dict, ignored_tokenID = -1):
    resolver = PhrasesResolver(coref_dict)
    resolver.fill_dicts(sentence)
    return resolve_phrases(sentence, tokenID, resolver, ignored_tokenID)
