__author__ = 'ZeqiuWu'
import sys
import math
from multiprocessing import Process, Lock
from nlp_parse import parse
from ner_feature import pipeline, pipeline_qa, filter, pipeline_test
from pruning_heuristics import prune

def get_number(filename):
    with open(filename) as f:
        count = 0
        for line in f:
            count += 1
        return count

def multi_process_parse(fin, fout, isTrain, nOfNones):
    file = open(fin, 'r')
    sentences = file.readlines()
    sentsPerProc = int(math.floor(len(sentences)*1.0/numOfProcesses))
    lock = Lock()
    processes = []
    out_file = open(fout, 'w', 0)
    for i in range(numOfProcesses):
        if i == numOfProcesses - 1:
            p = Process(target=parse, args=(sentences[i*sentsPerProc:], out_file, lock, i, isTrain, nOfNones))
        else:
            p = Process(target=parse, args=(sentences[i*sentsPerProc:(i+1)*sentsPerProc], out_file, lock, i, isTrain, nOfNones))
        p.start()
        processes.append(p)
    for proc in processes:
        proc.join()
    out_file.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print 'Usage:feature_generation.py -DATA -numOfProcesses -feature_freq_threshold'
        exit(1)
    data = sys.argv[1]
    feature_freq_threshold = int(sys.argv[3])
    indir = 'data/source/%s' % data
    outdir = 'data/intermediate/%s/rm' % data

    numOfProcesses = int(sys.argv[2])
    # NLP parse

    raw_train_json = indir + '/train.json'
    raw_test_json = indir + '/test.json'
    train_json = outdir + '/train_new.json'
    test_json = outdir + '/test_new.json'
    qa_json = indir + '/qa.json'

    ### Generate features using Python wrapper (disabled if using run_nlp.sh)
    print 'Start nlp parsing'
    multi_process_parse(raw_train_json, train_json, True, 1)
    print 'Train set parsing done'
    multi_process_parse(raw_test_json, test_json, False, 1)
    print 'Test set parsing done'


    print 'Start rm feature extraction'
    pipeline(train_json, indir + '/brown', outdir, requireEmType=False, isEntityMention=False)
    pipeline_qa(qa_json, indir + '/brown', outdir+'/feature.map',outdir+'/type.txt', outdir, requireEmType=False, isEntityMention=False)
    filter(outdir+'/feature.map', outdir+'/train_x.txt', outdir+'/feature.txt', outdir+'/train_x_new.txt', feature_freq_threshold)
    filter(outdir+'/feature.map', outdir+'/qa_x.txt', outdir+'/feature.txt', outdir+'/qa_x_new.txt', feature_freq_threshold)
    pipeline_test(test_json, indir + '/brown', outdir+'/feature.txt',outdir+'/type.txt', outdir, requireEmType=False, isEntityMention=False)

    ### Perform no pruning to generate training data
    print 'Start rm training and test data generation'
    feature_number = get_number(outdir + '/feature.txt')
    type_number = get_number(outdir + '/type.txt')
    prune(outdir, outdir, 'no', feature_number, type_number, neg_label_weight=1.0, isRelationMention=True)

