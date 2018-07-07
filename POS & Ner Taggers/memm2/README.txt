How to run our code:

----- GreedyMaxEntTag
*********************
POS
python GreedyMaxEntTag.py ../pos_data/ass1-tagger-test ../memm1/model ../memm1/feature_map out_greedy extra

*********************
NER
python GreedyMaxEntTag.py ../ner_data/dev ../ner/model ../ner/feature_map ../out_greedy_dev extra accuracy 



----- MEMMTag
our extra file is e.mle 
*********************
POS
python MEMMTag.py ../pos_data/ass1-tagger-test-input ../memm1/model ../memm1/feature_map out ../hmm1/e.mle

** to check accuracy add a word at the end of the commandline
python MEMMTag.py ../pos_data/ass1-tagger-test ../memm1/model ../memm1/feature_map out ../hmm1/e.mle accuracy

*********************
NER

python MEMMTag.py ../ner/test.blind ../ner/model ../ner/feature_map ../ner/ner.memm.pred ../ner/e.mle

*** to check accuracy:
python MEMMTag.py ../ner/dev ../ner/model ../ner/feature_map ../ner/ner.memm.pred ../ner/e.mle accuracy