#!/usr/bin/python
import random
import sys


features = {}

def mapFeatureToNum(listTag):
    i = 0
    for line in listTag:
        if line[0] not in features:
            features[line[0]] = i
            i += 1

    for line in listTag:
        for feature in line:
            if feature not in features:
                features[feature] = i
                i += 1


def featureMap(i, feature):
    if i == 0:
        return str(feature)
    return str(feature) + ":1"


def main():
    featuresFile = sys.argv[1]
    featureVecsFile = sys.argv[2]
    featureMapFile = sys.argv[3]

    file = open(featuresFile, "r")
    lines = file.read().split('\n')
    listTag = list(map(lambda x: x.split(' '), lines))

    mapFeatureToNum(listTag)

    featuresDic = [[features[feature] for feature in line] for line in listTag]
    for line in featuresDic:
        line.sort()
    featuresDic = [[featureMap(i, feature) for i, feature in enumerate(line)] for line in featuresDic]

    outF = open(featureVecsFile, 'w')
    outF.write('\n'.join(list(map(lambda l: " ".join(l), featuresDic))))
    outF.close()

    mapF = open(featureMapFile, 'w')
    mapF.write("\n".join(list(map(lambda k: k + " " + str(features[k]), list(features.keys())))))
    mapF.close()



if __name__ == "__main__":
    main()
