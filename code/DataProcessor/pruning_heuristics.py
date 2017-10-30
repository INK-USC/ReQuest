import os
import operator
import sys
from collections import defaultdict
reload(sys)
sys.setdefaultencoding('utf8')

class PruneStrategy:
    def __init__(self, strategy):
        self._strategy = strategy
        self.pruner = self.no_prune

    def no_prune(self, fileid, is_ground, labels):
        new_labels = set(labels)
        return list(new_labels)

def prune(indir, outdir, strategy, feature_number, type_number, neg_label_weight, isRelationMention):
    prune_strategy = PruneStrategy(strategy=strategy)

    type_file = open((os.path.join(indir+'/type.txt')), 'r')
    negLabelIndex = -1
    for line in type_file:
        seg = line.strip('\r\n').split('\t')
        if seg[0] == "None":
            negLabelIndex = int(seg[1])
            print "neg label : ", negLabelIndex
            break

    mids = {}
    ground_truth = set()
    count = 0
    train_y = os.path.join(indir+'/train_y.txt')
    train_x = os.path.join(indir+'/train_x_new.txt')
    qa_x = os.path.join(indir+'/qa_x_new.txt')
    test_x = os.path.join(indir+'/test_x.txt')
    test_y = os.path.join(indir+ '/test_y.txt')
    mention_file = os.path.join(outdir+ '/mention.txt')
    mention_type = os.path.join(outdir+ '/mention_type.txt')
    mention_feature = os.path.join(outdir+ '/mention_feature.txt')
    mention_type_test = os.path.join(outdir+'/mention_type_test.txt')
    mention_feature_test = os.path.join(outdir+ '/mention_feature_test.txt')
    feature_type = os.path.join(outdir+ '/feature_type.txt')

    qa_pair = os.path.join(indir+'/qa_pair.txt')
    qa_mpair = os.path.join(indir+'/qa_mpair.txt')
    mention_file_qa = os.path.join(outdir+ '/mention_qa.txt')
    mention_feature_qa = os.path.join(outdir+ '/mention_feature_qa.txt')
    feature_feature_qa = os.path.join(outdir+ '/feature_feature_qa.txt')
    mention_question = os.path.join(indir+'/mention_question.txt')
    mention_pairs = os.path.join(indir+'/mention_pairs_qa.txt')
    # generate mention_type, and mention_feature for the training & qa corpus
    with open(train_x) as fx, open(train_y) as fy, open(test_y) as ft, \
        open(mention_type,'w') as gt, open(mention_feature,'w') as gf:
        for line in ft:
            seg = line.strip('\r\n').split('\t')
            ground_truth.add(seg[0])
        # generate mention_type and mention_feature
        for line in fy:
            line2 = fx.readline()
            seg = line.strip('\r\n').split('\t')
            seg_split = seg[0].split('_')
            fileid = '_'.join(seg_split[:-3])
            labels = [int(x) for x in seg[1].split(',')]
            new_labels = prune_strategy.pruner(fileid=fileid, is_ground=(seg[0] in ground_truth), labels=labels)
            if new_labels is not None:
                seg2 = line2.strip('\r\n').split('\t')
                if len(seg2) != 2:
                    print seg2
                try:
                    features = seg2[1].split(',')
                except:
                    features = [] #may have empty features after feature filtering
                if seg[0] in mids:
                    continue
                for l in new_labels:
                    if l == negLabelIndex:  # discount weight for None label (index is 1)
                        gt.write(str(count)+'\t'+str(l)+'\t' + str(neg_label_weight) + '\n')
                    else:
                        gt.write(str(count)+'\t'+str(l)+'\t1\n')
                for f in features:
                    gf.write(str(count)+'\t'+f+'\t1\n')
                mids[seg[0]] = count
                count += 1
                if count%200000==0:
                    print count
    print count

    print 'start qa'
    count_qa = 0
    mids_qa = {}
    with open(qa_x) as fx, open(mention_feature_qa, 'w') as gmf:
        for line in fx:
            seg = line.strip('\r\n').split('\t')
            if len(seg) != 2:
                print seg
            try:
                features = seg[1].split(',')
            except:
                features = [] #may have empty features after feature filtering
            if seg[0] in mids_qa:
                continue
            for f in features:
                gmf.write(str(count_qa)+'\t'+f+'\t1\n')
            mids_qa[seg[0]] = count_qa
            count_qa += 1
            if count_qa%200000==0:
                print count_qa
    print count_qa
    # generate mention_type_test, and mention_feature_test for the test corpus
    print count
    print 'start test'
    with open(test_x) as fx, open(test_y) as fy,\
        open(mention_type_test,'w') as gt, open(mention_feature_test, 'w') as gf:
        # generate mention_type and mention_feature
        for line in fy:
            line2 = fx.readline()
            seg = line.strip('\r\n').split('\t')
            try:
                labels = [int(x) for x in seg[1].split(',')]
            except:
                labels = [] ### if it's negative example (no type label), make it a []
            seg2 = line2.strip('\r\n').split('\t')
            features = seg2[1].split(',')
            if seg[0] in mids:
                mid = mids[seg[0]]
            else:
                mid = count
               # print line2
                mids[seg[0]] = count
                count += 1
            for l in labels:
                gt.write(str(mid)+'\t'+str(l)+'\t1\n')
            for f in features:
                gf.write(str(mid)+'\t'+f+'\t1\n')
    print count
    print 'start mention part'
    # generate mention.txt
    with open(mention_file,'w') as m:
        sorted_mentions = sorted(mids.items(), key=operator.itemgetter(1))
        for tup in sorted_mentions:
            m.write(tup[0]+'\t'+str(tup[1])+'\n')
    '''
    if isRelationMention:
        entity_mention_file = os.path.join(emDir+ '/mention.txt')
        triples_file = os.path.join(outdir+ '/triples.txt')
        with open(entity_mention_file, 'r') as emFile, open(triples_file, 'w') as triplesFile:
            emIdByString ={}
            for line in emFile.readlines():
                seg = line.strip('\r\n').split('\t')
                emIdByString[seg[0]] = seg[1]
            for tup in sorted_mentions:
                seg = tup[0].split('_')
                em1id = emIdByString['_'.join(seg[:-2])]
                em2id = emIdByString['_'.join(seg[:2]+seg[-2:])]
                rmid = tup[1]
                triplesFile.write(em1id+'\t'+em2id+'\t'+str(rmid)+'\n')
    '''

    print 'start mention_qa part'
    # generate mention.txt
    with open(mention_file_qa,'w') as m:
        sorted_mentions_qa = sorted(mids_qa.items(), key=operator.itemgetter(1))
        for tup in sorted_mentions_qa:
            m.write(tup[0]+'\t'+str(tup[1])+'\n')

    print 'start feature_type part'
    with open(mention_feature) as f1, open(mention_type) as f2,\
        open(feature_type,'w') as g:
        fm = defaultdict(set)
        tm = defaultdict(set)
        for line in f1:
            seg = line.strip('\r\n').split('\t')
            i = int(seg[0])
            j = int(seg[1])
            fm[j].add(i)
        for line in f2:
            seg = line.strip('\r\n').split('\t')
            i = int(seg[0])
            j = int(seg[1])
            tm[j].add(i)
        for i in xrange(feature_number):
            for j in xrange(type_number):
                if j == negLabelIndex:  ### discount weight for None label "1"
                    temp = len(fm[i]&tm[j]) * neg_label_weight
                else:
                    temp = len(fm[i]&tm[j])
                if temp > 0:
                    g.write(str(i)+'\t'+str(j)+'\t'+str(temp)+'\n')

    print 'start feature_feature_qa part'
    f_pairs2count = defaultdict(int)
    with open(qa_x) as f1, open(feature_feature_qa,'w') as g:
        for line in f1:
            seg = line.strip('\r\n').split('\t')
            features = seg[1].split(',')
            for i in range(len(features)):
                for j in range(i+1, len(features)):
                    f1 = features[i]
                    f2 = features[j]
                    f_pairs2count[frozenset([f1,f2])] += 1
        for f_pair in f_pairs2count:
            f1 = list(f_pair)[0]
            f2 = list(f_pair)[1]
            g.write(str(f1)+'\t'+str(f2)+'\t'+str(f_pairs2count[f_pair])+'\n')
    print 'start qa relation mention pairs part'
    with open(qa_mpair) as fin, open(mention_pairs, 'w') as fout:
        for line in fin:
            seg = line.strip('\r\n').split('\t')
            fout.write((str(mids_qa[seg[0]])+'\t'+str(mids_qa[seg[1]])+'\t'+seg[2]+'\n'))
    print 'start qa mention question pairs part'
    with open(qa_pair) as fin, open(mention_question, 'w') as fout:
        for line in fin:
            seg = line.strip('\r\n').split('\t')
            fout.write((str(mids_qa[seg[0]])+'\t'+seg[1]+'\t'+seg[2]+'\n'))
