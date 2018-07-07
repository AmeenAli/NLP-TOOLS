import sys
import time
import random

startTime = time.time()
errorCheck = True
targetTag = 'Live_In'

def readAnnotationFile(name_file):
    annotations = []
    sentences = open(name_file, "r").read().split("\n")
	
    for sentence in sentences:
        if sentence != "":
            sentence = sentence.split("(")[0]
            nextId = sentence.split("\t")[0].replace("sent", "")
            sentence = sentence.replace("sent"+ str(nextId) + "\t", "")
            if targetTag in sentence:
                person, location = sentence.split(targetTag)
                person = person.replace("\t", "")
                location = location.replace("\t", "")
                annotations.append(nextId + " " +  person + " " + targetTag + " " + location )
	
    return annotations

def passedTime(previous_time):
    return round(time.time() - previous_time, 3)



def errorCheck(mistakes):
    to_extract = min(40, len(mistakes))
    to_analyse = random.sample(mistakes, to_extract)
    for errors in to_analyse:
        print "Relation :"
        print errors


def precision(goldData, predData):
    good = 0.0
    bad = 0.0
	
    mistakes = []
	
    for pred in predData:
        left, right = pred.split(" " + targetTag)
        other_pred = left + ". " + targetTag + right
		
        if pred in goldData or pred + "." in goldData or other_pred in goldData:
            good += 1
        else:
            bad += 1
            mistakes.append(pred)
			
    if errorCheck:
        print "="*20
        print "PRECISION ERRORS (not in gold)"
        print "="*20
        errorCheck(mistakes)
    return good/(good+bad)

	
def recall(goldData, predData):
    good = 0.0
    bad = 0.0
    mistakes = []
    for gold in goldData:
        left, right = gold.split(" " + targetTag)
        if left[-1] == ".":
            left = left[:-1]
            other_gold = left + " " + targetTag + right
        else:
            other_gold = left + ". " + targetTag + right
        if gold in predData  or gold + "." in predData or other_gold in predData:
            good += 1
        else:
            bad += 1
            mistakes.append(gold)
    if errorCheck:
        print "="*20
        print "RECALL ERRORS (not in pred)"
        print "="*20
        errorCheck(mistakes)
		
    return good/(good+bad)


if __name__ == '__main__':

    goldFile = sys.argv[1]
    predictedFile = sys.argv[2]
    goldData = readAnnotationFile(goldFile)
    predData = readAnnotationFile(predictedFile)
    prec = precision(goldData, predData)
    print "Precision is " + str(prec)
    rec = recall(goldData, predData)
    print "Recall is " + str(rec)
    f1 = (2*prec*rec)/(prec+rec)
    print "="*20
    print "F1 is " + str(f1)
