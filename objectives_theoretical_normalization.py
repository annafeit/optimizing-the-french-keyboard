from read_input import * 
from test_model import*
import numpy as np 
PYTHONIOENCODING="utf-8"

def get_objectives(mapping, w_p, w_a, w_f, w_e, corpus_weights,quadratic=0):
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
     = get_all_input_values(corpus_weights)
                   
        
    return accu_get_objectives(mapping, w_p, w_a, w_f, w_e, \
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics, quadratic=quadratic)

def accu_get_objectives(mapping, w_p, w_a, w_f, w_e,\
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
    
    for c, s in {c:s for c,s in mapping.iteritems()}.iteritems():
        if not c in characters:
            mapping.pop(c)  
            print("%s not in the to-be-mapped character set"%c)
        elif not s in keyslots:
            mapping.pop(c)  
            print("%s not mapped to a keyslot for which we have values"%s)

    P=0
    A=0
    F=0
    E=0
    for c, s in mapping.iteritems():        
        P+=x_P[c,s]            
        A+=x_A[c,s]
        #if x_A[c,s]>0:
            #print '%s: %f'%(c, x_A[c,s])
        F+=x_F[c,s]
        E+=x_E[c,s] 
    lin_A = A
    print 'linear Association: %.4f'%lin_A
    if quadratic:           
        prob_sim, distance_level_0_norm = get_quadratic_costs(characters,\
                               keyslots,\
                               p_single,distance_level_0,\
                               similarity_c_c, similarity_c_l)
        for (c1,c2) in similarity_c_c:
            if c1 in mapping and c2 in mapping:
                s1 = mapping[c1]
                s2 = mapping[c2]                
                v = prob_sim[c1,c2]*distance_level_0_norm[s1,s2]
                A += v
                #if v>0:
                    #print '%s, %s: %f'%(c1, c2, v)
    print 'quadratic Association: %.4f'%(A - lin_A)
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
                               ergonomics, 
                    theoretical_normalization = 1):
    
    """ computes the linear cost: for each linear variable x[c,s] compute the P, A, F and E term (as if it is chosen)
        Returns the linear cost for each objective and the weighted sum.                
    """
    print("Getting linear cost")
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
            #also add similarity to fixed special characters as a linear cost
            fixed_mapping = get_fixed_mapping()
            for f in fixed_mapping.keys():
                if (f,c) in similarity_c_c.keys():
                    A += 2*((p_single[c] + p_single[f])*similarity_c_l[(f,c)]*distance_level_0[s,fixed_mapping[f]])
                elif (c,f) in similarity_c_c.keys():
                    A += 2*((p_single[c] + p_single[f])*similarity_c_l[(c,f)]*distance_level_0[s,fixed_mapping[f]])
            x_P[c,s] = P
            x_A[c,s] = A
            x_F[c,s] = F
            x_E[c,s] = E
    
    if theoretical_normalization:
    #now normalize these terms such that they are all between 0 and 1
        x_P = normalize_objectives(x_P)
        x_A = normalize_objectives(x_A)
        x_F = normalize_objectives(x_F)
        x_E = normalize_objectives(x_E)
    #Ergonomics is normalized separately:
    #n = len(get_characters())
    #min_sum = 0.01
    #max_sum = 0.059
    #for k, v in x_E.iteritems():
    #    x_E[k] = (v - (min_sum/float(n))) / (float(max_sum) - float(min_sum))
    else:
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

def get_quadratic_costs(
                               characters,\
                               keyslots,\
                               p_single,\
                                distance_level_0,
                               similarity_c_c, similarity_c_l,\
                               theoretical_normalization=1):
    print("Getting quadratic cost")
    prob_sim = {}    
    for c1 in characters:
        for c2 in characters:
            if(c1,c2) in similarity_c_c.keys():
                #Unweighted!
                p = (p_single[c1] + p_single[c2])*similarity_c_c[c1,c2]
                prob_sim[(c1,c2)] = p
            else:
                prob_sim[(c1,c2)] = 0
    
    if theoretical_normalization:
        #normalize with normalization factor of full objective (later multiplied with distance)
        max_sum = 0
        min_sum = 0
        for c1 in characters: 
            #for each character determine the maximum association cost for assigning that character to a slot and sum up
            costs_per_slot_min = []
            costs_per_slot_max = []
            for s1 in keyslots:            
                tmp_sum_min = 0 #sum up the association cost for all other characters 
                tmp_sum_max = 0
                for c2 in characters:
                    if c1 != c2:
                        #add maximum association cost if that character was assigned to a key
                        tmp_sum_max += np.max([prob_sim[c1,c2]*distance_level_0[s1,s2] for s2 in keyslots if s2 != s1]) 
                        tmp_sum_min += np.min([prob_sim[c1,c2]*distance_level_0[s1,s2] for s2 in keyslots if s2 != s1]) 
                costs_per_slot_min.append(tmp_sum_min)
                costs_per_slot_max.append(tmp_sum_max)
            max_sum += np.max(costs_per_slot_max) #
            min_sum += np.min(costs_per_slot_min) #
    else:
        prob_sim = normalize_dict_values(prob_sim)
    
    
    
    #normalization factor is included in the distance because there all values are > 0. Otherwise there are some problems
    distance_level_0_norm = distance_level_0.copy()
    if theoretical_normalization:
        n = len(characters)
        for (s1,s2), v in distance_level_0.iteritems():
            if v>0:
                distance_level_0_norm[(s1,s2)] = 100*((v - (min_sum/float(n))) / (float(max_sum) - float(min_sum)))
            
    
    return prob_sim, distance_level_0_norm

def normalize_dict_values(d):
    """
    Normalizes all values to be between 0 and 1 such that they maximally sum up to 1
    """
    #normalize single values to be between 0 and 1
    maximum = np.max(d.values())
    minimum = np.min(d.values())
    
    for k, v in d.iteritems():
        d[k] = (v - minimum) / float(maximum - minimum)        
    return d

def normalize_objectives(d):
    """
     Normalize such that they maximally sum up to 100
    """   
    #for each character add up the maximum cost for assigning that character to a slot
    max_sum = 0
    min_sum = 0
    for c in get_characters():
        all_slot_values = [v for (_c,_s), v in d.iteritems() if _c==c]
        max_sum += np.max(all_slot_values)
        min_sum += np.min(all_slot_values)
        
   
    #then normalize by that
    n = len(get_characters())
    for k, v in d.iteritems():
        d[k] = 100* ((v - (min_sum/float(n))) / (float(max_sum) - float(min_sum)))
       
    return d
           
def neighborhood(s, n, keyslots, distances):
    return [s2 for s2 in keyslots if distances[s,s2]<= n and (not s == s2)]