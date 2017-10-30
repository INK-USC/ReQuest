Data=KBP
echo $Data

mkdir -pv data/intermediate/$Data/em
mkdir -pv data/intermediate/$Data/rm
mkdir -pv data/results/$Data/em
mkdir -pv data/results/$Data/rm

### Generate features
echo 'Step 1 Generate Features'
python code/DataProcessor/feature_generation.py $Data 10 2
echo ' '

### Train ReType on Relation Classification
echo 'Step 2 Train ReQuest on Relation Classification'
code/Model/request/request -data $Data -mode m -size 50 -negative 3 -threads 20 -alpha 0.0001 -samples 1 -iters 1000 -lr 0.015 -qaMFWeight 3.0 -qaMMWeight 3.0

### Evaluate ReType on Relation Classification
echo 'Step 3 Evaluate ReQuest on Relation Classification'
python code/Evaluation/emb_test.py $Data request cosine 0.0
echo ' '
python code/Evaluation/tune_threshold.py $Data emb request cosine
