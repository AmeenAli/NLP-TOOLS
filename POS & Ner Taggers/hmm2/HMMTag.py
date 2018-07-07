import sys

isCheck = True if len(sys.argv) > 6 else False
totalCorrect = 0
totalChecked = 0


totalWords = 0
tagSet = set(["XX"])
qDictionaty = {}
eDictionaty = {}

eMap = {}
qMap = {}

output = []

isNer = 0


def splitTag(x):
    if not isCheck:
        return [x]
    index = x.rfind('/')
    return [x[:index], x[index + 1:].lower()]


def splitWord(lines):
    llist = []
    for i in lines:
        llist.append(list(map(splitTag, i.split(' '))))
    return llist;

def exstractEandQ(e, q):
    for line in e:
        global totalWords
        totalWords += len(line)
        part = line.split('\t')
        space = part[0].split(' ')
        if space[0] not in eMap:
            # not sure if it's supposed to be here
            eMap[space[0]] = {}
        eMap[space[0]][space[1]] = float(part[1])
        if space[1] is 'i-loc' or space[1] is 'i-org' or space[1] is 'o':
            global isNer
            isNer = 1
        tagSet.add(space[1])

    for line in q:
        part = line.split('\t')
        qMap[part[0]] = float(part[1])


def argMax(tagMap):
    value = list(tagMap.values())
    key = list(tagMap.keys())
    return key[value.index(max(value))]


def qEstimate(qMap, c, a, b):
    abc = a + " " + b + " " + c
    if abc in qDictionaty:
        return qDictionaty[abc]

    bcCount = 0
    abcCount = 0
    cCount = 0
    abCount = 1
    bCount = 1

    bc = b + " " + c
    ab = a + " " + b

    if c in qMap:
        cCount = qMap[c]

    if bc in qMap:
        bcCount = qMap[bc]

    if ab in qMap:
        abCount = qMap[ab]

    if abc in qMap:
        abcCount = qMap[abc]

    if b in qMap:
        bCount = qMap[b]

    qDictionaty[abc] = (abcCount / abCount) * 0.82 + (bcCount / bCount) * 0.15 + (cCount / totalWords) * 0.03

    return qDictionaty[abc]


def eEstimate(eMap, word, tag):
    wordtag = word + " " + tag
    if wordtag in eDictionaty:
        return eDictionaty[wordtag]

    if word not in eMap:
        word = "*UNK*"

    if tag in qMap:
        tagCount = qMap[tag]
    else:
        tagCount = 100000

    if tag in eMap[word]:
        eDictionaty[wordtag] = eMap[word][tag] / tagCount
        return eDictionaty[wordtag]

    eDictionaty[wordtag] = 0.5 / tagCount
    return eDictionaty[wordtag]


def scoreEstimate(word, tag, prev, prevprev):
    eScore = eEstimate(eMap, word, tag)
    qScore = qEstimate(qMap, tag, prevprev, prev)
    return eScore * qScore


# using word signatures for unseen words
def signWord(word, origword):
    if word[-3:] == 'ing':
        return ["vbg"]
    if any(map(lambda c: c == '-', word)):
        return ["jj"]
    if "O'" in word:
        return ["nnp"]
    if len(word) > 1 and all(map(lambda c: c.isupper(), origword)):
        return ["nnp"]
    if sum(map(lambda c: (1 if c.isdigit() else 0), word)) > float(len(word)) / 2:
        return ["cd"]
    if word in ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "zero"]:
        return ["cd"]
    if len(word) > 0 and origword[0].isupper():
        return ["nnp", "nn", "nns"]
    if word[-4:] == 'ings':
        return ["nns"]
    if word[-4:] == 'able' or word[-4:] == 'ible' or word[-4:] == 'less' or word[-3:] == 'ous':
        return ["jj"]
    if word[-2:] == 'ly':
        return ["rb"]
    if word[-3:] == 'ers':
        return ["nns"]
    if word[-4:] == 'tion' or word[-3:] == 'ist' or word[-2:] == 'ty' or word[-4:] == 'ship' or word[
                                                                                                -3:] == 'dom' or word[
                                                                                                                 -3:] == 'ism' or word[
                                                                                                                                  -4:] == 'ment' or word[
                                                                                                                                                    -4:] == 'ness' or word[
                                                                                                                                                                      -4:] == 'sion' or word[
                                                                                                                                                                                        -3:] == 'acy' or word[
                                                                                                                                                                                                         -4:] == 'ence' or word[
                                                                                                                                                                                                                           -4:] == 'ance':
        return ["nn"]
    if word[-3:] == 'est':
        if word[:-3] in eMap:
            if eMap[word[:-3]] == "jj":
                return ["jjs"]
        return ["rbs"]
    if word[-2:] == 'er':
        if word[:-2] in eMap:
            if eMap[word[:-2]] == "jj":
                return ["jjr"]
        return ["rbr"]
    if word[-2:] == 'en':
        return ["vbn"]
    if word in ["i", "you", "he", "she", "it"]:
        return ["prp"]
    if word in ["who", "what", "when", "where", "when", "whom", "whose", "how"]:
        return ["wp"]
    if word in ["and", "but", "or", "for", "no", "so", "yet"]:
        return ["cc"]
    if word[-1:] == 's':
        if word[:-1] in eMap:
            if eMap[word[:-1]] in ["vb", "vbp"]:
                return ["vbz"]
        return ["nns", "nnp"]
        if word[-2:] == 'ed':
            return ["vbd"]
    if word[-3:] == 'ize' or word[-3:] == 'ise' or word[-2:] == 'fy':
        return ["vb"]
    if word[-3:] == 'ish' or word[-3:] == 'ive' or word[-2:] == 'ic' or word[-4:] == 'ical' or word[
                                                                                               -3:] == 'ful' or word[
                                                                                                                -5:] == 'esque':
        return ['jj']
    return []


# viterbi algorithm with back pointers
def viterbiAlgo(listData):
    for line in listData:
        numOfWordsInLine = len(line) - 1
        # initializing..
        V = [{}] + [{} for word in line]
        for t in tagSet:
            V[0][t] = {}
            for r in tagSet:
                V[0][t][r] = 0

        V[0]["XX"]["XX"] = 1
        BP = [{}] + [{} for word in line]

        prevprev = ["XX"]
        prev = ["XX"]
        for i in range(0, numOfWordsInLine + 1):
            origword = line[i][0]
            word = origword.lower()
            currTagSet = list(tagSet)
            if word not in eMap and not isNer:
                if signWord(word, origword):
                    currTagSet = signWord(word, origword)
            elif word not in eMap:
                currTagSet = list(tagSet)
            else:
                currTagSet = list(eMap[word].keys())
            V[i + 1] = {}
            BP[i + 1] = {}

            for t in prev:
                V[i + 1][t] = {}
                BP[i + 1][t] = {}

                for r in currTagSet:
                    temp = {}
                    for rr in prevprev:
                        temp[rr] = (V[i][rr][t]) * scoreEstimate(word, r, t, rr)

                    V[i + 1][t][r] = max(list(temp.values()))
                    BP[i + 1][t][r] = argMax(temp)

            prevprev = prev
            prev = currTagSet

        V.pop(0)
        BP.pop(0)

        value = map(lambda x: x.values(), V[numOfWordsInLine].values())
        maxValue = list(map(max, value))
        maxV = max(maxValue)
        maxIndex = maxValue.index(maxV)
        maxI = list(V[numOfWordsInLine].keys())[maxIndex]
        maxJ = argMax(V[numOfWordsInLine][maxI])
        x = [0 for i in range(0, numOfWordsInLine + 1)]
        x[numOfWordsInLine] = maxJ
        x[numOfWordsInLine - 1] = maxI
        # handling a weird case...
        if numOfWordsInLine == 0:
            x[0] = 'O'
        for i in reversed(range(0, numOfWordsInLine - 1)):
            x[i] = BP[i + 2][x[i + 1]][x[i + 2]]
        # statistics
        if isCheck:
            for i, tag in enumerate(line):
                if len(tag) == 2:
                    global totalChecked
                    totalChecked += 1
                    if tag[1].lower() == x[i].lower():
                        global totalCorrect
                        totalCorrect += 1
                print(str(totalCorrect) + "/" + str(totalChecked) + " = " + str(float(totalCorrect) / totalChecked))
        # print to output
        if line != [['']]:
            output.append(
                " ".join(map(lambda i: str(line[i][0]) + "/" + str(x[i].upper()), range(0, numOfWordsInLine + 1))))


def main():
    inputFile = sys.argv[1]
    qFile = sys.argv[2]
    eFile = sys.argv[3]
    outputFile = sys.argv[4]
    extraFile = sys.argv[5]

    input = open(inputFile, "r").read().split('\n')
    q = open(qFile, "r").read().split('\n')
    e = open(eFile, "r").read().split('\n')
    listData = splitWord(input)
    exstractEandQ(e, q)

    viterbiAlgo(listData)

    outputF = open(outputFile, 'w')
    outputF.write('\n'.join(output))
    outputF.close()


if __name__ == "__main__":
    main()
