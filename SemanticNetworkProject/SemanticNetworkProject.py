import os.path
import stanza
from stanza.server import CoreNLPClient
from extractor.core import InformationExtractor
from extractor.settings import set_dep_type
from extractor.relations.importer import RelationsExtractors

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

#input_text = "A semantic network is a graph structure for representing knowledge. It consists of nodes, links and link labels."
#input_text = "A boy and a girl are playing with figures. Their small and big red and white cubes and yellow parallelepipeds are on the table. These figures are parts of a pyramid."
#input_text = "The cubes are red and not big. There are cubes and no spheres on the table. They are parts of a wall."
#input_text = "United States of America is a country. It is very large. Barack Obama was a president of it. His daughters are Sasha and Malia. They were one of the most influential teenagers of 2014."
#input_text = "There are neither green nor yellow cubes on the table."
#input_text = "Middle ear has anvil and stirrup. Middle ear contains anvil and stirrup. Middle ear includes anvil and stirrup. Middle ear is made of anvil and stirrup. Middle ear consists of anvil and stirrup."
input_text = "Doors of the car. The car’s door is open. The car with a door. A segment is a part of a circle. A circle is a set of points. Points within the figure. Functions used within Geometry. The imaginary axis is the vertical line in a complex plane. The altitude with the hypotenuse as base divides the hypotenuse into two lengths. The first part of the ear the sound waves reach is called the tympanic membrane. Middle ear consists of anvil and stirrup."

set_dep_type("enhancedPlusPlusDependencies")
#set_dep_type("basicDependencies")

RelationsExtractors.use_all_relations()
#RelationsExtractors.use_relations(["part_of"])

#java -Xmx5G -cp C:\Users\Alexander\stanza_corenlp\* edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 60000 -threads 5 -maxCharLength 100000 -quiet False -serverProperties english -annotators tokenize,ssplit,pos,lemma,ner,depparse,coref -preload -outputFormat serialized
with CoreNLPClient(properties=language, start_server=stanza.server.StartServer.DONT_START, annotators="tokenize,ssplit,pos,lemma,ner,depparse,coref") as client:
      document = client.annotate(input_text)
      ie = InformationExtractor()
      ie.extract(document)
      print(ie.resolved_coreferences)
#TODO: save to Neo4j
