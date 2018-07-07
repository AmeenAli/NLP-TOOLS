import sys

eMap = {}
qMap = {}

outputLines = []

totalCorrect = 0
totalChecked = 0
isCheck = True if len(sys.argv) > 6 else False

def splitTag(x):
    if not isCheck:
        return [x]
    index = x.rfind('/')
    return [x[:index], x[index + 1:]]


def splitWord(lines):
    llist = []
    for i in lines:
        llist.append(list(map(splitTag, i.split(' '))))
    return llist;


def exstractToEandQ(e, q):
    for line in e:
        part = line.split('\t')
        space = part[0].split(' ')
        if space[0] not in eMap:
            eMap[space[0]] = {}
        eMap[space[0]][space[1]] = float(part[1])

    for line in q:
        part = line.split('\t')
        qMap[part[0]] = float(part[1])


def qScore(tag, prev, prevprev):
    one = 0
    two = 0
    three = 0

    if tag in qMap:
        one = float(qMap[tag])
    pair = prev + " " + tag
    if pair in qMap:
        two = float(qMap[pair])
    triplet = prevprev + " " + pair
    if triplet in qMap:
        three = float(qMap[triplet])

    return three * 0.83 + two * 0.15 + one * 0.02


def getScore(word, prev, prevprev):
    if word not in eMap:
        word = "*UNK*"

    tags = eMap[word]
    scores = {}
    for tag in tags:
        scores[tag] = float(tags[tag]) * qScore(tag, prev, prevprev)
    return scores


def argMax(tagMap):
    value = list(tagMap.values())
    key = list(tagMap.keys())
    return key[value.index(max(value))]


def greedyTagging(listData):
    for line in listData:
        tags = ["XX", "XX"]
        ll = []
        for wordNum, tag in enumerate(line):
            chosenTag = argMax(getScore(tag[0].lower(), tags[-1], tags[-2]))
            tags.append(chosenTag)
            if line != [['']]:
                ll.append(tag[0] + "/" + chosenTag.upper())
            if isCheck and len(tag) == 2:
                global totalChecked
                totalChecked += 1
                if tag[1].lower() == chosenTag.lower():
                    global totalCorrect
                    totalCorrect += 1
        if isCheck:
            print(str(totalCorrect) + "/" + str(totalChecked) + " = " + str(float(totalCorrect) / totalChecked))
        outputLines.append(" ".join(ll))


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
    exstractToEandQ(e, q)
    greedyTagging(listData)

    file = open(outputFile, 'w')
    file.write('\n'.join(outputLines))
    file.close()


if __name__ == "__main__":
    main()
