
# Instructions

* First, you must download all the folders in the repository. Folder named "code"
contains all the experimental code. The code depends on two libraries: OpenKE
[1] and LibKGE [2]. The reason is that some embeddings were created with OpenKE
while others with LibKGE. It also depends on the library tqdm.

[1] https://github.com/thunlp/OpenKE

[2] https://github.com/uma-pi1/kge

* We put a copy of the OpenKE library that we used in "code". In the case of
LibKGE, we put a copy under "support". In case these libraries are not found, please download it from their repository. Our code depends on an older
version of the KGE library, namely it was tested with
6d8f7404b5046ad76b6aa3968922ba2c00c81480. It seems that the new version of the
library does not load old embedding models. Also make sure that you download
all the datasets (script is available in the directory "data" of LibKGE). The copy of the library under "support" contains already the datasets used in the experiments.


* If you want to reproduce the experiments, then you should execute the script
"pipeline.sh" in the directory "scripts". This script is heavily commented and
performs all the necessary operations in a sequence. It will first compute the
top-k answers, train the models for C1, C2, and C3, annotate the top-k answers,
and invoke metal and squid to produce the final answers. It will also invoke
other baselines and print all the results (F1, etc.) as output. The
annotations, results, etc. are also written in json format. We provide an
additional script to parse the json files and produce a latex-friendly tabular
version of all the obtained results.

The script reads and writes data in one directory, which we call A. We
provide a copy of these two directories under "data".  This script receives as
input the model to use (e.g., Transe), the db (e.g., db15k237), and the path to
A. For instance, the command can be invoked as follows:

`./pipeline.sh <path_to_data> fb15k237 transe`

Optionally, the script allows the user to skip some operations using the
parameters -SKIPX where X is the operation to skip. Please check the
documentation inside the script for more details.

The directory A can have an arbitrary name (default "data"). This directory has
a special structure and it is supposed to contain the embedding models and the
gold standard. The script will write in this directory all the experimental
data. For instance, it will write the top-k answers, the annotations produced
by the classifiers, logs, etc.

## More details about the scripts invoked by pipeline.sh ***

*   The script `create_queries.py` takes in input a list of facts (can be the
    train/valid/test triples) and creates two files with all possible head and
    tail queries. The queries are stored in the 'queries' subfolder

*  The script `create_answers.py` takes the output of `create_queries.py` as input
    and return the filtered and raw top k answers for each query. The output
    files are stored in the subfolder "answers"

*   The script `create_answer_annotations_cwa.py` annotated the provided answers
    using the content of the KG (thus with closed-world assumption)

*   The script `create_training_data.py` creates the training data for the
    various classifiers

*   The script `create_model.py` trains the models used by various classifiers
    (LSTM,CONV,MLP,METAL etc)

*   The script `create_answer_annotations_classifier.py` invokes the classifier
    passed as input and returns the annotations produced by the classifier.
    These annotations are also stored on a json file.

*   The script `evaluate_annotations_gold_standard.py` compares the annotations
    produced by the classifier with the gold standard and return metrics like
    F1, etc.

*   The scripts `classifier*` implements the various classifiers. These classes
    are organised in a hierarchy `Classifier->SupervisedClassfier->`etc.) to
    share common methods

*   The scripts print* print the results collected during the experiments. In
    particular, `print_hyperparameter`_results returns the results of grid-search
    while `print_performance_classifiers` returns the performance of classifiers

*   The script `hyperparamer_tuning.py` performs the hyperparameters tuning.

The folder support contains several files used by the various scripts:

*   The scripts dataset* contains methods to parse the databases

*   The script `embedding_model` abstracts the embedding models and provide a
    single interface to the rest of the program.

## Gold standard

*   The jupyter notebook `annotate_gold_standard.ipynb` is used to manually
    annotate answers with true labels. It produces a web interface to speed up
    the creation of the gold standard.  The annotations are stored in the
    subfolder "annotations"
