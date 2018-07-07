How to run our code:

----- Greedy


*********************
POS

python GreedyTag.py ../pos_data/ass1-tagger-test-input ../hmm1/q.mle ../hmm1/e.mle out-test-input extra

** To print accuracy to ass1-tagger-test or ass1-tagger-train, just add a word at the end of the command line, for example:

python GreedyTag.py ../pos_data/ass1-tagger-test ../hmm1/q.mle ../hmm1/e.mle out-test-input extra accuracy


*********************
NER

python GreedyTag.py ../ner_data/test.blind ../hmm1/q-ner.mle ../hmm1/e-ner.mle out-test-ner-input extra


** to get accuracy

python GreedyTag.py ../ner_data/dev ../hmm1/q-ner.mle ../hmm1/e-ner.mle out-test-ner-input extra accuracy


----- HMMTag

*********************
POS

python HMMTag.py ../pos_data/ass1-tagger-test-input ../hmm1/q.mle ../hmm1/e.mle out-test-input extra

** To print accuracy to ass1-tagger-test or ass1-tagger-train, just add a word at the end of the command line, for example:

python HMMTag.py ../pos_data/ass1-tagger-test-input ../hmm1/q.mle ../hmm1/e.mle out-test-input extra accuracy


*********************
NER

python HMMTag.py ../ner_data/test.blind ../ner/q.mle ../ner/e.mle ../ner/out-test-ner-input extra

** to get accuracy

python HMMTag.py ../ner_data/dev ../ner/q.mle ../ner/e.mle ../ner/out-test-ner-input extra accuracy


