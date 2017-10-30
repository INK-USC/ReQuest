## ReQuest: Indirect Supervision for Relation Extraction Using Question-Answer Pairs

Source code and data for WSDM'18 paper *[Indirect Supervision for Relation Extraction Using Question-Answer Pairs]*. 

## Performance
Performance comparison with several *relation extraction* systems over KBP 2013 dataset (**sentence-level extraction**). 

Method | Precision | Recall | F1 
-------|-----------|--------|----
Mintz (our implementation, [Mintz et al., 2009](http://web.stanford.edu/~jurafsky/mintz.pdf)) | 0.296 | 0.387 | 0.335 
LINE + Dist Sup ([Tang et al., 2015](https://arxiv.org/pdf/1503.03578.pdf)) | **0.360** | 0.257 | 0.299 
MultiR ([Hoffmann et al., 2011](http://raphaelhoffmann.com/publications/acl2011.pdf)) | 0.325 | 0.278 | 0.301 
FCM + Dist Sup ([Gormley et al., 2015](http://www.aclweb.org/anthology/D15-1205)) | 0.151 | **0.498** | 0.300 
CoType-RM ([Ren et al., 2017](https://arxiv.org/pdf/1610.08763v1.pdf)) | 0.342 | 0.339 | 0.340
ReQuest ([Wu et al., 2018]) | 0.386 | 0.410 | **0.397**

## Dependencies

We will take Ubuntu for example.

* python 2.7
* Python library dependencies
```
$ pip install pexpect ujson tqdm
```

* [stanford coreNLP 3.7.0](http://stanfordnlp.github.io/CoreNLP/) and its [python wrapper](https://github.com/stanfordnlp/stanza). Please put the library under `ReQuest/code/DataProcessor/'.

```
$ cd code/DataProcessor/
$ git clone git@github.com:stanfordnlp/stanza.git
$ cd stanza
$ pip install -e .
$ wget http://nlp.stanford.edu/software/stanford-corenlp-full-2016-10-31.zip
$ unzip stanford-corenlp-full-2016-10-31.zip
```
* [eigen 3.2.5](http://bitbucket.org/eigen/eigen/get/3.2.5.tar.bz2) (already included). 


## Data
We [process](https://github.com/shanzhenren/StructMineDataPipeline) (using our [data pipeline](https://github.com/shanzhenren/StructMineDataPipeline)) two public RE datasets to our JSON format. We ran [Stanford NER](https://nlp.stanford.edu/software/CRF-NER.shtml) on training set to detect entity mentions, and performed distant supervision using [DBpediaSpotlight](https://github.com/dbpedia-spotlight/dbpedia-spotlight) to assign type labels:

   * **NYT** ([Riedel et al., 2011](https://pdfs.semanticscholar.org/db55/0f7af299157c67d7f1874bf784dca10ce4a9.pdf)): 1.18M sentences sampled from 294K New York Times news articles. 395 sentences are manually annotated with 24 relation types and 47 entity types. ([Download JSON](https://drive.google.com/drive/folders/0B--ZKWD8ahE4UktManVsY1REOUk?usp=sharing))
   * **Wiki-KBP**: the training corpus contains 1.5M sentences sampled from 780k [Wikipedia articles](https://github.com/xiaoling/figer) ([Ling & Weld, 2012](http://xiaoling.github.io/pubs/ling-aaai12.pdf)) plus ~7,000 sentences from 2013 KBP corpus. Test data consists of 14k mannually labeled sentences from [2013 KBP slot filling](http://surdeanu.info/kbp2013/) assessment results. It has 13 relation types and 126 entity types after filtering of numeric value-related relations. ([Download JSON](https://drive.google.com/drive/folders/0B--ZKWD8ahE4RjFLUkVQTm93WVU?usp=sharing))

Please put the data files in corresponding subdirectories under `ReQuest/data/source`

We use the [answer sentence selection dataset](https://github.com/xuchen/jacana/tree/master/tree-edit-data/answerSelectionExperiments/data) from TREC QA as our source of indirect supervision. We ran Stanford NER to extract entity mentions on both question and answer sentences and process the dataset into JSON format containing QA-pairs. Details of how we construct QA-pairs can be found in our paper.

We provide the processed qa.json file and it should be put into each data folder under ReQuest/data/source. 

## Makefile
To compile `request.cpp` under your own g++ environment
```
$ cd ReQuest/code/Model/request; make
```

## Default Run & Parameters
Run ReQuest for the task of *Relation Extraction* on the Wiki-KBP dataset

Start the Stanford corenlp server for the python wrapper.
```
$ java -mx4g -cp "code/DataProcessor/stanford-corenlp-full-2016-10-31/*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer
```

Feature extraction, embedding learning on training data, and evaluation on test data.
```
$ ./run_kbp.sh  
```
The hyperparamters for embedding learning are included in the run_{dataname}.sh script.

## Evaluation
Evaluates relation extraction performance (precision, recall, F1): produce predictions along with their confidence score; filter the predicted instances by tuning the thresholds.
```
$ python code/Evaluation/emb_test.py extract KBP request cosine 0.0
$ python code/Evaluation/tune_threshold.py extract KBP emb request cosine
```
