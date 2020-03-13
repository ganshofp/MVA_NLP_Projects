import argparse
from cyk import CYK
import os


# Input setting
parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=False, help = 'File to parse')
parser.add_argument('--sentence', type=str, required=False, help='Sentence to parse')
args = parser.parse_args()


# Importing the sequoia corpus
file_path = os.path.join(os.getcwd(), 'sequoia-corpus+fct.mrg_strict')

with open(file_path,'r') as f:
    file = f.read()
    sentences = file.split('\n')[0:]
    
    
# Split the dataset
corpus_length = len(sentences)
length_train = int(0.8 * corpus_length)
corpus_train = sentences[:length_train]

# Build the parser with corpus_train
print('Building the parser...')
cyk_parser = CYK(corpus_train)
print('Done')

# If a sentence is given, parse the sentence
if args.sentence:
    sentence = args.sentence
    print('Sentence: ' + sentence + '\n')
    print('Parsing...')
    parsed_sentence = cyk_parser.parse(sentence)
    print('Done')
    if parsed_sentence is None:
        print('No suitable parsing has been found')
    else:
        print('Parsed sentence: ' + parsed_sentence)

        
# If a file is given, parse the sentences in the file
if args.file:
    
    for sentence in open(args.file):
        
        print(sentence + '\n')
        print('Parsing...')
        parsed_sentence = cyk_parser(sentence)
        if parsed_sentence is None:
            print('No suitable parsing has been found')
        else:
            print(parsed_sentence)
