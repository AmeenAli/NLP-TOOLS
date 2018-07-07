import sys
import pickle
import numpy

isTrain = True if len(sys.argv) > 5 else False

eMap = {}

totalChecked = 0
totalCorrect = 0

tagSet = set([])

features = {}
reverseFeatures = {}
cacheDic = {}
probabiltyCache = {}
outputLines = []



def splitTag(x):
    if not isTrain:
        return [x]
    index = x.rfind('/')
    return [x[:index], x[index + 1:]]


def splitWord(lines):
    llist = []
    for i in lines:
        llist.append(list(map(splitTag, i.split(' '))))
    return llist


def argmax(d):
    v = list(d.values())
    k = list(d.keys())
    return k[v.index(max(v))]


def extractE(eMLE):
    for line in eMLE:
        part = line.split('\t')
        space = part[0].split(' ')
        if space[0] not in eMap:
            eMap[space[0]] = {}
        eMap[space[0]][space[1]] = float(part[1])


def extractFeat(featureMap):
    for line in featureMap:
        space = line.split(' ')
        features[space[0]] = int(space[1])
        reverseFeatures[space[1]] = space[0]
        if '=' not in space[0] or space[0] == '=':
            tagSet.add(space[0])
        else:
            type, value = space[0].split('=', 1)
            if type == 'TiBeforeBefore':
                tag1, tag2 = value.split('/')
                if tag1 not in cacheDic:
                    cacheDic[tag1] = set([])
                cacheDic[tag1].add(tag2)


def isNewWord(word):
    word = word.lower()
    tempWord = 'Wi=' + word
    if tempWord not in features:
        return True
    else:
        return False

def getFeatures(Wi, WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore, TiBeforeBefore):
    features = {}
    if isNewWord(Wi):
        lengthWord = len(Wi)
        for i in range(0, 4):
            if lengthWord > i:
                features['prefix' + str(i + 1)] = Wi[:i + 1]
                features['suffix' + str(i + 1)] = Wi[lengthWord - i - 1:]
        features['contains_number'] = any(char.isdigit() for char in Wi)
        features['contains_hyphen'] = True if ('-' in Wi) else False
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

def predictConfidence(Wi, WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore, TiBeforeBefore, model):
    featureVec = numpy.zeros(len(features) - 1)
    f = getFeatures(Wi, WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore, TiBeforeBefore)
    for key, feature in f.items():
        temp = key + "=" + str(feature)
        if temp in features:
            featureVec[features[temp] - 1] = 1
    return model.predict_log_proba([featureVec])

def getScore(Wi, WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore, TiBeforeBefore, model):
    cachee = Wi + str(WiBefore) + str(WiBeforeBefore) + str(WiAfter) + str(WiAfterAfter) + TiBefore + TiBeforeBefore
    if cachee not in probabiltyCache:
        probabiltyCache[cachee] = (
        predictConfidence(Wi, WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore, TiBeforeBefore, model)[0])
    return probabiltyCache[cachee]


# viterbi algorithm with back pointers
def viterbiAlgo(listData, model):
    for line in listData:
        numOfWordsInLine = len(line) - 1
        temptagSet = set(tagSet)
        temptagSet.add("XX")
        V = [{}] + [{} for word in line]

        for t in temptagSet:
            V[0][t] = {}
            for r in tagSet:
                V[0][t][r] = 0

        V[0]["XX"]["XX"] = 1
        BP = [{}] + [{} for word in line]
        prevPretemptagSet = ["XX"]
        pretemptagSet = ["XX"]

        lineLength = len(line)

        for i in range(0, numOfWordsInLine + 1):
            origWord = line[i][0]
            word = origWord.lower()
            currtagSet = tagSet
            if word in eMap:
                currtagSet = list(eMap[word].keys())
            currtagSet = list(map(lambda x: x.upper(), currtagSet))

            # set some features
            if i > 0:
                WiBefore = line[i - 1][0]
            else:
                WiBefore = None
            if i > 1:
                WiBeforeBefore = line[i - 2][0]
            else:
                WiBeforeBefore = None
            if i < lineLength - 1:
                WiAfter = line[i + 1][0]
            else:
                WiAfter = None
            if i < lineLength - 2:
                WiAfterAfter = line[i + 2][0]
            else:
                WiAfterAfter = None

            V[i + 1] = {}
            BP[i + 1] = {}

            for t in pretemptagSet:
                TiBefore = t
                V[i + 1][t] = {}
                BP[i + 1][t] = {}
                l = {}
                for r in currtagSet:
                    l[r] = {}
                for tT in prevPretemptagSet:
                    TiBeforeBefore = tT
                    score = (V[i][tT][t]) + getScore(word, WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore,
                                                     TiBeforeBefore, model)
                    for r in currtagSet:
                        l[r][tT] = score[features[r]]
                for r in currtagSet:
                    V[i + 1][t][r] = max(list(l[r].values()))
                    BP[i + 1][t][r] = argmax(l[r])
            prevPretemptagSet = pretemptagSet
            pretemptagSet = currtagSet

        V.pop(0)
        BP.pop(0)

        matrix = map(lambda x: x.values(), V[numOfWordsInLine].values())
        maxx = list(map(max, matrix))
        maxV = max(maxx)
        maxTIndex = maxx.index(maxV)
        maxT = list(V[numOfWordsInLine].keys())[maxTIndex]
        maxR = argmax(V[numOfWordsInLine][maxT])
        y = [0 for i in range(0, numOfWordsInLine + 1)]
        y[numOfWordsInLine] = maxR
        y[numOfWordsInLine - 1] = maxT
        # weird case...
        if numOfWordsInLine == 0:
            y[0] = 'O'
        for i in reversed(range(0, numOfWordsInLine - 1)):
            y[i] = BP[i + 2][y[i + 1]][y[i + 2]]
        if isTrain:
            for i, tag in enumerate(line):
                if len(tag) == 2:
                    global totalChecked
                    global totalCorrect
                    totalChecked += 1
                    if tag[1].lower() == y[i].lower():
                        totalCorrect += 1
            print(str(totalCorrect) + "/" + str(totalChecked) + " = " + str(float(totalCorrect) / totalChecked))
        if line != [['']]:
            outputLines.append(
                " ".join(map(lambda i: str(line[i][0]) + "/" + str(y[i].upper()), range(0, numOfWordsInLine + 1))))


def main():
    inputFile = sys.argv[1]
    modelFile = sys.argv[2]
    featureMap = sys.argv[3]
    outputFile = sys.argv[4]
    eFile = sys.argv[5]

    input = open(inputFile, "r").read().split('\n')
    featureMap = open(featureMap, "r").read().split('\n')

    eMLE = open(eFile, "r").read().split('\n')

    extractE(eMLE)

    listData = splitWord(input)

    extractFeat(featureMap)

    # load the model from disk
    model = pickle.load(open(modelFile, 'rb'))

    viterbiAlgo(listData, model);

    o = open(outputFile, 'w')
    o.write('\n'.join(outputLines))
    o.close()


if __name__ == "__main__":
    main()
