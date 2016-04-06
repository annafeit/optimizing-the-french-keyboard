import pandas as pd
import numpy as np
import codecs
import random

PYTHONIOENCODING="utf-8"


def create_test_model(level_cost):    
    
    print "read in: characters, keyslots and letters"
    azerty = get_azerty()
    letters = get_letters()
    characters = get_characters()
    keyslots = get_keyslots()
    
    print "read in: similarity values"
    similarity_c_c = get_characte_similarities()
    similarity_c_l = get_character_letter_similarities()
    
    print "read in: distance values"    
    distance_level_0, distance_level_1 = get_distances(level_cost)

    #read in single probabilities
    
    p_single, p_bigram = get_probabilities()
    ergonomics = get_ergonomics()
    performance = get_performance()
    
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


    


def create_dummy_values_performance_ergonomics_probability(randomize=False):
    """
        Creates input files with dummy values for performance, ergonomics, bigram and letter probabilities
        If randomize=True it creates randomized values, if False, the values are more or less constant. 
    """
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
        
