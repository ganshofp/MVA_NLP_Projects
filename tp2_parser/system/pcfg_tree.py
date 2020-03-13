# Tree to build the pcfg of a sentence in brackets form
from utils import *


# Node class to build a tree
class Node:
    def __init__(self, parent, value):
        self.parent = parent
        self.value = value
        self.children = []

    def GetChildrenValues(self):
        return list(map(lambda x: x.value, self.children))
    
    
    
    
# Build PCFG of a sentence and get a grammar in the form of a dictionary where keys are tags X and
# grammar[X] is also a dictionary so that grammar[X][Y] is the number of times the rule X -> Y appears.
class PCFG_Tree:
    def __init__(self, sentence):
        self.root = Node(None, 'SENT')
        self.grammar = {'SENT' : {}}
        self.lexicon = {}
        self.inv_lexicon = {}
        
        sentence = functional_tags_out(sentence)
        current_node = self.root
        sentence = sentence.split(' ')
        sentence = sentence[2:]
        
        
        for idx, word in enumerate(sentence):
            if '(' in word:
                current_tag = word.replace('(', '')
                new_node = Node(current_node, current_tag)
                current_node.children.append(new_node)
                current_node = new_node
                
                if current_tag not in self.grammar:
                    self.grammar[current_tag] = {}
                    
            else:
                num_closed_brackets = 0
                ele = ''
                for caract in word:
                    if caract == ')':
                        num_closed_brackets += 1
                    else:
                        ele += caract
                        
                
                add_dic(self.inv_lexicon, ele, current_tag, 1)
                        
                add_dic(self.lexicon, current_tag, ele, 1)
                
                for i in range(num_closed_brackets):
                    if current_node.parent is not None:
                        current_node = current_node.parent
    
    def ExtractGrammar(self, node=None):
        if node is None:
            node = self.root
        if len(node.children) > 0:
            rule = listToString(node.GetChildrenValues())
            if rule not in self.grammar[node.value]:
                self.grammar[node.value][rule] = 1
            else:
                self.grammar[node.value][rule] += 1
            
            for child in node.children:
                self.ExtractGrammar(child)