from objectives import*
from read_input import * 
import numpy as np 
PYTHONIOENCODING="utf-8"

def create_reformulation_input(w_P, w_A, w_F, w_E, level_cost):
    """
        creates the file reformulation_input.txt which is used as input for the kaufmann-broeckx reformulation done in the C++ scripts.
    """
    level_cost = {u'':0, u'Shift':1, u'Alt':2, u'Alt_Shift':3}
    w_P = 0.25
    w_A = 0.25
    w_F = 0.25
    w_E = 0.25
    #Read in model
    print "read in: characters, keyslots and letters"
    azerty = get_azerty()
    letters = get_letters()
    characters = get_characters()
    keyslots = get_keyslots()

    print "read in: similarity values"
    similarity_c_c = get_character_similarities()
    similarity_c_l = get_character_letter_similarities()

    print "read in: distance values"    
    distance_level_0, distance_level_1 = get_distances(level_cost)

    #read in  probabilities
    print "read in: probability values" 
    p_single, p_bigram = get_probabilities()
    print "read in: ergonomics, performance" 
    ergonomics = get_ergonomics()
    performance = get_performance()

    print "Done reading input values."
    
    linear_costs, x_p, x_a, x_f, x_e =  get_linear_costs(w_P, w_A, w_F, w_E, 
                                               azerty,\
                                               characters,\
                                               keyslots,\
                                               letters,\
                                               p_single, p_bigram,\
                                               performance,\
                                               similarity_c_c, similarity_c_l,\
                                               distance_level_0, distance_level_1,\
                                               ergonomics)
    
    #Writes an input file for the reformualtion of the quadratic term
    f = codecs.open("reformulation_input.txt", 'w', encoding="utf-8")
    f.write("# number of letters and keys\n")
    f.write(str(len(keyslots))+"\n")
    f.write("# w_A*probabilities*similarities\n")
    for c1 in characters:
        prob_strings = []
        for c2 in characters:
            if(c1,c2) in similarity_c_c.keys():
                #Don#t forget the weighting
                p = w_A*(p_single[c1] + p_single[c2])*similarity_c_c[c1,c2]
                prob_strings.append("%f"%p)
            else:
                prob_strings.append("0")
        #add dummy values to fill it up to number of keyslots
        for i in range(len(keyslots) - len(characters)):
            prob_strings.append("0")
        f.write(" ".join(prob_strings) + "\n")
    #add dummy values to fill it up to number of keyslots
    for i in range(len(keyslots) - len(characters)):
        prob_strings = []
        for c2 in characters:
            prob_strings.append("0")
        #add dummy values to fill it up tp number of keyslots
        for i in range(len(keyslots) - len(characters)):
            prob_strings.append("0")
        f.write(" ".join(prob_strings) + "\n")

    #write the w_A weighted distances with linear cost added on diagonal
    f.write("# distances\n")
    distances = distance_level_0

    for s1 in keyslots:
        dist_strings = []
        for s2 in keyslots:        
            d = distances[(s1,s2)]
            dist_strings.append("%f"%d) 

        f.write(" ".join(dist_strings) + "\n")

    f.write("# fixation of the spacebar to the bottom\n")
    f.write("0\n")
    f.write("# scale for rounding down the probabilities\n")
    f.write("1e6")
    f.write("# distances\n")
    distances = distance_level_0

    for c in characters:
        lin_strings = []
        for s in keyslots:        
            l = linear_cost[(c,s)]
            lin_strings.append("%f"%l) 

        f.write(" ".join(lin_strings) + "\n")
    #add dummy values to fill it up to number of keyslots
    for i in range(len(keyslots) - len(characters)):
        lin_strings = []
        for s in keyslots:
            lin_strings.append("0")    
        f.write(" ".join(lin_strings) + "\n")

    f.close()
    print "Done."