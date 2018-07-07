"""
Usage: main.py  <INPUT_FILE> [-m mode_num]

-h --help   show this
-m mode_number    mode: 1=sentence, 2=window, 3=tree [default: 1]
"""


from docopt import docopt
import pickle
import time
import numpy

modes={1:"sentence", 2:"window", 3:"tree"}
POS=set(['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'JJ', 'JJR', 'JJS', 'VBZ', 'WRB'])
targetWords = ["car" ,"bus" ,"hospital" ,"hotel" ,"gun" ,"bomb" ,"horse" ,"fox" ,"table", "bowl", "guitar" ,"piano"]

class StringToNum:
    def __init__(self, initialList=[], unkWord=None):
        from collections import Counter
        self.string2num={}
        self.string2count=Counter()
        self.counter=0
        self.unkWord=unkWord
        for str in initialList:
            self.getIdAndUpdate(str)

    def getIdAndUpdate(self, str, count=1):
        if not self.string2num.__contains__(str):
            self.string2num[str] = self.counter
            self.counter+=1
        self.string2count[str]=self.string2count.get(str,0)+count
        return self.string2num[str]

    def getId(self,str):
        if not self.string2num.__contains__(str):
            str=self.unkWord
        return self.string2num[str]

    def filterWords(self,threshold):
        toFilter=[w for w,t in self.string2count.iteritems() if t<threshold]
        for w in toFilter:
            self.string2count.pop(w)
            self.string2num.pop(w)
        self.getIdAndUpdate(self.unkWord)

    def len(self):
        return len(self.string2num)

    def shiftIDByN(self, n):
        string2numTemp={}
        for w, t in self.string2num.iteritems():
            string2numTemp[w]=t+n
        self.string2num=string2numTemp



class Processing:
    def __init__(self, word2num, context):
        self.word2num=word2num
        self.context=context

    def saveToOutput(self, pickleName):
        saveObject((self.word2num,self.context), pickleName)

    def loadFile(pickleName):
        word2num, context = loadObject(pickleName)
        return Processing(word2num, context)






def saveObject(obj, file):
    f=open(file, 'wb+')
    pickle.dump(obj,f, pickle.HIGHEST_PROTOCOL)

def loadObject(file):
    f=open(file, 'rb')
    return pickle.load(f)

def inverseDic(dic):
    return {y: x for x,y in dic.iteritems()}


def corpusLemmaToID(file, unkWord):
    inputFile=open(file, 'r')
    word2num = StringToNum(unkWord=unkWord)
    for line in inputFile:
        line = line.strip()
        if len(line)>0:
            words=line.split()
            lemma = words[2]
            word2num.getIdAndUpdate(lemma)
    word2num.filterWords(100)
    word2num=StringToNum(word2num.string2num.keys(), word2num.unkWord)
    return word2num

def updateContextPair(context, (x,y)):
    contexts=context.get(x)
    if not contexts:
        contexts=context[x]={}
    contexts[y]=contexts.get(y,0)+1

def List2Tuples(list, tupleSize):
    from itertools import tee, izip
    tupIterator=tee(list,tupleSize)
    for i,itr in enumerate(tupIterator):
        for j in range(0,i):
            next(itr,None)
    return izip(*tupIterator)

def sentenceToWindow(sentence, windowSize):
    windows=[]
    for window in List2Tuples(sentence, windowSize * 2 +1):
        windows.append(window)
    return windows


def updateContextSentence(context, sentence, unkId):
    sentenceLemmas = [sentence[i+1][0] for i in range(0,len(sentence)) if sentence[i+1][1] in POS and sentence[i+1][0] != unkId]
    for lemma in sentenceLemmas:
        for lemma_context in sentenceLemmas:
            if lemma!=lemma_context:
                updateContextPair(context,(lemma,lemma_context))


def updateContextWindow(context, sentence,unkId, windowSize):
    sentenceLemmas = [sentence[i+1][0] for i in range(0,len(sentence)) if sentence[i+1][1] in POS and sentence[i+1][0] != unkId]
    sentenceLemmas = [None] * windowSize + sentenceLemmas + [None] * windowSize
    windows=sentenceToWindow(sentenceLemmas, windowSize)
    for w in windows:
        lemmaId=w[windowSize]
        for lemmaContext in w:
            if lemmaId!=lemmaContext and lemmaContext is not None:
                updateContextPair(context, (lemmaId, lemmaContext))


def updateContextTree(context, sentence, unkId,prepPos, word2numTree):
    for word_id, word in sentence.items():
        if word[0] != unkId and (word[1] in POS):
            currId=str(word[0])
            parentId=word[3]
            addition = ""
            while (parentId!=0 and sentence[parentId][0]==unkId):
                parentId=sentence[parentId][3]
            if parentId==0:
                parentKind="*ROOT*"
            else:
                parentNode=sentence[parentId]
                if parentNode[1]==prepPos:
                    addition="{} {}".format(parentNode[2], str(parentNode[0]))
                    grandparentId=parentNode[3]
                    while (grandparentId != 0 and sentence[grandparentId][0]==unkId):
                        grandparentId = sentence[grandparentId][3]
                    if grandparentId==0:
                        parentKind="*ROOT*"
                    else:
                        grandparentNode = sentence[grandparentId]
                        parentKind = str(grandparentNode[0])
                else:
                    parentKind=str(parentNode[0])
            currDep=word[2]

            up_content_id = word2numTree.getIdAndUpdate(currId)
            up_feature_id = word2numTree.getIdAndUpdate(" ".join([addition, parentKind, currDep, "up"]))
            down_content_id = word2numTree.getIdAndUpdate(parentKind)
            down_feature_id = word2numTree.getIdAndUpdate(" ".join([addition, currId, currDep, "down"]))

            updateContextPair(context, (up_content_id, up_feature_id))
            updateContextPair(context, (up_feature_id, up_content_id))
            updateContextPair(context, (down_content_id, down_feature_id))
            updateContextPair(context, (down_feature_id, down_content_id))


def corpusLemmaToContext(file, word2num, prepPos, unkWord, min=None, contextMode="sentence"):
    unkId=word2num.getId(unkWord)
    word2numTree=StringToNum()
    context={}
    if contextMode=="sentence":
        update=lambda contexts, sentence: updateContextSentence(context, sentence, unkId)
    else:
        if contextMode == "window":
            update = lambda contexts, sentence: updateContextWindow(context, sentence,unkId, windowSize=2)

        else:
            if contextMode == "tree":
                update = lambda contexts, sentence: updateContextTree(context, sentence,unkId,prepPos, word2numTree)
            else:
                raise Exception("Unknown context mode :(")

    inputFile=open("" + file, 'r')
    sentence = {}
    isEmptyLine= True
    for line in inputFile:
        line=line.strip()
        if len(line)>0:
            isEmptyLine=False
            wordsArray=line.split()
            id = int(wordsArray[0])
            lemma=wordsArray[2]
            pos=wordsArray[3]
            lemmaId=word2num.getId(lemma)
            headId=wordsArray[6]
            deprel=wordsArray[7]
            sentence[id]= (lemmaId, pos, deprel, int(headId))
        else:
            if not isEmptyLine:
                update(context, sentence)
                sentence={}
            isEmptyLine=True
    update(context, sentence)

    if min is not None:
        for wordId, wordContext in context.items():
            filter=[wordIdContext for wordIdContext, count in wordContext.items() if count< min]
            for wordIdContext in filter:
                wordContext.pop(wordIdContext)
        filter=[]
        for wordId, wordContext in context.items():
            if len(wordContext)==0:
                filter.append(wordId)
        for wordId in filter:
            context.pop(wordId)

    return word2numTree, context




def processInput(file, modeAux):
    word2num = corpusLemmaToID(file, unkWord="*UNK*")
    context=corpusLemmaToContext(file,word2num, "IN", unkWord="*UNK*", min=2, contextMode=modeAux)
    return Processing(word2num, context)


def contexts2PMIContexts(context):
    import copy
    freqs = {}
    context = copy.deepcopy(context)
    freqTotal = 0
    for u,u_context in context.items():
        ufreqTotal = 0
        for __, uvfreq in u_context.items():
            ufreqTotal += uvfreq
        freqs[u] = ufreqTotal
        freqTotal += ufreqTotal

    sum_all_p = numpy.float64(0.0)
    sum_all_p_u = numpy.float64(0.0)

    filter = []
    for u, u_context in context.items():
        p_u = float(freqs[u]) / freqTotal
        sum_all_p_u += p_u
        for v, uvfreq in u_context.items():
            p_v = float(freqs[v]) / freqTotal
            p_u_v = float(uvfreq) / freqTotal
            sum_all_p += p_u_v
            u_v_pmi = numpy.log(p_u_v) - (numpy.log(p_u) + numpy.log(p_v))
            if u_v_pmi < 0:
                filter.append((u,v))
            u_context[v] = u_v_pmi
    assert abs(sum_all_p_u -1) < 0.001
    assert abs(sum_all_p - 1) < 0.001
    # Filter negative pmis
    for (u,v) in filter:
        context[u].pop(v, None)
        context[v].pop(v, None)

    filter = []
    for w_id, w_context in context.items():
        if len(w_context) == 0:
            filter.append(w_id)
    for w_id in filter:
        context.pop(w_id)
    return context


def calcCosineDistance(context, targetWordsIds):
    print("Cosine distance, length of every vectors")
    lengths = {}
    for u, u_context in context.items():
        sum = 0.0
        for __, u_v_count in u_context.items():
            sum += numpy.log(u_v_count) ** 2
        lengths[u] = sum

    print("Cosine distance, dot product")
    DotPro = {}
    for u in targetWordsIds:
        u_context = context[u]
        for att, u_att_count in u_context.items():
            for v, v_att_count in context[att].items():
                n = numpy.log(u_att_count) * numpy.log(v_att_count)
                DotPro[(u,v)] = DotPro.get((u,v), 0.0) + n

    print("Cosine distance: similarity...")
    sim = {}
    for u in targetWordsIds:
        u_context = context[u]
        sim[u] = {}
        for a in u_context:
            for v in context[a]:
                if u != v:
                    sim[u][v] = DotPro[(u,v)] / numpy.sqrt(lengths[u] * lengths[v])
    return sim


if __name__ == '__main__':
    args = docopt(__doc__, version='Naval Fate 2.0')
    file=args['<INPUT_FILE>']
    modeNum=int(args['-m'])
    if modeNum not in modes:
        print("Illegal mode")
        exit()

    calcProcessing = True
    calcSimiliarties = True
    saveOutput = False
    mode = modes[modeNum]
    print("The selected mode is " + mode + " you will find the output in "+mode+"_out")
    out_dir = "../output/{}_out".format(mode)

    print("Processing input file")
    if calcProcessing:
        currTime=time.time()
        processedData = processInput("" + file, modeAux=mode)
        if saveOutput:
            processedData.saveToOutput(out_dir+"/processed.pickle")
        afterTime=time.time()
        print("Done in %.2f secs " %(afterTime-currTime))
    else:
        processedData=Processing.loadFile(out_dir+"/processed.pickle")

    targetWordsId = [processedData.word2num.getId(w) for w in targetWords]

    word2numTree, context=processedData.context

    num2word=inverseDic(processedData.word2num.string2num)

    if mode=="tree":
        targetWordsId=[word2numTree.getId(str(id)) for id in targetWordsId]
        num2wordTree=inverseDic(word2numTree.string2num)
        inv= lambda u: " ".join([num2word[int(s)] if s.isdigit() else s for s in num2wordTree[u].split()])
    else:
        inv = lambda u: num2word[u]

    print("Converting frequencies to PMIs, calculating cosine distances")
    if calcSimiliarties:
        pmiContext=contexts2PMIContexts(context)
        sim=calcCosineDistance(pmiContext, targetWordsId)
        if saveOutput:
            saveObject(sim,out_dir+"/sim_pmi.pickle")
    else:
        pmiContext=contexts2PMIContexts(context)
        sim = loadObject(out_dir+"/sim_pmi.pickle")

    print("first order similarity:")
    for w in targetWordsId:
        wSortPMI=sorted(list(pmiContext[w].items()), key=lambda (v,score): score, reverse=True)
        wPMITop20=[inv(v) for i, (v,score) in enumerate(wSortPMI) if i<20]
        print(inv(w), wPMITop20)

    print("second order similarity:")
    for w in targetWordsId:
        wSim=set([])
        for uAtt in pmiContext[w]:
            for v in pmiContext[uAtt]:
                if w!=v:
                    wSim.add((v, sim[w][v]))
        wSim=sorted(list(wSim), key=lambda (v,score): score, reverse=True)
        wPMITop20=[inv(v) for i, (v,score) in enumerate(wSim) if i<20]
        print(inv(w), wPMITop20)

    print("Fennito!!!!!")




