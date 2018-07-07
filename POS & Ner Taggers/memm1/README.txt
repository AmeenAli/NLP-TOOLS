How to run our code:

----- ExtractFeatures
*********************
POS
python ExtractFeatures.py ../pos_data/ass1-tagger-train features_file

*********************
NER
python ExtractFeatures.py ../ner_data/train ../ner/features_file



----- ConvertFeatures
*********************
POS
python ConvertFeatures.py features_file feature_vecs feature_map

*********************
NER
python ConvertFeatures.py ../ner/features_file ../ner/feature_vecs ../ner/feature_map



----- TrainSolver
( sklearn, numpy, scipy, pickle )
*********************
POS
python TrainSolver.py feature_vecs model

*********************
NER
python TrainSolver.py ../ner/feature_vecs ../ner/model