"""
Usage: word2vec.py  <WORDS_FILE> <CONTEXT_FILE>

-h --help   show this
"""

from docopt import docopt
import numpy
import part1

targetWords = ["car", "bus", "hospital", "hotel", "gun", "bomb", "horse", "fox", "table", "bowl", "guitar",
                    "piano"]

class CosineCache:
    def __init__(self):
        self.root={}
        self.dot={}

    def rootCache(self, u,uVec):
        if not self.root.__contains__(u):
            self.root[u]=numpy.sqrt(numpy.dot(uVec, uVec))
        return self.root[u]

    def dotCache(self, u, v, uVec,vVec):
        if not self.dot.__contains__((u,v)):
            self.dot[(u,v)] = self.dot[(v,u)]=numpy.dot(uVec,vVec)
        return self.dot[(u,v)]

    def cosDistance(self, u, v, uVec, vVec):
        uRoot=self.rootCache(u,uVec)
        vRoot=self.rootCache(v,vVec)
        uvDot=self.dotCache(u,v,uVec,vVec)
        return uvDot/(vRoot*uRoot)



def loadArr(word2int, file):
    f=open(file,'r')
    for line in f:
        width=len(line.split())-1
        break;
    height=1
    for line in f:
        height+=1

    wordsArr=numpy.ndarray(shape=(height,width), dtype=numpy.float32)
    row=0
    f=open(file,'r')
    wordsIds=[]
    for line in f:
        lineArr=line.split()
        wId=word2int.getIdAndUpdate(lineArr[0])
        wordsArr[row]=lineArr[1:]
        wordsIds.append(wId)
        row+=1
    return wordsArr


def loadFromFile(wordsFile,contextFile):
    word2int=part1.StringToNum()
    context2int=part1.StringToNum()
    words=loadArr(word2int, wordsFile)
    contexts=loadArr(context2int, contextFile)
    return word2int,context2int, words, contexts


if __name__=='__main__':
    args=docopt(__doc__, version='Naval Fate 2.0')
    wordsFile=args['<WORDS_FILE>']
    contextFile=args['<CONTEXT_FILE>']

    print("Loading input files...")
    word2int, context2int, words, contexts = loadFromFile(wordsFile,contextFile)

    numWords=20
    int2word=part1.inverseDic(word2int.string2num)
    int2context=part1.inverseDic(context2int.string2num)

    print("\nprinting first order")

    cosCache=CosineCache()
    for word in targetWords:
        wordID=word2int.getId(word)
        vec=words[wordID,:]
        distances={int2context[i] : cosCache.dotCache(word, int2context[i], vec, contexts[i,:]) for i in range(0,contexts.shape[0])}
        distancesTuples=sorted(distances.items(), key=lambda x:x[1], reverse=True)
        distancesTuples=[x for x,y in distancesTuples]
        print word,distancesTuples[1:numWords+1]

    del cosCache

    print("\nprinting second order")

    cosCache = CosineCache()
    for word in targetWords:
        wordID = word2int.getId(word)
        vec = words[wordID, :]
        distances = {int2word[i]: cosCache.cosDistance(word, int2word[i], vec, words[i, :]) for i in
                     range(0, words.shape[0])}
        distancesTuples = sorted(distances.items(), key=lambda x: x[1], reverse=True)
        distancesTuples = [x for x, y in distancesTuples]
        print word, distancesTuples[1:numWords + 1]
