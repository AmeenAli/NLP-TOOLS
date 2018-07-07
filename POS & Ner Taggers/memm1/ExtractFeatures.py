#!/usr/bin/python
import random
import sys

output = []

countDictionary = {}


def splitTag(x):
    index = x.rfind('/')
    return [x[:index], x[index + 1:]]


def splitWord(lines):
    llist = []
    for i in lines:
        llist.append(list(map(splitTag, i.split(' '))))
    return llist


def isRare(word):
    if word.lower() in countDictionary:
        if countDictionary[word.lower()] < 5:
            return True
        else:
            return False
    return True


def getFeatures(Wi, WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore, TiBeforeBefore):
    features = {}
    if isRare(Wi):
        lenWord = len(Wi)
        for i in range(4):
            if lenWord > i:
                features['prefix' + str(i + 1)] = Wi[:i + 1]
                features['suffix' + str(i + 1)] = Wi[lenWord - i - 1:]
        features['contains_number'] = any(char.isdigit() for char in Wi)
        features['contains_hyphen'] = any(char == '-' for char in Wi)
        features['contains_uppercase'] = any(char.isupper() for char in Wi)
    else:
        features["Wi"] = Wi.lower()

    features['TiBefore'] = TiBefore
    features['TiBeforeBefore'] = TiBeforeBefore + '/' + TiBefore
    if WiBefore is not None:
        features['WiBefore'] = WiBefore.lower()
    if WiBeforeBefore is not None:
        features['WiBeforeBefore'] = WiBeforeBefore.lower()
    if WiAfter is not None:
        features['WiAfter'] = WiAfter
    if WiAfterAfter is not None:
        features['WiAfterAfter'] = WiAfterAfter

    return features


def printFeatures(obj):
    fProp = []
    for key, feature in obj.items():
        fProp.append(key + "=" + str(feature))
    return " ".join(fProp)


def extractData(listData):
    for line in listData:
        for [word, tag] in line:
            word = word.lower()
            if word not in countDictionary:
                countDictionary[word] = 0
            countDictionary[word] += 1


def createFeatures(listData):
    for line in listData:
        lineLength = len(line)
        for i, [Wi, tag] in enumerate(line):
            if i > 0:
                WiBefore = line[i - 1][0]
                TiBefore = line[i - 1][1]
            else:
                WiBefore = None
                TiBefore = "XX"
            if i > 1:
                WiBeforeBefore = line[i - 2][0]
                TiBeforeBefore = line[i - 2][1]
            else:
                WiBeforeBefore = None
                TiBeforeBefore = "XX"
            if i < lineLength - 1:
                WiAfter = line[i + 1][0]
            else:
                WiAfter = None
            if i < lineLength - 2:
                WiAfterAfter = line[i + 2][0]
            else:
                WiAfterAfter = None
            # print to output
            output.append(tag + " " + printFeatures(
                getFeatures(Wi, WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore, TiBeforeBefore)))


def main():
    inputFile = sys.argv[1]
    outputFile = sys.argv[2]

    input = open(inputFile, "r").read().split('\n')

    listData = splitWord(input)

    extractData(listData)

    createFeatures(listData)

    out = open(outputFile, 'w')
    out.write('\n'.join(output))
    out.close()


if __name__ == "__main__":
    main()
