import os.path
import stanza
from stanza.server import CoreNLPClient
import extractor

#lang = "en"
#stanza.download(lang)
#nlp = stanza.Pipeline(lang)

#doc = nlp(input_text)
#print(doc)

#for sentence in doc.sentences:
#    for (word1, dep, word2) in sentence.dependencies:
#        print(f'{word1.text} ({word1.lemma}) -{dep}-> {word2.text} ({word2.lemma})')

language = "english"
version = "4.2.0"
stanza.install_corenlp()
if not os.path.isfile(f"./models/stanford-corenlp-{version}-models-{language}.jar"):
    stanza.download_corenlp_models(model=language, version=version)

input_text = "A semantic network is a graph structure for representing knowledge in patterns of interconnected nodes and arcs. It consists of nodes, links and link labels."
#input_text = "A boy and a girl are playing with figures. Their small and big red and white cubes and yellow parallelepipeds are on the table. These figures are parts of a pyramid."
#input_text = "The cubes are red and not big. There are cubes and no spheres on the table. They are parts of a wall."
#input_text = "United States of America is a country. It is very large. Barack Obama was a president of it. His daughters are Sasha and Malia. They were one of the most influential teenagers of 2014."

#java -Xmx5G -cp C:\Users\Alexander\stanza_corenlp\* edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 60000 -threads 5 -maxCharLength 100000 -quiet False -serverProperties english -annotators tokenize,ssplit,pos,lemma,ner,depparse,coref -preload -outputFormat serialized
with CoreNLPClient(properties=language, start_server=stanza.server.StartServer.DONT_START, annotators="tokenize,ssplit,pos,lemma,ner,depparse,coref") as client:
      document = client.annotate(input_text)
      ie = extractor.InformationExtractor()
      ie.extract(document)
      print(ie.resolved_coreferences)
#TODO: source, dep, target - chains of resp
#TODO: negation checker (sentence, headID)
#TODO: conjunction checker (sentence, headID)
#TODO: create array of triples -> (subject, relation, object)
#TODO: save to Neo4j
#dictionary for coreference (full document); dictionaries for dep (current sentence)
#1) Класс обработки текста (создаёт словарь разрешения кореферентности)
#2) Класс обработки предложения (обрабатывает зависимости, игнорируя лишние, но собирает их все в словари; подготавливает фразы (мемоизация?))
#3) Классы или функции цепочек обязанностей для обработки зависимостей и получения массивов триплетов
#4) Классы или функции для обработки отрицаний и конъюнкции
#5) Класс или функция для сохранения триплетов в Neo4j
