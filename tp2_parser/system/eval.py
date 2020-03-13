from cyk import CYK
import os
from PYEVALB import scorer
from PYEVALB import parser
from utils import *


# Importing the corpus
file_path = os.path.join(os.getcwd(), 'sequoia-corpus+fct.mrg_strict')

with open(file_path,'r') as f:
    file = f.read()
    sentences = file.split('\n')[0:]
    
    
    
# Split the dataset
corpus_length = len(sentences)

length_train = int(0.8 * corpus_length)
length_dev = int(0.1 * corpus_length)
length_test = int(0.1 * corpus_length)

end_dev = length_train + length_dev
 

corpus_train = sentences[:length_train]
corpus_dev = sentences[length_train:end_dev]
corpus_test = sentences[end_dev:]


# Get unparsed sentence from eval_corpus.txt
with open('data/eval_corpus.txt', 'r') as f:
    file = f.read()
    test_sentences = file.split('\n')



# Build the parser with corpus_train
print('Building the parser...')
cyk_parser = CYK(corpus_train)
print('Done')

# Parsing of Evaluation sentences
print('Parsing...')


test_sentences_bis = []

with open('data/evaluation_data.parser.txt', 'w') as f:
    for sentence in test_sentences:
        parsed_sentence = cyk_parser.parse(sentence)
        if parsed_sentence is not None:
            test_sentences_bis.append(sentence)
            f.write('%s\n' % parsed_sentence)
        
        
print('Done')



# Get accuracy
# Get sentences parsed by our parser
with open('data/evaluation_data.parser.txt', 'r') as f:
    file = f.read()
    parsed_sentences = file.split('\n')
    
    
# Remove first two and last brackets to use parser from PYEVALB
initial_parsed_sentences = []
parsed_sentences_final = []

for sent in test_sentences_bis:
    initial_parsed_sentences.append(sent[2:-1])
    
for sent in parsed_sentences:
    parsed_sentences_final.append(parsed_sentences[2:-1])
    

# Put in tree form
initial_tree = parser.create_from_bracket_string(initial_parsed_sentences)
my_tree = parser.create_from_bracket_string(parsed_sentences_final)
        
# Get accuracy
result = scorer.Scorer().score_trees(initial_tree, my_tree)
print('Accuracy on Evaluation set: ' + str(result.tag_accracy))

