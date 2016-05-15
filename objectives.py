from read_input import * 
from test_model import*
import numpy as np 
PYTHONIOENCODING="utf-8"

def get_objectives(mapping, w_p, w_a, w_f, w_e, level_cost, quadratic=0):
    """
        A wrapper for the _get_objectives function to use the standard test variables
    """
    azerty,\
    characters,\
    keyslots,\
    letters,\
    p_single, p_bigram,\
    performance,\
    similarity_c_c, similarity_c_l,\
    distance_level_0, distance_level_1,\
    ergonomics\
     = create_test_model(level_cost)
                   
    return _get_objectives(mapping, w_p, w_a, w_f, w_e, \
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics, quadratic=quadratic)

def _get_objectives(mapping, w_p, w_a, w_f, w_e,\
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics, quadratic=1):
    """
        For a given mapping, returns the objective value for the given weights, and the individual objectives values for P,A,F,E
    """
    #Compute linear cost matrices
    linear_cost, x_P, x_A, x_F, x_E = get_linear_costs(w_p, w_a, w_f, w_e, 
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics)
        
    #remove letters from mapping that are not in characters list
    for m in mapping.keys():
        if not m in characters:
            mapping.pop(m)  
            print("%s not in the to-be-mapped character set"%m)

    P=0
    A=0
    F=0
    E=0
    for c, s in mapping.iteritems():
        P+=x_P[c,s]            
        A+=x_A[c,s]
        F+=x_F[c,s]
        E+=x_E[c,s]    
    if quadratic:   
        nonzeros = 0
        for (c1,c2) in similarity_c_c:
            #Compute nonzeros for normalization
            if c1 in mapping and c2 in mapping:
                v = (p_single[c1] + p_single[c2])*similarity_c_c[(c1,c2)]
                if v > 0:
                    nonzeros += 1
        for (c1,c2) in similarity_c_c:
            if c1 in mapping and c2 in mapping:
                s1 = mapping[c1]
                s2 = mapping[c2]
                A += (2/ float(nonzeros))* (p_single[c1] + p_single[c2])*similarity_c_c[(c1,c2)]*(distance_level_0[(s1,s2)])              
    
    objective =  w_p*P + w_a*A + w_f*F + w_e*E
    return objective, P, A, F, E
    

def get_linear_costs(w_p, w_a, w_f, w_e, 
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics):
    
    """ computes the linear cost: for each linear variable x[c,s] compute the P, A, F and E term (as if it is chosen)
        Returns the linear cost for each objective and the weighted sum.                
    """

    x_P = {} 
    x_A = {} 
    x_F = {} 
    x_E = {} 

    for c in characters: 
        for s in keyslots: 
            P=0
            A=0
            #if that character was previously not on azerty, distance is 0.
            F = p_single[c] * distance_level_1.get((s, azerty.get(c,"NaN")),0)
            E=0
            for l in letters:
                #update performance
                if (c,l) in p_bigram:
                    P += (p_bigram[(c,l)]*performance[(s,azerty[l])]) 
                if (l,c) in p_bigram:
                    P += (p_bigram[(l,c)]*performance[(azerty[l],s)])            
                #update association. This is symmetric, so we add it twice to make it comparable with the other scores
                if (c,l) in similarity_c_l:
                    A += 2*((p_single[c] + p_single[l])*similarity_c_l[(c,l)]*distance_level_0[s,azerty[l]])
                #update ergonomics
                if (c,l) in p_bigram:                
                    E += (p_bigram[(c,l)]*ergonomics[(s,azerty[l])])
                if (l,c) in p_bigram:
                    E += (p_bigram[(l,c)]*ergonomics[(azerty[l],s)])
            x_P[c,s] = P
            x_A[c,s] = A
            x_F[c,s] = F
            x_E[c,s] = E
    #now normalize these terms such that they are all between 0 and 1

    x_P = normalize_dict_values(x_P)
    x_A = normalize_dict_values(x_A)
    x_F = normalize_dict_values(x_F)
    x_E = normalize_dict_values(x_E)

    #weighted sum of linear terms
    linear_cost = {}
    for c in characters: 
        for s in keyslots:
            linear_cost[c,s] = w_p * x_P[c,s] + w_a*x_A[c,s] + w_f*x_F[c,s] + w_e*x_E[c,s]         
    return linear_cost, x_P, x_A, x_F, x_E

def normalize_dict_values(d):
    """
    Normalizes all values to be between 0 and 1, then divides them by the number of non-zero values 
    to make them comparable with association scores, for which many values are 0
    """
    nonzeros = len([v for v in d.values() if not v == 0])
    maximum = np.max(d.values())
    minimum = np.min(d.values())

    for k, v in d.iteritems():
        d[k] = v / float(maximum - minimum)
        d[k] = d[k] / float(nonzeros)
        return d
    
def neighborhood(s, n, keyslots, distances):
    return [s2 for s2 in keyslots if distances[s,s2]<= n and (not s == s2)]