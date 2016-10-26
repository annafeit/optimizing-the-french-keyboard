from objectives import*
from read_input import * 
import numpy as np 
PYTHONIOENCODING="utf-8"

def create_reformulation_input(w_P, w_A, w_F, w_E, corpus_weights, filename, quadratic=1):
    
    """
        creates the file reformulation_input.txt which is used as input for the kaufmann-broeckx reformulation done in the C++ scripts.
    """
    
    #Read in input values
    
    azerty,\
    characters,\
    keyslots,\
    letters,\
    p_single, p_bigram,\
    performance,\
    similarity_c_c, similarity_c_l,\
    distance_level_0, distance_level_1,\
    ergonomics\
     = get_all_input_values(corpus_weights)
        
    #linear_costs is already weighted, the x_ are not    
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
    scenario, char_set = get_scenario_and_char_set()
    #Writes an input file for the reformualtion
    f = codecs.open("reformulation/input/"+filename+".txt", 'w', encoding="utf-8")
    f.write("#scenario=%s,set=%s,w_P=%f,w_A=%f,w_F=%f,w_E=%f,w_formal=%f,w_twitter=%f,w_code=%f\n"%(scenario,char_set,
                                                                                w_P,w_A, w_F, w_E, 
                                                                                corpus_weights["formal"], 
                                                                                corpus_weights["twitter"],
                                                                                corpus_weights["code"]))
    f.write("# number of letters and keys\n")
    f.write(str(len(keyslots))+"\n")
    f.write("# w_A*probabilities*similarities\n")
    
    ## QUADRATIC PART
    #this is unweighted
    prob_sim, distance_level_0_norm = get_quadratic_cost(\
                               characters,\
                               keyslots,\
                               p_single,\
                               similarity_c_c, similarity_c_l)
    
    for c1 in characters:
        prob_strings = []
        for c2 in characters:
            prob_strings.append("%f"%(quadratic*w_A*prob_sim_matrix[(c1,c2)])) #remember to weight           
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

    #write the distances for quadratic part only!
    f.write("# distances\n")
    distances = distance_level_0_norm

    for s1 in keyslots:
        dist_strings = []
        for s2 in keyslots:        
            d = distances[(s1,s2)]
            dist_strings.append("%f"%d) 

        f.write(" ".join(dist_strings) + "\n")

    
    f.write("# fixation of the spacebar to the bottom\n")
    f.write("0\n")
    f.write("# scale for rounding down the probabilities\n")
    f.write("1e6\n")
    
    ## LINEAR PART
    f.write("# linear cost\n")

    for c in characters:
        lin_strings = []
        for s in keyslots:        
            l = linear_costs[(c,s)]
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