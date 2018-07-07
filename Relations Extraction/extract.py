import sys
import part1
import json
import numpy
import scipy
import pickle
from collections import OrderedDict
import random
import part1
import spacy
import numpy as np
import itertools
from nltk.corpus import wordnet as wn
from sklearn.externals import joblib
from sklearn import metrics,svm


LOCATION_NER = { 'GPE', 'FACILITY', 'LOC' }
LOCATION_ALTER_NER = { 'ORG' }
TARGET_TAG = {1: "Live_In", 0 : "Other_Tag" }
TAG_TO_PREDICT = "Live_In"
PERSON_NER = { 'PERSON' }


def isGazette(word):
    word=word.lower().replace(" ", "-")
    return word.lower() in part1.countries or word.lower() in  part1.states or word.lower() in  part1.cities

def checkEntityChunkPhrase(phrase):
    for chunk in phrase:
        if part1.entityToPerson(chunk["ner"]) != "PERSON":
            return False
    return True

def createAnnotationsFile(output_file, predicted, tags, sentences):
    file = open(output_file, "w")
    toWrite = ""
    index = 0
    for i, predict in enumerate(predicted):
        sentenceId, chunk = tags[i]
        left, right = chunk
        if predict == 1 or (predict == 0 and connected(sentences[sentenceId]["words"], left, right)):
            toWrite += "sent" + str(sentenceId) + "\t"
            toWrite += part1.chunkPhrase(left)
            toWrite += "\t" + TAG_TO_PREDICT + "\t"
            toWrite += part1.chunkPhrase(right) + "\n"

    file.write(toWrite)


def connected(sentence, left, right):
    pattern = ["from", "of"]
    not_in = ["manager"]
    pattern_of = ["home", "governor" , "king" , "hometown" , "citizen" , "resident" , "inhabitant" , "civilian"]
    pattern_in = ["live", "living", "stay", "staying", "representative" , "settle" , "reside"]
    work = {"spokesman", "spokeswoman", "diver", "Lt.", "representative", "governor", "manager"}
    if not part1.chunkPhrase(left).endswith("'s'"):
        if checkEntityChunkPhrase(left) and (isGazette(part1.chunkPhrase(right) or part1.entityToLocation(right[-1]) == "LOCATION" or part1.entityToLocation(right[0]) == "LOCATION")):
            start = False
            found = False
            for id, word in sentence.iteritems():
                if word["id"] == left[0]["id"]:
                    if id-1 in sentence and sentence[id-1]["lemma"] in work:
                        found = True
                if word["id"] == left[-1]["id"]:
                    start = True
                if  word["id"] == right[0]["id"]:
                    break
                if start:
                    if word["lemma"] in pattern_in and id+1 in sentence:
                        if sentence[id+1]["lemma"] in {"in", "on"}:
                            found = True
                    if word["lemma"] in pattern_of and id+1 in sentence:
                        if sentence[id+1]["lemma"] == "of":
                            found = True
                    if word["lemma"] in pattern:
                        if id-1 in sentence:
                            if not sentence[id-1]["lemma"] in not_in:
                                # found = True
                                if id+1 in sentence:
                                    if isGazette(sentence[id+1]["lemma"]):
                                        found = True
                                    if sentence[id+1]["tag"] == "ADJ":
                                        if id+2 in sentence:
                                            if isGazette(sentence[id+2]["lemma"]):
                                                found = True
                            else:
                                found = False
            return found
    return False


def createData(sentences, allFeatures):
    featuresArray = []
    tagging = []
    for sentenceId, dic in sentences.iteritems():
        sentence = dic['words']
        chunk = itertools.permutations(part1.extractChunks(sentence), 2)
        for chunkPair in chunk:
            x = part1.chunkPhrase(chunkPair[0])
            y = part1.chunkPhrase(chunkPair[1])
            connect = part1.AnnotationsConnection(x, y)
            feat_sent = part1.Features(chunkPair[0], chunkPair[1], sentence)
            features = []
            for feat in feat_sent.feat:
                if feat in allFeatures:
                    features.append(allFeatures[feat])

            featuresArray.append(features)
            tagging.append((sentenceId, chunkPair))
    inflatedFeats = []
    for dense in featuresArray:
        sparse = np.zeros(len(allFeatures))
        for i in dense:
            sparse[i] = 1
        inflatedFeats.append(sparse)
    return scipy.sparse.csr_matrix(inflatedFeats), tagging


if __name__ == '__main__':
    inputFile=sys.argv[1]
    outputFile=sys.argv[2]
    corpus = open(inputFile, "r").read().split("\n")

    sentences = part1.processCorpus(corpus)
    svc=joblib.load('model.pkl')
    featuresLearn=pickle.load(open('features.pkl','rb'))
    featuresDic={ feat:id for id,feat in featuresLearn.iteritems()}
    features, tagging = createData(sentences, featuresLearn)
    predicted = svc.predict(features)
    createAnnotationsFile(outputFile, predicted, tagging, sentences)

