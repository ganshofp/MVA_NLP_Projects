from utils import *
from pcfg_tree import *
from copy import deepcopy
import numpy as np





# Class to build the PCFG in Chomsky normal form
class PCFG:

    def __init__(self, corpus):

        # Initialize grammar, lexicon and new tags
        self.grammar = {}
        self.lexicon = {}
        self.inv_lexicon = {}
        self.set_new_tags = set()

        # Build PCFG from corpus
        self.build_pcfg(corpus)

        # Build dictionnary of words form the corpus with the corresponding frequency 
        # {word : frequency}
        self.tokens = {}
        for tag in self.lexicon.keys():
            for word in self.lexicon[tag].keys():
                if word in self.tokens.keys():
                    self.tokens[word] += self.lexicon[tag][word]
                else:
                    self.tokens[word] = self.lexicon[tag][word]
        sum = np.sum(list(self.tokens.values()))
        
        for word in self.tokens:
            self.tokens[word] /= sum

            
        # Apply Chomsky normalization to PCFG from corpus
        self.to_chomsky_form()

        
        # Build dictionnary of terminal tags form the corpus with the corresponding frequency 
        # {terminal_tag : frequency}
        self.terminal_tags = {tag: np.sum(list(counts.values())) for (tag, counts) in self.lexicon.items()}
        sum = np.sum(list(self.terminal_tags.values()))
        for tag in self.terminal_tags:
            self.terminal_tags[tag] /= sum

        
        # Normalize
        count_to_freq(self.grammar)
        count_to_freq(self.lexicon)
        count_to_freq(self.inv_lexicon)

        
        # Get all tags
        list_all_tags = get_tags(self.grammar)
        
        # Tags lists
        self.list_new_tags = list(self.set_new_tags)
        self.list_tags = list(set(list_all_tags).difference(self.set_new_tags))
        self.list_all_tags = self.list_tags + self.list_new_tags
        self.dic_all_tags = {word: idx for (idx, word) in enumerate(self.list_all_tags)}
        
        self.nb_tags = len(self.list_tags)
        self.nb_all_tags = len(self.list_all_tags)

        
    # Apply Chomsky normalization to PCFG
    def to_chomsky_form(self):
        self.to_binary_rules()
        self.unit_rules_out()

        
    # Telescope unait rules
    def unit_rules_out(self):
        grammar_copy = deepcopy(self.grammar)
        lexicon_copy = deepcopy(self.lexicon)

        rules_to_remove = []

        for tag in grammar_copy.keys():
            
            for rule in grammar_copy[tag].keys():
                count = grammar_copy[tag][rule]
                list_tags = rule.split(' ')
                
                if len(list_tags) == 1: # Check if unit rule

                    child_tag = list_tags[0]
                    rules_to_remove.append((tag, child_tag))
                    proba = count / (np.sum(list(self.grammar[tag].values())))

                    # rule A -> B where B is a pre-terminal tag
                    if child_tag in lexicon_copy:
                        
                        if tag != "SENT":
                            new_tag = tag + "&" + child_tag
                            self.set_new_tags.add(new_tag)
                            
                            # new_tag -> word
                            for word in lexicon_copy[child_tag].keys():
                                count2 = lexicon_copy[child_tag][word]
                                add_dic(self.lexicon, new_tag, word, count2*proba)

                            
                            # for each rule X -> Y A, add rule X -> Y A&B
                            for tag2 in grammar_copy.keys():
                                for rule2 in grammar_copy[tag2].keys():
                                    list_tags = rule2.split(' ')
                                    count2 = grammar_copy[tag2][rule2]
                                    if len(list_tags) == 2 and list_tags[1] == tag:
                                        new_rule2 = rule2.replace(tag, new_tag)
                                        add_dic(self.grammar, tag2, new_rule2, count2)

                    # If B not pre-terminal, for each rule B -> X Y, add A -> X Y
                    else:
                    
                        for grand_child_tag in grammar_copy[child_tag].keys():
                            list_grand_child_tags = grand_child_tag.split(' ')
                            count3 = grammar_copy[child_tag][grand_child_tag]
                            if len(list_grand_child_tags) == 2:
                                add_dic(self.grammar, tag, grand_child_tag, count3*proba)
                

        for (left, right) in rules_to_remove:
            del self.grammar[left][right]
            
        for tag in grammar_copy.keys():
            if len(self.grammar[tag]) == 0:
                del self.grammar[tag]

    
    # Replace all rules with more than 2 children with a chain of rule
    def to_binary_rules(self):
        grammar_copy = deepcopy(self.grammar)
    
    
        for tag in grammar_copy.keys():
        
            for rule in grammar_copy[tag].keys():
            
                count = grammar_copy[tag][rule]
                tags_list = rule.split(' ')
            
                if len(tags_list) > 2: 
                    del self.grammar[tag][rule]
                    old_tag = tag
                    for idx, sub_tag in enumerate(tags_list[:-2]):
                        new_symbol = tag + '|' + '-'.join(tags_list[idx+1:])
                        self.set_new_tags.add(new_symbol)
                        new_rule = listToString([sub_tag, new_symbol])
                        add_dic(self.grammar, old_tag, new_rule, count)
                        old_tag = new_symbol
                    
                    last_two_tags = listToString(tags_list[-2:])
                    add_dic(self.grammar, old_tag, last_two_tags, count)
                                                     
 
                    
    # Build the PCFG
    def build_pcfg(self, corpus):
 
        for sentence in corpus:
            tree = PCFG_Tree(sentence)
            tree.ExtractGrammar()
        
            lexicon_sent = tree.lexicon
            inv_lexicon_sent = tree.inv_lexicon
            grammar_sent = tree.grammar
            
        
            # Add lexicon of sentence in general lexicon
            for tag in lexicon_sent.keys():
                for word in lexicon_sent[tag].keys():
                    add_dic(self.lexicon, tag, word, 1)
                    
            # Add inverse lexicon of sentence in general inverse lexicon
            for word in inv_lexicon_sent.keys():
                for tag in inv_lexicon_sent[word]:
                    add_dic(self.inv_lexicon, word, tag, 1)
                
            # Add grammar of sentence in general grammar      
            for tag in grammar_sent.keys():
                for rule in grammar_sent[tag].keys():
                    add_dic(self.grammar, tag, rule, 1)
                
            
        # Get rid of terminal tags
        self.grammar = { tag : dic for tag,dic in self.grammar.items() if len(dic) > 0}             