import pandas as pd
import numpy as np
import codecs
import random

PYTHONIOENCODING="utf-8"


def create_test_model(level_cost):    
    
    print "read in: characters, keyslots and letters"
    with codecs.open('input\\characters.txt', encoding='utf-8') as f:
        characters = f.read().splitlines()
    with codecs.open('input\\letters.txt', encoding='utf-8') as f:
        letters = f.read().splitlines()
    with codecs.open('input\\variable_slots.txt', encoding='utf-8') as f:    
        keyslots = f.read().splitlines()
    
    print "read in: azerty letters and numbers"
    azerty = getAzerty()
    numbers = pd.read_csv("input\\numbers.csv", index_col=1, sep="\t", encoding='utf-8', quoting=3).to_dict()["keyslot"]
    #remove number keys from free keyslots

    for n_slot in numbers.values():        
        keyslots.remove(n_slot)
    
    #Similarity values (c,c)->s, (c,l)->s
    print "read in: similarity values"
    similarity_c_c = read_similarity_matrix('input\\similarity_c_c_binary.xlsx', characters, letters)
    similarity_c_l = read_similarity_matrix('input\\similarity_c_l.xlsx', characters, letters)
    
    #Distance values (key,key)->d
    print "read in: distance values"    
    distance_level_0, distance_level_1 = read_distance_matrix("input\\distance.xlsx", level_cost, recompute=0)
    
    #Frequency distributions c/l -> p, (c/l, c/l) -> p
    #TODO
    all_chars = letters+characters
    #read in single probabilities
    p_single = pd.read_csv("input\\frequency_letters.csv", sep="\t", encoding="utf-8", index_col=0, quoting=3).to_dict()["frequency"]
    #read in bigram probabilities
    p_bigram = read_matrix("input\\frequency_bigrams.csv")
    
    #read in Ergonomic values
    ergonomics = read_matrix("input\\ergonomics.csv")
    
    #Performance: (key, letter)->t
    performance = read_matrix("input\\performance.csv")
    
    print "Done reading input values."
    
    return azerty,\
           characters,\
           keyslots,\
           letters,\
           p_single, p_bigram,\
           performance,\
           similarity_c_c, similarity_c_l,\
           distance_level_0, distance_level_1,\
           ergonomics

def read_matrix(path):
    with codecs.open(path, 'r', encoding="utf-8") as bigram_file:
        all_lines = bigram_file.readlines()
        lines = [l.rstrip() for l in all_lines]
        #create dict
        p_bigrams = {}
        for l in lines:
            parts = l.split(" ")
            p_bigrams[(parts[0], parts[1])] = float(parts[2])
    return p_bigrams
    
def read_similarity_matrix(path, characters, letters):
    """
        Reads the given matrix into a dictionary of the form (c1,c2)->similarity
        Filters out all characters that are not in the given character list
        Already normalized
    """    
    df = pd.read_excel(path, encoding='utf-8')

    index = df.index
    columns = df.columns
    dictionary = {}
    for i in range(0,len(df)): #row index
        for j in range(0, len(df.columns)): #column index
            row = index[i]
            col = columns[j]
            if (row in characters and col in characters) or (row in characters and col in letters):
                if not pd.isnull(df.iloc[i,j]):
                    dictionary[(row,col)] = df.iloc[i,j]
    return dictionary

def read_distance_matrix(path, level_cost, recompute=0):
    """
        reads the distance between the keys from the excel file. If the file is empty (or recompute is set) it creates the distance matrix
        and writes it to the file. The file does not include any level distance.
        Distance is defined as the sum of the vertical and horizontal distance.         
        
        level_cost: dict
            additional cost for each lower level, e.g. level_cost = {'':0, 'Shift':1, 'Alt':2, 'Alt_Shift':3}, 
            is computed in relation to each other, 
            that is cost is 1 if one character on Shift, the other on Alt level. Cost is 2 if one character on single, other
            on Alt level
            
        outputs 2 dictionaries from key-tuple to distance.
        dictionary_level_0: normalized distance not including any level cost
        dictionary_level_1: normalized distance including the level cost
    """
    row_numbers = {u"A":0, u"B":1, u"C":2, u"D":3, u"E":4}
    df = pd.read_excel(path, encoding='utf-8')
    index = df.index
    columns = df.columns
    dictionary_level_0 = {}
    dictionary_level_1 = {}
    changed = 0
    for i in range(0,len(index)): #row index
        for j in range(0, len(columns)): #column index
            slot1 = index[i]
            slot2 = columns[j]            
            if recompute or pd.isnull(df.iloc[i,j]):                
                #if there is no value yet, compute it based on the names:
                row_distance = np.abs(row_numbers[slot1[0]] - row_numbers[slot2[0]])
                column_distance = np.abs(int(slot1[1:3]) - int(slot2[1:3]))                
                #Special case: shift
                if slot1[0:3] == "A03":
                    if int(slot2[1:3])>3:
                        column_distance = max(0,column_distance-4)
                if slot2[0:3] == "A03":
                    if int(slot1[1:3])>3:
                        column_distance = max(0,column_distance-4)
                df.iloc[i,j] = row_distance+column_distance
                changed = 1
                
            level_distance = np.abs(level_cost[slot1[4:]] - level_cost[slot2[4:]])
            #add level cost and normalize
            dictionary_level_1[(slot1,slot2)] = (df.iloc[i,j]+level_distance) / float((df.max().max() + np.max(level_cost.values())))
            dictionary_level_0[(slot1,slot2)] = df.iloc[i,j] / float((df.max().max()))
    if changed:
        df.to_excel(path)                                  
    return dictionary_level_0, dictionary_level_1

def create_dummy_values_performance_ergonomics_probability(randomize=False):
    print "read in: characters, keyslots and letters"
    with codecs.open('input\\characters.txt', encoding='utf-8') as f:
        characters = f.read().splitlines()
    with codecs.open('input\\letters.txt', encoding='utf-8') as f:
        letters = f.read().splitlines()
    with codecs.open('input\\variable_slots.txt', encoding='utf-8') as f:    
        keyslots = f.read().splitlines()
        
    
    
    azerty = pd.read_csv("input\\azerty.csv", index_col=1, sep="\t", encoding='utf-8', quoting=3).to_dict()["keyslot"]
    numbers = pd.read_csv("input\\numbers.csv", index_col=1, sep="\t", encoding='utf-8', quoting=3).to_dict()["keyslot"]
    #remove number keys from free keyslots

    for n_slot in numbers.values():        
        keyslots.remove(n_slot)
        
    all_chars = letters+characters
        
    #Create dummy data for single letter frequency
    if randomize:       
        p_single = {character: random.random()*float(1)/len(all_chars) for character in all_chars}
    else:
        p_single = {character: float(1)/len(all_chars) for character in all_chars}
    df = pd.DataFrame()
    df = df.from_dict(p_single,orient="index")
    df.columns = ["frequency"]
    df.to_csv("input\\frequency_letters.csv", sep="\t", encoding="utf-8", quoting=3)

    #create dummy data for bigram frequency
    if randomize:        
        p_bigram = {(c1,c2): random.random()*float(1)/len(all_chars) for c1 in all_chars for c2 in all_chars}
    else:
        p_bigram = {(c1,c2): float(1)/len(all_chars) for c1 in all_chars for c2 in all_chars}
    p_bigram_strings = ["%s %s %f\n"%(c1,c2,n) for (c1,c2), n in p_bigram.iteritems()]
    p_bigrams_strings = [s.encode("utf-8") for s in p_bigram_strings]
    with open("input\\frequency_bigrams.csv", 'w') as bigram_file:
        bigram_file.writelines(p_bigrams_strings)

    #Ergonomics (c, l)-> e
    #TODO    
    ergonomics = {}
    for s in keyslots:
        for l in letters:
            r1 = 1
            r2 = 1
            if randomize:
                r1 = random.random()
                r2 = random.random()     
            ergonomics[(s,azerty[l])]= r1*0.2
            ergonomics[(azerty[l],s)]= r2*0.2
    ergonomic_strings = ["%s %s %f\n"%(s,l,n) for (s,l), n in ergonomics.iteritems()]
    ergonomics_strings = [s.encode("utf-8") for s in ergonomic_strings]
    with open("input\\ergonomics.csv", 'w') as ergonomic_file:
        ergonomic_file.writelines(ergonomics_strings)

    #Performance: (key, letter)->t
    #TODO
    performance = {}
    for s in keyslots:
        for l in letters:
            r1 = 1
            r2 = 1
            if randomize:
                r1 = random.random()
                r2 = random.random()             
            performance[(s,azerty[l])]= r1*0.2 
            performance[(azerty[l],s)]= r2*0.2 
            if s[4:] == "Shift":
                performance[(s,azerty[l])]+= 0.1 
                performance[(azerty[l],s)]+= 0.1
            if s[4:] == "Alt":
                performance[(s,azerty[l])]+= 0.2 
                performance[(azerty[l],s)]+= 0.2
            if s[4:] == "Alt_Shift":
                performance[(s,azerty[l])]+= 0.3 
                performance[(azerty[l],s)]+= 0.3
    performance_string = ["%s %s %f\n"%(s,l,n) for (s,l), n in performance.iteritems()]
    performance_strings = [s.encode("utf-8") for s in performance_string]
    with open("input\\performance.csv", 'w') as performance_file:
        performance_file.writelines(performance_strings)
        
def getAzerty():
    """
        Returns the Azerty keyboard in form of a dict from characters to keyslots (=mapping)
    """
    return pd.read_csv("input\\azerty.csv", index_col=1, sep="\t", encoding='utf-8', quoting=3).to_dict()["keyslot"]