import sys
import pickle
import numpy

isCheck = True if len(sys.argv) > 5 else False

totalChecked = 0
totalCorrect = 0

output = []

featuresMap = {}
reversedFeaturesMap = {}


def splitTag(x):
    if not isCheck:
        return [x]
    index = x.rfind('/')
    return [x[:index], x[index + 1:]]


def splitWord(lines):
    llist = []
    for i in lines:
        llist.append(list(map(splitTag, i.split(' '))))
    return llist


# mapping the features from the feature file - straight mapping and reversed
def mappingFeatures(features):
    for line in features:
        part = line.split(' ')
        featuresMap[part[0]] = int(part[1])
        reversedFeaturesMap[part[1]] = part[0]


def getFeatures(Wi, WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore, TiBeforeBefore):
    featuress = {}
    wordLength = len(Wi)
    for i in range(0, 4):
        if wordLength > i:
            featuress['prefix' + str(i + 1)] = Wi[:i + 1]
            featuress['suffix' + str(i + 1)] = Wi[wordLength - i - 1:]
    featuress['contains_number'] = any(char.isdigit() for char in Wi)
    featuress['contains_uppercase'] = any(char.isupper() for char in Wi)
    featuress['contains_hyphen'] = True if ('-' in Wi) else False
    featuress['Wi'] = Wi.lower()
    featuress['TiBefore'] = TiBefore
    featuress['TiBeforeBefore'] = TiBeforeBefore + '/' + TiBefore

    if WiBefore is not None:
        featuress['WiBefore'] = WiBefore.lower()
    if WiBeforeBefore is not None:
        featuress['WiBeforeBefore'] = WiBeforeBefore.lower()
    if WiAfterAfter is not None:
        featuress['WiAfterAfter'] = WiAfterAfter
    if WiAfter is not None:
        featuress['WiAfter'] = WiAfter

    return featuress


def predict(Wi, WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore, TiBeforeBefore, model):
    featuresVec = numpy.zeros(len(featuresMap) - 1)
    featuress = getFeatures(Wi, WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore, TiBeforeBefore)
    for key, feature in featuress.items():
        name = key + '=' + str(feature)
        if name in featuresMap:
            featuresVec[featuresMap[name] - 1] = 1
    return model.predict([featuresVec])


def greedyAlgo(listData, model):
    for line in listData:
        tags = ["XX", "XX"]
        linePrint = []
        lineLength = len(line)
        if line == [['']]:
            continue
        for i, tag in enumerate(line):
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
            TiBefore = tags[-1]
            TiBeforeBefore = tags[-2]

            newTagIndex = predict(tag[0], WiBefore, WiBeforeBefore, WiAfter, WiAfterAfter, TiBefore, TiBeforeBefore,
                                  model)
            newTag = reversedFeaturesMap[str(int(newTagIndex[0]))]
            tags.append(newTag)
            linePrint.append((tag[0] + "/" + newTag.upper()))
            if isCheck and len(tag) == 2:
                global totalChecked
                totalChecked += 1
                if tag[1] == newTag:
                    global totalCorrect
                    totalCorrect += 1

        if isCheck:
            print(str(totalCorrect) + "/" + str(totalChecked) + "=" + str(float(totalCorrect) / totalChecked))

        output.append(" ".join(linePrint))


def main():
    inputFile = sys.argv[1]
    modelFile = sys.argv[2]
    featureFile = sys.argv[3]
    outputFile = sys.argv[4]

    input = open(inputFile, "r").read().split('\n')
    features = open(featureFile, "r").read().split('\n')

    # splitting the input data
    listData = splitWord(input)

    mappingFeatures(features)

    # loading the model file
    # Prepare the feature vector for prediction
    model = pickle.load(open(modelFile, 'rb'))

    greedyAlgo(listData, model)

    o = open(outputFile, 'w')
    o.write('\n'.join(output))
    o.close()


if __name__ == "__main__":
    main()
