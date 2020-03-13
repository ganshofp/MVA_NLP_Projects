from pcfg import *
from utils import *
from pcfg import *
import pickle
import numpy as np


# Class to handle OOV words
class OOV:
    
    def __init__(self, lexicon, list_all_tags, tokens):
        
        # Lexicon from PCFG
        self.lexicon = lexicon
        self.tokens = tokens
        
        # Words in the Polyglott embeddings
        self.poly_words, self.poly_embeddings = pickle.load(open('data/polyglot-fr.pkl', "rb"), 
                                                           encoding='bytes')
        
        # List of words in the lexicon                                    
        self.words_lexicon = list(tokens.keys())
        self.words_lexicon_id = {word: idx for (idx, word) in enumerate(self.words_lexicon)}
        
        # Assign Id's to each word in Polyglott embeddings
        self.poly_words_id = {word: idx for (idx, word) in enumerate(self.poly_words)}
        
        # Embedding matrix
        self.lexicon_embeddings = None
        
        # Words in the lexicon having a polyglott embedding
        self.lexicon_words_with_embed = []
        self.lexicon_words_with_embed_id = {}
        
        # Build embedding matrix with words from lexion
        self.build_embeddings_lexicon()
        self.lexicon_embeddings /= np.linalg.norm(self.lexicon_embeddings, axis=1)[:, None]  # normalize embeddings
        
        
        

        
    # Returns the closest word using a combination of levi distance and cosine similarity
    # of embeddings (if available)
    def closest_word(self, query):
            
        query_normalized = normalize(query, self.words_lexicon_id)
            
        # query_normalized exists in lexicon
        if query_normalized is not None:
            return query_normalized
            
        # Embedding of query exists in Polyglott embeddings, then return word
        # with closest embedding
        if query in self.poly_words:
            closest_word = self.closest_word_embedding(query)
            return closest_word
            
        # If embedding of query does not exists in in Polyglott embeddings, then return
        # word with closest levi distance and highest frequency
        else:
            closest_word = self.closest_word_levi(query,2)
            return closest_word
            
    
    # Build an emebdding matrix with words from the lexicon having on 
    # in the Polyglott embeddings
    def build_embeddings_lexicon(self):
        
        # Get embedding of the word if in the polyglott embeddings
        for word in self.words_lexicon:
            word_normalized = normalize(word, self.poly_words_id)
                
            if word_normalized is not None:
                self.lexicon_words_with_embed.append(word)
                id_word = self.poly_words_id[word_normalized]
                    
                if self.lexicon_embeddings is None:
                    self.lexicon_embeddings = self.poly_embeddings[id_word]
                else:
                    self.lexicon_embeddings = np.vstack([self.lexicon_embeddings, self.poly_embeddings[id_word]])

            
        # Assign new indexes to words having a polyglott embedding
        self.lexicon_words_with_embed_id = {w: i for (i, w) in enumerate(self.lexicon_words_with_embed)}

                
        
        
    # Returns word with closest embedding to query
    def closest_word_embedding(self, query):
            
            
        # Check if query has polyglott embedding
        query = normalize(query, self.poly_words_id)
            
        if query is None:
            print('Query has no embedding in the Polyglott embeddings')
            return None
            
            
        # If query has polyglott embedding, returns word in the lexicon
        # with closest embedding
        query_idx = self.poly_words_id[query]
        query_embedding = self.poly_embeddings[query_idx]
        query_embedding /= np.linalg.norm(query_embedding) # normalize
        indices, distances = l2_nearest(self.lexicon_embeddings, query_embedding, 1)
            
        idx = indices[0]
            
        closest_word = self.lexicon_words_with_embed[idx]
            
        return closest_word
        
    # Returns Levenshtein distance between two strings
    def levenshtein_distance(self, s1, s2):
        # Convert string to list
        list1 = list(s1)
        list2 = list(s2)
        N1 = len(list1)
        N2 = len(list2)
    
        # Initialize  Matrix
        mat = np.zeros((N1+1,N2+1))
        mat[:,0] = np.arange(N1+1)
        mat[0,:] = np.arange(N2+1)

        # Dynamic Programming
        for i in range(1, N1+1):
            for j in range(1, N2+1):
                if list1[i-1] == list2[j-1]:
                    mat[i, j] = min(mat[i-1, j]+1, mat[i,j-1]+1, mat[i-1,j-1])
                else:
                    mat[i, j] = min(mat[i-1,j]+1, mat[i, j-1]+1, mat[i-1,j-1]+1)
                
        return mat[-1,-1] 

        
        
    def closest_word_levi(self, query, k):
            
        candidates = {}
            
        # Separate candidates with different levi distance
        for i in range(1,k+1):
            candidates[i] = [] 
                
    
        min_dist = k
            
        # Find candidates
        for word in self.words_lexicon:
            levi_dist = self.levenshtein_distance(word, query)
            if levi_dist <= min_dist:
                candidates[levi_dist].append(word)
                min_dist = levi_dist
            
            
        # Find final candidates (with the lowest levi distance)
        final_candidates = None
        for i in range(1,k+1):
            if len(candidates[i]) > 0:
                final_candidates = candidates[i]
                break
            
        if final_candidates == None:
            print('No words within a levenshtein distance of {} for: {}'.format(k,query))
            return None
                    
                
        # Get frequency of each candidate
        freq_final_candidates = []
        for final_candidate in final_candidates:
            freq_final_candidates.append(self.tokens[final_candidate])
                
                
        idx_max_freq = np.argmax(freq_final_candidates)
            
        return final_candidates[idx_max_freq]         