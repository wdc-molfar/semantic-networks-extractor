def set_dep_type(dep_type):
    global __dep_type, __is_enchanced
    __dep_type = dep_type
    __is_enchanced = "enhanced" in __dep_type.lower()

def get_dep_type():
    global __dep_type
    return __dep_type

set_dep_type("enhancedPlusPlusDependencies")

def check_edge_negation(sentence, edge):
    if(edge.dep == "neg"): return True
    if(edge.dep == "det" or edge.dep == "advmod"):
        target_token = sentence.token[edge.target - 1]
        target_lemma = target_token.lemma
        if(target_lemma == "no" or target_lemma == "not" or target_lemma == "n't"): return True
    return False

def check_word_negation(sentence, tokenID):
    for edge in getattr(sentence, __dep_type).edge:
        if(edge.source - 1 == tokenID):
            if(check_edge_negation(sentence, edge)): return True
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
        for edge in getattr(sentence, get_dep_type()).edge:
            self.source_edges_dict.setdefault(edge.dep, dict())[edge.source - 1] = edge.target - 1
            self.target_edges_dict.setdefault(edge.dep, dict())[edge.target - 1] = edge.source - 1
    
    def get_resolved_phrases(self, sentence, tokenID):
        if(tokenID in self.phrases_dict): return self.phrases_dict[tokenID]
        token = sentence.token[tokenID]
        clusterID = token.corefClusterID
        resolved = self.doc_coref_dict[clusterID] if clusterID != 0 else resolve_phrases(sentence, tokenID, self.doc_coref_dict)
        self.phrases_dict[tokenID] = resolved
        return resolved

def __get_normalized_phrases_dicts(sentence, tokenID, coref_dict, normalize=True):
    token = sentence.token[tokenID]
    normalized_word = token.lemma if normalize and token.pos == "NNS" else token.word.lower() if token.ner == "O" else token.word
    normalized_phrases = [{tokenID: normalized_word}]
    for edge in getattr(sentence, __dep_type).edge:
        if(edge.source - 1 == tokenID):
            if(check_edge_negation(sentence, edge)): return []
            target_tokenID = edge.target - 1
            if(__is_enchanced and
               next((True for normalized_dict in normalized_phrases
                     if target_tokenID in normalized_dict), False)):
                continue
            if(edge.dep == "amod" or edge.dep == "advmod" or edge.dep == "compound"):
                if(next((True for e in getattr(sentence, __dep_type).edge
                        if e.target == edge.target and e.dep.startswith("conj")), False)):#TODO: optimize (use dicts?)
                    continue
                new_dicts = __get_normalized_phrases_dicts(sentence, target_tokenID, coref_dict, False)
                normalized_phrases = [{**current_dict, **new_dict}
                                      for current_dict in normalized_phrases
                                      for new_dict in new_dicts]

            elif(edge.dep.startswith("nmod")):
                new_dicts = __get_normalized_phrases_dicts(sentence, target_tokenID, coref_dict, False)
                if(edge.dep == "nmod:poss"):
                    target_token = sentence.token[target_tokenID]
                    target_pos = target_token.pos
                    is_possessive = target_pos == "PRP$"
                    if((target_pos == "PRP" or is_possessive) and target_token.corefClusterID != 0):
                        resolved_corefs = coref_dict.get(target_token.corefClusterID, None)
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
                case_tokenID = next((e.target - 1 for e in getattr(sentence, __dep_type).edge
                        if e.source == edge.target and e.dep == "case"), -1)#TODO: optimize (use dicts?)
                if(case_tokenID != -1):
                    for current_dict in normalized_phrases:
                        current_dict[case_tokenID] = sentence.token[case_tokenID].lemma

            elif(edge.dep.startswith("conj")):
                normalized_phrases.extend(__get_normalized_phrases_dicts(sentence, target_tokenID, coref_dict, normalize))
    return normalized_phrases

def resolve_phrases(sentence, tokenID, coref_dict):
    phrases_dicts = __get_normalized_phrases_dicts(sentence, tokenID, coref_dict)
    phrases = [' '.join([phrase_dict[key] for key in sorted(phrase_dict)]) for phrase_dict in phrases_dicts]
    return phrases
