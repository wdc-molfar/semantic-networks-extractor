from . import phrases_resolver
from . import settings
from .relations.importer import RelationsExtractors

class SentenceParser:
    """Extracts information from sentence."""
    def __init__(self, coref_dict):
        self.resolver = phrases_resolver.PhrasesResolver(coref_dict)

    def extract(self, sentence):
        #print("------------------------------------------------------------------------------------------------")
        self.resolver.fill_dicts(sentence)
        relations = set()
        for edge in getattr(sentence, settings.get_dep_type()).edge:
            #print(f"1: {sentence.token[edge.source-1].word} -{edge.dep}-> {sentence.token[edge.target-1].word}")
            #print(f"2: {'; '.join(self.resolver.get_resolved_phrases(sentence, edge.source-1))} -{edge.dep}-> {'; '.join(self.resolver.get_resolved_phrases(sentence, edge.target-1))}")
            #print(RelationsExtractors.extract(sentence, edge, self.resolver))
            relations.update(RelationsExtractors.extract(sentence, edge, self.resolver))
            #ner (!="O") -> is_a ner.lower()
            #проверка на соответствие отдельных источников и целей (advmod -> respectively)
        return relations

class InformationExtractor:
    """Extracts information from text."""
    def __init__(self):
        self.resolved_coreferences = dict()

    def __fill_coref_dict(self, document):
        for chain in document.corefChain:
            mention = min((mention for mention in chain.mention if
                 document.sentence[mention.sentenceIndex].token[mention.headIndex].pos != "PRP"),
                key=lambda mention: mention.sentenceIndex)
            sentence = document.sentence[mention.sentenceIndex]
            self.resolved_coreferences[chain.chainID] = phrases_resolver.resolve_phrases_from_coref_dict(sentence, mention.headIndex, self.resolved_coreferences)

    def extract(self, document):
        self.resolved_coreferences.clear()
        self.__fill_coref_dict(document)
        parser = SentenceParser(self.resolved_coreferences)
        relations = set()
        for sentence in document.sentence:
            relations.update(parser.extract(sentence))
        return relations

