from sklearn.datasets import load_svmlight_file
from sklearn.linear_model import LogisticRegression
import sys
import pickle

features = sys.argv[1]
model = sys.argv[2]
firstTrain , secondTrain = load_svmlight_file(features)
myModel = LogisticRegression(penalty='l2')
myModel.fit(firstTrain , secondTrain)
pickle.dump(myModel , open(model , 'wb'))
