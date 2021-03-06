import argparse
from support.dataset_fb15k237 import Dataset_FB15k237
from support.dataset_dbpedia50 import Dataset_dbpedia50
from support.utils import *
import pickle
import os
import json

def parse_args():
    parser = argparse.ArgumentParser(description = '')
    parser.add_argument('--classifier', dest='classifier', type=str, choices=['mlp', 'mlp_multi', 'lstm', 'conv', 'snorkel', 'trans', 'supensemble', 'squid'])
    parser.add_argument('--name_signals', dest='name_signals', help='name of the signals (classifiers) to use when multiple signals should be combined', type=str, required=False, default="mlp_multi,lstm,conv,path,sub")
    parser.add_argument('--result_dir', dest ='result_dir', type = str, help = 'Output dir.')
    parser.add_argument('--db', dest = 'db', type = str, default = "fb15k237", choices=['fb15k237', 'dbpedia50'])
    parser.add_argument('--topk', dest='topk', type=int, default=10)
    parser.add_argument('--model', dest='model', type=str, default="transe", choices=['complex', 'rotate', 'transe'])
    parser.add_argument('--type_prediction', dest='type_prediction', type=str, default="head", choices=['head', 'tail'])

    parser.add_argument('--snorkel_low_threshold', dest='snorkel_low_threshold', type=str,
                        default="0.2,0.2,0.2,0,0")
    parser.add_argument('--snorkel_high_threshold', dest='snorkel_high_threshold', type=str,
                        default="0.6,0.6,0.6,0.5,0.5")

    return parser.parse_args()

args = parse_args()

# Load the dataset
dataset = None
annotations_dir = args.result_dir + '/' + args.db + '/annotations/'
if args.db == 'fb15k237':
    dataset = Dataset_FB15k237()
elif args.db == 'dbpedia50':
    dataset = Dataset_dbpedia50()

# Load the training data
annotations_filename = get_filename_answer_annotations(args.db, args.model, 'train', args.topk, args.type_prediction)
with open(annotations_dir + annotations_filename, 'rb') as fin:
    annotations = pickle.load(fin)

gold_valid_standard = None
gold_dir = args.result_dir + '/' + args.db + '/annotations/'
path_gold_valid_standard = gold_dir + get_filename_gold(args.db, args.topk, '-valid')
if os.path.exists(path_gold_valid_standard):
    with open(path_gold_valid_standard, 'rt') as fin:
        gold_valid_standard = json.load(fin)


# Load the embedding model
embedding_model_typ = args.model
if args.classifier != 'snorkel':
    from support.embedding_model import Embedding_Model
    embedding_model = Embedding_Model(args.result_dir, embedding_model_typ, dataset)

# Load the classifier
if args.classifier == 'mlp':
    from classifier_mlp import Classifier_MLP
    classifier = Classifier_MLP(dataset, args.type_prediction, args.result_dir, embedding_model)
if args.classifier == 'mlp_multi':
    from classifier_mlp_multi import Classifier_MLP_Multi
    classifier = Classifier_MLP_Multi(dataset, args.type_prediction, args.result_dir, embedding_model)
elif args.classifier == 'lstm':
    from classifier_lstm import Classifier_LSTM
    classifier = Classifier_LSTM(dataset, args.type_prediction, args.result_dir, embedding_model)
elif args.classifier == 'conv':
    from classifier_conv import Classifier_Conv
    classifier = Classifier_Conv(dataset, args.type_prediction, args.result_dir, embedding_model, args.topk)
elif args.classifier == 'trans':
    from classifier_transformer import Classifier_Transformer
    classifier = Classifier_Transformer(dataset, args.type_prediction, args.result_dir, embedding_model)
elif args.classifier == 'snorkel':
    from classifier_snorkel import Classifier_Snorkel
    signals = args.name_signals.split(",")
    lows = args.snorkel_low_threshold.split(",")
    highs = args.snorkel_high_threshold.split(",")
    thresholds = []
    for i, l in enumerate(lows):
        h = highs[i]
        thresholds.append((float(l), float(h)))
    classifier = Classifier_Snorkel(dataset, args.type_prediction, args.topk, args.result_dir, signals, embedding_model_typ, abstain_scores=thresholds)
elif args.classifier == 'squid':
    from classifier_squid import Classifier_Squid
    signals = args.name_signals.split(",")
    lows = args.snorkel_low_threshold.split(",")
    highs = args.snorkel_high_threshold.split(",")
    thresholds = []
    for i, l in enumerate(lows):
        h = highs[i]
        thresholds.append((float(l), float(h)))
    classifier = Classifier_Squid(dataset, args.type_prediction, args.topk, args.result_dir, signals, embedding_model_typ, abstain_scores=thresholds)
elif args.classifier == 'supensemble':
    from classifier_supensemble import Classifier_SuperEnsemble
    signals = args.name_signals.split(",")
    classifier = Classifier_SuperEnsemble(dataset, args.type_prediction, args.topk, args.result_dir, signals,
                                    embedding_model_typ)
else:
    raise Exception('Not supported')

if args.classifier == 'snorkel' or args.classifier == 'squid':
    training_data = classifier.create_training_data(annotations, valid_dataset=gold_valid_standard)
else:
    training_data = classifier.create_training_data(annotations)

# Save the training data on a file
training_data_dir = args.result_dir + '/' + args.db + '/training_data/'
training_data_filename = get_filename_training_data(args.db, args.model, args.classifier, args.topk, args.type_prediction)
with open(training_data_dir + training_data_filename, 'wb') as fout:
    pickle.dump(training_data, fout)
