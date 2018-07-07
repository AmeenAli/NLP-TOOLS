you should download punkt and wordnet packages for nltk in this way :
nltk.download("wordnet")
nltk.download("punkt")
you should also download spacy , scipy , numpy , nltk , sklearn.

*******************************************************************************
To train the model, run part1.py 
python part1.py CORPUS.TRAIN.txt TRAIN.annotations

this line will produce the model file that the extract.py will use in order to extract the relations.

To extract the relations, run extract.py:
Please use the .txt file
python extract.py CORPUS.TRAIN.txt train.annotations

It will write in train.annotations the extracted relations

*******************************************************************************

To evaluate, run eval.py:
python eval.py TRAIN.annotations train.annotations
in the following format
python eval.py gold pred
