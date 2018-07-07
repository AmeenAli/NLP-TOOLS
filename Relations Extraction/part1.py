import sys
from collections import OrderedDict
import random
import spacy
import itertools
from nltk.corpus import wordnet as wn
import json
import numpy as np
import scipy
import pdb
import pickle
from sklearn.externals import joblib
from sklearn import metrics , svm


spc = spacy.load('en')


countriesJson = json.load(open('countries.json'))
usJson = json.load(open('us.json'))
citiesJson = json.load(open('cities.json'))
states = []

for s in usJson:
    states.append(usJson[s].lower().replace(" ", "-"))
countries = []

for c in countriesJson:
    countries.append(c["name"].lower().replace(" ", "-"))

countries.append("u.s.")
cities = {}

for c in citiesJson:
    cities[c["name"].lower().replace(" ", "-")] = 1

PERSON_NER = {'PERSON'}
TARGET_TAG = "Live_In"
LOCATION_NER = {'GPE', 'FACILITY', 'LOC'}
LOCATION_ALTER_NER = {'ORG'}
TAGS = {'OrgBased_In', 'Located_In', 'Work_For', 'Kill', 'Live_In'}
LABELS = {'OrgBased_In': 5, 'Located_In': 4, 'Work_For': 3, 'Kill': 2, "Live_In": 1, "other": 0}


class AnnotationsConnection:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, connection):
        if isinstance(connection, AnnotationsConnection):
            return self.x == connection.x and self.y == connection.y
        return False

    def __repr__(self):
        return '(x=%s, y=%s)' % (self.x, self.y)

    def __hash__(self):
        return hash(self.__repr__())


def entityToPerson(entity):
    if entity in ['PERSON']:
        entity = "PERSON"
    return entity

def entityToLocation(entity):
    if entity["ner"] in [ 'LOC', 'GPE', 'ORG' ] :
        return "LOCATION"
    return entity["ner"]

def nameOrEntity(word):
    if word["pos"].startswith("NN"):
        return "NN"
    return word["pos"]

def isCountry(word):
    word = word.lower().replace(" ", "-")
    return word in countries

def isCity(word):
    word = word.lower().replace(" ", "-")
    return word in cities

def isState(word):
    word = word.lower().replace(" ", "-")
    return word in states


class Features:
    def __init__(self, x, y, sentence):
        self.x = x
        self.y = y
        self.feat = []
        self.buildFeatures(sentence)

    def buildFeatures(self, sentence):
        # entity based features
        # entity type 1
        self.feat.append(self.x[-1]["ner"])
        self.feat.append(entityToPerson(self.x[-1]["ner"]))
        # entity 1 head
        self.feat.append(self.x[-1]['word'])
        # entity type 2
        self.feat.append(self.y[-1]["ner"])
        self.feat.append(entityToLocation(self.y[-1]))
        # entity 2 head
        self.feat.append(self.y[-1]['word'])
        # concatenate types
        self.feat.append(self.x[-1]["ner"] + self.y[-1]["ner"])

        for word in self.x:
            self.feat.append(word["pos"])
        for word in self.y:
            self.feat.append(word["pos"])

        # word based features
        start = False
        before1 = None
        before2 = None
        after1 = None
        after2 = None
        syntactChunk = []

        for id, word in sentence.iteritems():
            if word == self.y[0]:
                start = False
                if id-1 in sentence:
                    before2 = sentence[id-1]["word"]
            if word == self.y[-1]:
                if id+1 in sentence:
                    after2 = sentence[id+1]["word"]
                break
            if start:
                self.feat.append("Between+"+word["word"])
                syntactChunk.append(word["pos"])
            if word == self.x[0]:
                if id-1 in sentence:
                    before1 = sentence[id-1]["word"]
            if word == self.x[-1]:
                if id+1 in sentence:
                    after1 = sentence[id+1]["word"]
                start = True

        for syntact in syntactChunk:
            self.feat.append("Base"+syntact)

        # word before entity 1
        if before1 is None:
            self.feat.append("BeforeEnt1Start")
        else:
            self.feat.append("BeforeEnt1"+before1)
        if before2 is None:
            self.feat.append("BeforeEnt2Start")
        else:
            self.feat.append("BeforeEnt2"+before2)

        if after1 is None:
            self.feat.append("AfterEnt1End")
        else:
            self.feat.append("AfterEnt1"+after1)
        if after2 is None:
            self.feat.append("AfterEnt2End")
        else:
            self.feat.append("AfterEnt2"+after2)

        # entity level
        self.feat.append(nameOrEntity(self.x[-1]))
        self.feat.append(nameOrEntity(self.y[-1]))

        # synonyms
        syns = wn.synsets(chunkPhrase(self.x), 'n')
        if len(syns) > 0:
            list_sim = [lemma.name() for synset in syns[0].hyponyms() for lemma in synset.lemmas()]
            for sim in list_sim:
                self.feat.append(sim)
        syns = wn.synsets(chunkPhrase(self.y), 'n')
        if len(syns) > 0:
            list_sim = [lemma.name() for synset in syns[0].hyponyms() for lemma in synset.lemmas()]
            for sim in list_sim:
                self.feat.append(sim)
        dep = self.x[0]["parent"]
        while dep != 0 and dep != self.y[-1]["id"]:
            self.feat.append(sentence[dep]["word"])
            dep = sentence[dep]["parent"]
        dep = self.y[-1]["parent"]
        while dep != 0 and dep != self.x[0]["id"]:
            self.feat.append(sentence[dep]["word"])
            dep = sentence[dep]["parent"]

        for word in self.x:
            if isCity(word["word"]):
                self.feat.append("CityLeft"+word["word"])
            if isState(word["word"]):
                self.feat.append("StateLeft"+word["word"])
            if isCountry(word["word"]):
                self.feat.append("CountryLeft"+word["word"])
        for word in self.y:
            if isCity(word["word"]):
                self.feat.append("CityRight"+word["word"])
            if isState(word["word"]):
                self.feat.append("StateRight"+word["word"])
            if isCountry(word["word"]):
                self.feat.append("CountryRight"+word["word"])


def extractChunks(words):
    i=0
    chunks = []
    chunk = []
    prev = None
    for j, word in words.iteritems():
        if word['bio'] in {'O', 'B'}:
            if word['bio'] =='0' and word['dep'] == 'compound':
                chunk.append(word)
            if chunk:
                chunks.append(chunk)
            chunk=[]
            if word['bio'] =='0' and word['dep'] == 'compound':
                chunk.append(word)
        if word['bio'] in {'I','B'}:
            chunk.append(word)
        prev=word
        i += 1
    return chunks

def readAnnotationsFile(file):
    annotations = {}
    sentences = open(file, "r").read().split("\n")
    for sentence in sentences:
        if sentence == "":
            continue
        sentence = sentence.split("(")[0]
        sentenceId = int(sentence.split("\t")[0].replace("sent", ""))
        sentence = sentence.replace("sent" + str(sentenceId) + "\t", "")
        x, tag, y, _ = sentence.split("\t")
        if sentenceId not in annotations:
            annotations[sentenceId] = []
        if tag not in TAGS:
            tag = 'other'
        annotations[sentenceId].append((AnnotationsConnection(x, y), LABELS[tag]))
    return annotations


def processCorpus(corpus):
    sentencesDic = OrderedDict()
    for sentence in corpus:
        if sentence == "":
            continue
        sentenceId = int(sentence.split("\t")[0].replace("sent", ""))
        parsedSentence = spc(unicode(sentence.split("\t")[1]))
        sentencesDic[sentenceId] = OrderedDict()
        sentencesDic[sentenceId]["text"] = sentence.split("\t")[1]
        sentencesDic[sentenceId]["words"] = {}

        for i, word in enumerate(parsedSentence):
            headId = word.head.i + 1
            if word == word.head:
                assert (word.dep_ == "ROOT"), word.dep_
                headId = 0

            words = {
                "id": word.i + 1,
                "word": word.text,
                "lemma": word.lemma_,
                "pos": word.pos_,
                "tag": word.tag_,
                "parent": headId,
                "dependency": word.dep_,
                "bio": word.ent_iob_,
                "ner": word.ent_type_
            }

            sentencesDic[sentenceId]["words"][words["id"]] = words
    return sentencesDic

def chunkPhrase(chunks):
    phrase=""
    for chunk in chunks:
        if chunk['word'] in ['.','-']:
            phrase = phrase[:-1] + chunk['word']
        else:
            phrase += chunk['word'] + ' '
    return phrase[:-1]

def createData(annotations,sentences):
    allFeatures={}
    arrayFeatures=[]
    labels=[]
    for sentenceId, dic in sentences.iteritems():
        sentence = dic['words']
        chunk= itertools.permutations(extractChunks(sentence), 2)
        featuresChunks=[]
        size=0
        for chunkPair in chunk:
            size += 1
            for annotation, tag in annotations[sentenceId]:
                x = chunkPhrase(chunkPair[0])
                y = chunkPhrase(chunkPair[1])
                connect = AnnotationsConnection(x,y)
                correct, label = False, 0
                if (annotation.x == x or annotation.x==x + "." or annotation.x== x + " .") and (annotation.y==y or annotation.y==y + "." or annotation.y==y + " ."):
                    correct, label = True, tag
                labels.append(label)
                feature=Features(chunkPair[0],chunkPair[1],sentence)
                features=[]
                for feat in feature.feat:
                    if feat not in allFeatures:
                        allFeatures[feat]=len(allFeatures)
                    features.append(allFeatures[feat])
                arrayFeatures.append(features)

    fullFeautures = []
    for dense in arrayFeatures:
        sparse = np.zeros(len(allFeatures))
        for i in dense:
            sparse[i]=1
        fullFeautures.append(sparse)
    A = np.array(fullFeautures)
    return scipy.sparse.csr_matrix(A), np.array(labels), allFeatures

def saveModel(svc, features):
    joblib.dump(svc, 'model.pkl')
    pickle.dump(features, open('features.pkl', 'wb'))

if __name__ == '__main__':
    corpusFile = sys.argv[1]
    annotationsFile = sys.argv[2]
    print("Reading annotation file... ")
    annotations = readAnnotationsFile(annotationsFile)
    print("Done!\n")
    corpus = open(corpusFile, "r").read().split("\n")
    print("Reading the corpus file... ")
    sentences = processCorpus(corpus)
    print("Done!\n")
    print("Creating features... ")
    features, tags, allFeatures = createData(annotations,sentences)
    print("Done!\n")
    svc = svm.LinearSVC()
    svc.fit(features, tags)
    saveModel(svc, allFeatures)
    print("Saving model... Done!\n")




