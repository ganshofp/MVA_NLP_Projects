# Regroup all functions used to build the parser
import re
from operator import itemgetter
import networkx as nx


DIGITS = re.compile("[0-9]", re.UNICODE)


# Function to convert list to string
def listToString(s):  
    
    # initialize an empty string 
    str1 = ""  
    
    # traverse in the string   
    for idx, ele in enumerate(s):
        if idx == len(s)-1:
            str1 += ele
        else:
            str1 += ele + ' '  
    
    # return string   
    return str1 


# Remove functional tags
def functional_tags_out(sentence):
    sentence = sentence.split(' ')
    new_sentence = []
    for part_sent in sentence:
        if '(' in part_sent:
            new_part_sent = ''
            for caract in part_sent:
                if caract == '-':
                    break
                new_part_sent += caract
        else:
            new_part_sent = part_sent
            
        new_sentence.append(new_part_sent)
    
    return listToString(new_sentence)  


# Add rule to dictionary
def add_dic(dico, tag, rules, count):
    if tag not in dico.keys():
        dico[tag] = {}
    if rules not in dico[tag]:
        dico[tag][rules] = count
    else:
        dico[tag][rules] += count
        
        
        
# Normalize counts
def count_to_freq(dico):
    for tag in dico:
            total = 0
            for rule in dico[tag].keys():
                total += dico[tag][rule]
            
            
            for rule in dico[tag].keys():
                dico[tag][rule] /= total
                
                

# Get all tags from grammar
def get_tags(dico):
    tags_list = []
    for tag in dico:
        if tag not in tags_list:
            tags_list.append(tag)
            
        for rule in dico[tag].keys():
            list_child_tags = rule.split(' ')
            for child_tag in list_child_tags:
                if child_tag not in tags_list:
                    tags_list.append(child_tag)
                    
    return tags_list 


# Convert list to parsed sentence
def list_to_parsed_sentence(parsing):
        if type(parsing) == str:
            return parsing

        else:
            string = ''
            for p in parsing:
                root_tag = p[0]
                parsing_substring = p[1]
                string = string + '(' + root_tag + ' ' + list_to_parsed_sentence(parsing_substring) + ')' + ' '
            string = string[:-1]  
            return string
        
        
# Remove unnecessary tag information    
def clean_tag(functional_tag):
    return functional_tag.split("-")[0]

# Create file with non-parsed sentences
def unparse(sentence):
    sentence = sentence.split(' ')
    
    list_sentence = []
    
    for token in sentence:
        if ')' in token:
            word = ''
            for caract in token:
                if caract == ')':
                    break
                else:
                    word += caract
            list_sentence.append(word)
            
    sent = listToString(list_sentence)
    
    return sent 


# Returns tree from parsed sentence
def tagged_sent_to_tree(tagged_sent, remove_after_hyphen=True):
    max_id_node = 0

    tree = nx.DiGraph()

    sent = tagged_sent.split()
    hierarchy = list()

    hierarchy.append([])

    level = 0  # difference between the number of opened and closed parenthesis

    for (idx_bloc, bloc) in enumerate(sent):

        if bloc[0] == "(":

            if remove_after_hyphen:
                tag = clean_tag(bloc[1:])  # we add it to the hierarchy
            else:
                tag = bloc[1:]
            if level < len(hierarchy):  # there is already one tag as its level
                hierarchy[level].append((tag, max_id_node))
            else:  # first tag as its level
                hierarchy.append([(tag, max_id_node)])
            if idx_bloc > 0:
                tree.add_node(max_id_node, name=tag)
                max_id_node += 1
            level += 1

        else:

            word = ""
            nb_closing_brackets = 0
            for caract in bloc:
                if caract == ")":
                    nb_closing_brackets += 1
                else:
                    word += caract

            tree.add_node(max_id_node, name=word)
            tree.add_edge(max_id_node - 1, max_id_node)
            max_id_node += 1

            level -= nb_closing_brackets

            for k in range(nb_closing_brackets - 1, 0, -1):
                root = hierarchy[-2][-1][0]  # root tag
                id_root = hierarchy[-2][-1][1]
                if root == '':
                    break
                tags = hierarchy[-1]  # child tags

                for tag in tags:
                    tree.add_edge(id_root, tag[1])

                hierarchy.pop()

    return tree

# Partial sentence from subtree rooted at node
def tree_to_sentence_helper(tree, node):
    children = list(tree.successors(node))
    if (len(children) == 1) and (len(list(tree.successors(children[0]))) == 0):
        return "(" + tree.nodes[node]["name"] + " " + tree.nodes[children[0]]["name"] + ")"
    else:
        res = "(" + tree.nodes[node]["name"]
        for child in sorted(children):
            res += " " + tree_to_sentence_helper(tree, child)
        res += ")"
        return res


# Transform tree to sentence
def tree_to_sentence(tree):
    root = list(nx.topological_sort(tree))[0]
    return "( " + tree_to_sentence_helper(tree, root) + ")"

# The functions below are taken from https://nbviewer.jupyter.org/gist/aboSamoor/6046170

# In case the word is not available in the vocabulary,
# we can try multiple case normalizing procedure.
# We consider the best substitute to be the one with the lowest index,
# which is equivalent to the most frequent alternative.
def case_normalizer(word, dictionary):
    w = word
    lower = (dictionary.get(w.lower(), 1e12), w.lower())
    upper = (dictionary.get(w.upper(), 1e12), w.upper())
    title = (dictionary.get(w.title(), 1e12), w.title())
    results = [lower, upper, title]
    results.sort()
    index, w = results[0]
    if index != 1e12:
        return w
    return word

# If the word is OOV, find the closest alternative
def normalize(word, word_id):
    if word not in word_id:
        word = DIGITS.sub("#", word)
    
    if word not in word_id:
        word = case_normalizer(word, word_id)

    if word not in word_id:
        return None
    
    return word


# Sorts words according to their Euclidean distance.
# To use cosine distance, embeddings has to be normalized so that their l2 norm is 1.
# indeed (a-b)^2"= a^2 + b^2 - 2a^b = 2*(1-cos(a,b)) of a and b are norm 1"""
def l2_nearest(embeddings, query_embedding, k):
    distances = (((embeddings - query_embedding) ** 2).sum(axis=1) ** 0.5)
    sorted_distances = sorted(enumerate(distances), key=itemgetter(1))
    return zip(*sorted_distances[:k])