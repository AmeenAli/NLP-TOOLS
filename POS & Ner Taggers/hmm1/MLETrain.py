import sys

eMap = {}
qMap = {}
length = [0, 1, 2]


def splitTag(x):
    index = x.rfind('/')
    return [x[:index], x[index + 1:]]


def splitWord(lines):
    llist = []
    for i in lines:
        llist.append(list(map(splitTag, i.split(' '))))
    return llist;


def extractData(listTag):
    for lineNum, line in enumerate(listTag):
        for wordNum, tag in enumerate(line):
            if len(tag) == 2:
                # what about unknown words??
                if tag[0] not in eMap:
                    if lineNum > 0.9 * len(listTag):
                        tag[0] = '*UNK*'
                    if tag[0] not in eMap:
                        eMap[tag[0]] = {}
                if tag[1] not in eMap[tag[0]]:
                    eMap[tag[0]][tag[1]] = 0
                eMap[tag[0]][tag[1]] += 1

                for i in range(0, 3):
                    sequence = ' '.join(map(lambda x: 'XX' if (x < 0) else line[x][1], range(wordNum - i, wordNum + 1)))
                    if sequence not in qMap:
                        qMap[sequence] = 0
                    qMap[sequence] += 1


def main():
    trainFile = sys.argv[1]
    qFile = sys.argv[2]
    eFile = sys.argv[3]

    file = open(trainFile, "r")
    lines = file.read().lower().split('\n')
    listTag = splitWord(lines)

    #extract to eMap and qMap
    extractData(listTag)

    # printing to files
    qPrint = []
    for key in qMap:
        qPrint.append(key + '\t' + str(qMap[key]))

    ePrint = []
    for key in eMap:
        for tag in eMap[key]:
            ePrint.append(key + ' ' + tag + '\t' + str(eMap[key][tag]))

    q = open(qFile, 'w')
    q.write('\n'.join(qPrint))
    q.close()

    e = open(eFile, 'w')
    e.write('\n'.join(ePrint))
    e.close()


if __name__ == "__main__":
    main()
