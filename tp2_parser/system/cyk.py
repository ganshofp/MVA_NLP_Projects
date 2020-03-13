from utils import *
from pcfg import PCFG
from oov import OOV
import numpy as np
from copy import deepcopy
import operator


# Class to apply CYK algorithm
class CYK:
    
    def __init__(self, corpus):
        
        # PCFG and OOV class
        self.pcfg = PCFG(corpus)
        self.oov = OOV(self.pcfg.lexicon, self.pcfg.list_all_tags, self.pcfg.tokens)
        
        # Initialize CYP probability matrix
        self.proba_matrix = None
        self.cyk_matrix = None
              
        
    # Apply the CYK algorithm
    def CYK_algorithm(self, sentence):
        
        # Initialize
        n = len(sentence)
        r = self.pcfg.nb_all_tags
        P = np.zeros((n,n,r))
        cyk_matrix = np.zeros((n,n,r,3))
    
    
        # First level P[0,:,:]
        for idx_word, word in enumerate(sentence):
            
            # Get closest word in the lexicon
            word = self.oov.closest_word(word)
            
            if word is None:
                for idx_tag, tag in enumerate(self.pcfg.list_all_tags):
                    if tag in self.pcfg.terminal_tags:
                        P[0, idx_word, idx_tag] = self.pcfg.terminal_tags[tag]
                        
            else:
                for idx_tag, tag in enumerate(self.pcfg.list_all_tags):
                    if tag in self.pcfg.inv_lexicon[word]:
                        P[0, idx_word, idx_tag] = self.pcfg.inv_lexicon[word][tag]
                   
                        
                        
        # Other levels
        for l in range(1, n):
        
            for s in range(n-l):
            
                for tag in self.pcfg.grammar:
                    idx_tag = self.pcfg.dic_all_tags[tag]
                
                    for p in range(l):
                    
                        for rule in self.pcfg.grammar[tag]:
                            left_tag = rule.split(' ')[0]
                            right_tag = rule.split(' ')[1]
                            b = self.pcfg.dic_all_tags[left_tag]
                            c = self.pcfg.dic_all_tags[right_tag]
                    
                            prob_splitting = self.pcfg.grammar[tag][rule] * P[p, s, b] * P[l-p-1, s+p+1, c]
                        
                            if prob_splitting > P[l, s, idx_tag]:
                                P[l, s, idx_tag] = prob_splitting
                                cyk_matrix[l, s, idx_tag] = [p, b, c]
                        
                
                
                
        self.proba_matrix = P
        self.cyk_matrix = cyk_matrix.astype(int)
        
    # Remove new tags and de-telescope tags
    def clean_tags(self, tree):
        # remove new tags of type
        nodes = deepcopy(tree.nodes)
        for node in nodes:
            children = list(tree.successors(node))
            
            if len(children) == 0:
                pass
            
            elif len(children) == 1 and len(list(tree.successors(children[0]))) == 0:
                pass
            
            else:
                parent = list(tree.predecessors(node))
                if len(parent) == 0:
                    pass
                else:
                    tag = tree.nodes[node]["name"]
                    
                    if (self.pcfg.dic_all_tags[tag] >= self.pcfg.nb_tags) and (
                            "|" in tag):  
                        
                        for child in tree.successors(node):
                            tree.add_edge(parent[0], child)
                        tree.remove_node(node)

        # Decomposing A&B -> w into A -> B -> w
        max_node = np.max(tree.nodes())
        nodes = deepcopy(tree.nodes)
        for node in nodes:
            
            children = list(tree.successors(node))
            
            if len(children) == 0 or len(list(tree.predecessors(node))) == 0:
                pass
            
            elif len(children) == 1 and len(list(tree.successors(children[0]))) == 0:
                tag = tree.nodes[node]["name"]

                if (self.pcfg.dic_all_tags[tag] >= self.pcfg.nb_tags) and (
                        "&" in tag):  # new tag from unit rule
                    word = children[0]

                    idx_cut = None
                    
                    for (idx, c) in enumerate(tag):
                        if c == "&":
                            idx_cut = idx

                    tree.nodes[node]["name"] = tag[:idx_cut]

                    idx_pre_terminal_node = max_node + 1
                    tree.add_node(idx_pre_terminal_node, name=tag[idx_cut + 1:])
                    max_id_node += 1
                    tree.remove_edge(node, word)
                    tree.add_edge(node, idx_pre_terminal_node)
                    tree.add_edge(idx_pre_terminal_node, word)
    
    
    # Parse part of a sentence
    def parse_substring(self, s, l, idx_tag, sentence):
    

        if l == 0:
            return sentence[s]

        else: 
            cut = self.cyk_matrix[l, s, idx_tag, 0]
            idx_left_tag = self.cyk_matrix[l, s, idx_tag, 1]
            idx_right_tag = self.cyk_matrix[l, s, idx_tag, 2]

            left_tag = self.pcfg.list_all_tags[idx_left_tag]
            right_tag = self.pcfg.list_all_tags[idx_right_tag]

            return [[left_tag, self.parse_substring(s, cut, idx_left_tag, sentence)],
                    [right_tag, self.parse_substring(s + cut + 1, l - cut - 1, idx_right_tag, sentence)]]
    
    
    
    # Returns the parsed sentence
    def parse(self, sentence):
        
        sentence = sentence.split(' ')
        length_sentence = len(sentence)
        
        
        if length_sentence > 1:
            self.CYK_algorithm(sentence)
            idx_root_tag = self.pcfg.dic_all_tags['SENT']
            if self.proba_matrix[length_sentence - 1][0][idx_root_tag] == 0:  # no valid parsing
                return None
            parsing_list = self.parse_substring(0, length_sentence - 1, idx_root_tag, sentence)
            
        
        else:
            word = sentence[0]
            word_lexicon = self.oov.closest_word(word)
            
            
            if word_lexicon is None:
                tag = max(self.pcfg.terminal_tags, key=self.pcfg.terminal_tags.get)
                
            else:
                tag = max(self.pcfg.inv_lexicon[word_lexicon], key=self.pcfg.inv_lexicon[word_lexicon].get)
            
            parsing_list = '(' + tag + word + ')'
            
        # converting the parsing stored as a string into a tree
        tree = tagged_sent_to_tree("( (SENT " + list_to_parsed_sentence(parsing_list) + "))",
                                   remove_after_hyphen=False)
            
        self.clean_tags(tree)
            
            
        return tree_to_sentence(tree)
        