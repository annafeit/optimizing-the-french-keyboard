# -*- coding: utf-8 -*-
from gurobipy import *
from plotting import *
from test_model import *
from objectives import *
PYTHONIOENCODING="utf-8"

capitals ={u'à':u'À',u'â':u'Â',u'ç':u'Ç',u'é':u'É',u'è':u'È',u'ê':u'Ê',\
               u'ë':u'Ë',u'î':u'Î',u'ï':u'Ï',u'ô':u'Ô',\
               u'ù':u'Ù',u'û':u'Û',u'ü':u'Ü',u'ÿ':u'Ÿ',u'æ':u'Æ',u'œ':u'Œ',\
               u'ß':u'ẞ',u'þ':u'Þ',u'ð':u'Ð',u'ŋ':u'Ŋ',u'ĳ':u'Ĳ',\
               u'ə':u'Ə',u'ʒ':u'Ʒ',u'ı':u'İ'}

directory = "mappings" 
firstline = "#"

def solve_the_keyboard_Problem(w_p, w_a, w_f, w_e, corpus_weights, quadratic=0, capitalization_constraints=1, name="final"):
    """
        A wrapper for the _solve_the_keyboard_Problem function to use the standard test variables
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
                   
    model,mapping =  _solve_the_keyboard_Problem(w_p, w_a, w_f, w_e, \
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics, quadratic=quadratic, capitalization_constraints=capitalization_constraints)
    
    #obj, P, A, F, E = accu_get_objectives(mapping, w_p, w_a, w_f, w_e, \
    #                           azerty,\
    #                           characters,\
    #                           keyslots,\
    #                           letters,\
    #                           p_single, p_bigram,\
    #                           performance,\
    #                           similarity_c_c, similarity_c_l,\
    #                           distance_level_0, distance_level_1,\
    #                           ergonomics, quadratic=quadratic)
    
    obj, P, A, F, E = get_objectives(mapping, w_p, w_a, w_f, w_e, corpus_weights,quadratic=0)
    
    plot_mapping(mapping, plotname="mappings/"+name+".png", azerty=azerty, letters=letters,\
                 objective=obj,\
                 p=P, a=A, f=F, e=E, w_p=w_p,w_a=w_a, w_f=w_f, w_e=w_e)
    
    log_mapping(mapping, "mappings/"+name+".txt", objective=obj)
    
    return mapping
    


def _solve_the_keyboard_Problem(w_p, w_a, w_f, w_e,
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics, quadratic=0, capitalization_constraints=1):    
    
    
    
    #Test some stuff in advance to avoid infeasbility:
    if len(characters) > len(keyslots):
        print "Error: more characters sthan keyslots"
        return
    
    m = Model("keyboard_layout")    
    #add decision variables
    x = {}
    for c in characters:   
        for s in keyslots:
            n = u""+c+u"_to_"+s  
            n = n.encode("utf-8")
            x[c,s] = m.addVar(vtype=GRB.BINARY, name=n)            
            
            
    m.update()
    m._vars = m.getVars()
    
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

    #Define the objective terms
    P = quicksum(
            x_P[c,s]*x[c,s]\
                for c in characters for s in keyslots
        )            
    
    A = quicksum(
            x_A[c,s]*x[c,s]\
                 for c in characters for s in keyslots
        )
    if quadratic: 
        A += 0#quicksum(
            #(p_single[c1] + p_single[c2])*similarity_c_c[(c1,c2)]*(1-distance_level_1[(s1,s2)])*x[c1,s1]*x[c2,s2]\
            #     for (c1,c2) in similarity_c_c for s1 in keyslots for s2 in keyslots)
                
        
    F = quicksum(
            x_F[c,s]*x[c,s]\
                 for c in characters for s in keyslots
        )    
        
    E = quicksum(
            x_E[c,s]*x[c,s]\
                 for c in characters for s in keyslots
        )    
     
    m._P = P
    m._A = A
    m._F = F
    m._E = E
    m._w_p = w_p
    m._w_a = w_a
    m._w_f = w_f
    m._w_e = w_e
    
    # Set objective
    m.setObjective((w_p*P)+(w_a*A)+(w_f*F)+(w_e*E), GRB.MINIMIZE)
    m.update()
    print "set objective"
    
    #add the constraints. One for each character, one for each keyslot
    for c in characters:
        m.addConstr(quicksum(x[c,s] for s in keyslots) == 1, c +  "_mapped_once")
        
    for s in keyslots:
        m.addConstr(quicksum(x[c,s] for c in characters) <= 1, s + "_assigned_at_most_once")
    
    if capitalization_constraints:
        print("Adding capitalization constraints")
        for c,s_c in capitals.iteritems():
            if c in characters and s_c in characters:
                for k in keyslots:
                    if "Shift" in k:
                        m.addConstr(x[c,k] == 0, c +  "_not_mapped_to_shifted_key_"+k)
                    else:
                        if k+"_Shift" in keyslots:
                            #if character is assigned to this key, its capital version must be assigned to shifted version of the key
                            m.addConstr(x[c,k] - x[s_c, k+"_Shift"] == 0,c +  "_and_"+s_c+"mapped_to_shifted_"+k)
                        else:
                            #unshifted version should not be assigned to key where shifted version is not available
                            m.addConstr(x[c,k] == 0, c+"_no_shift_available_"+k)
            else:
                print("%s, %s, not in character set"%(c,s_c))
            
    
    print "set constraints"
    
    m.update()
    m.write("model.lp")
    if quadratic:
        print "optimizing with quadratic terms..."
    else:
        print "optimizing with linear terms only..."
    #optimize and pass custom callback function
    m.optimize(opti_callback)
    
    

    print "done"
    
    #Output objective values:
    
    print "Performance: %.3f"%m._P.getValue()
    print "Association: %.3f"%m._A.getValue()
    print "Familiarity: %.3f"%m._F.getValue()
    print "Ergonomics: %.3f"%m._E.getValue()
    
    #Print the solution
    mapping = create_mapping(m)
    for c in characters:
        for s in keyslots:
            v=x[c,s]
            if v.x ==1:                    
                #mapping[c] = s                
                print('%s to %s' %(c,s))
            
    
    try: 
        print('Obj: %g' % m.objVal)
    except:
        print ""
    
    #print('The model is infeasible; computing IIS')
    #m.computeIIS()
    #print('\nThe following constraint(s) cannot be satisfied:')
    #for c in m.getConstrs():
    #    if c.IISConstr:
    #        print('%s' % c.constrName)     
    
    #return the model with the fixed solution
    return m, mapping



def simple_mst_writer(model, mstfilename, nodecnt, obj):
    mstfile = open(mstfilename, 'w')
    varlist = model.getVars()
    soln    = model.cbGetSolution(varlist)
    
    mstfile.write(firstline) #add first line with weights and scenario
    mstfile.write('# MIP start from soln at node %d, Objective %e\n' %(nodecnt, obj))
    mapping = {}    
    for var, soln in zip(varlist, soln):
        n = var.VarName
        mstfile.write('%s %i\n' % (n, soln))
        #if soln == 1:
        #    c = n.split("_to_")[0]
        #    s = n.split("_to_")[1]
        #    mapping[c.decode("utf-8")] = s.decode("utf-8")
    
    #This doesn't work...
    #plot_mapping(mapping, plotname=mstfilename+".png", objective=obj,\
    #             a=model._A.getValue(), p=model._P.getValue(), f=model._F.getValue(), e=model._E.getValue(),\
    #        w_p=model._w_p, w_a=model._w_a, w_f=model._w_f, w_e=model._w_e)
           
    mstfile.close()
    
    
def opti_callback(model, where):    
    try:
        if where == GRB.callback.MIPSOL:
            obj = model.cbGet(GRB.callback.MIPSOL_OBJ)
            nodecnt = int(model.cbGet(GRB.callback.MIPSOL_NODCNT))
            print 'Found incumbent soln at node', nodecnt, 'objective', obj
            simple_mst_writer(model, directory+filename+"_%.4f.mst'%obj, nodecnt, obj)
    except GurobiError as e:
        print "Gurobi Error:"
        print e.errno
        print e.message
            
def create_mapping(m):
    """ creates the mapping (dictionary) from the model's variables """
    mapping = {}
    for v in m._vars:
        if v.x ==1:
            c = v.varName.split("_to_")[0]
            s = v.varName.split("_to_")[1]
            mapping[c.decode("utf-8")] = s.decode("utf-8")       
    return mapping

def optimize_reformulation(lp_path, capitalization=1):
    #add capitalization constraints
    if capitalization:                          
        new_path = add_capitalization_constraints(lp_path)
    else:
        new_path = lp_path
                              
    global firstline
    filename = ".".join(lp_path.split("."))[:-1] 
    reformualtionFile = open("reformulation/input/"+filename+".txt",'r')
    firstline= lpfile.readline() + ",capitalization="+capitalization #save first line with weights and scenario
                              
    #add folder for logging intermediate solutions
    global directory 
    directory = directory+filename+"/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    model = read(new_path)  
    model.setParam('NodefileStart', 0.5)
    print "SETTING: nodefileStart = 0.5"
    print "optimizing..."
    #optimize and pass custom callback function
    model.optimize(opti_callback)      

    print "done"
    
    #Output objective values:
                
    if model.status == GRB.Status.INF_OR_UNBD:
        # Turn presolve off to determine whether model is infeasible
        # or unbounded
        model.setParam(GRB.Param.Presolve, 0)
        model.optimize()

    if model.status == GRB.Status.OPTIMAL:
        print('Optimal objective: %g' % model.objVal)
        model.write('model.sol')
        
    elif model.status != GRB.Status.INFEASIBLE:
        print('Optimization was stopped with status %d' % model.status)
        
    #print('The model is infeasible; computing IIS')
    #model.computeIIS()
    #print('\nThe following constraint(s) cannot be satisfied:')s
    #for c in model.getConstrs():
    #    if c.IISConstr:
    #        print('%s' % c.constrName)     
    
    #return the model with the fixed solution
    return model

def add_capitalization_constraints(lp_path):
    lp_original = open(lp_path, 'r')
    new_path = ".".join(lp_path.split(".")[:-1])+"_capital."+lp_path.split(".")[-1]
    new_lp = open(new_path, 'w')
    all_lines = lp_original.readlines()
    for i in range(0,len(all_lines)):
        new_lp.write(all_lines[i])
        if i<len(all_lines)-1:
            #if next line is the "binaries" line, add capitalization constraints here
            if "binaries" in all_lines[i+1]:
                #for each key, if the shifted version of that key is also available, 
                #enforce that for all characters mapped to that key, the capital version of the character is mapped to the shifted key
                # if the shifted version is not available as a free slot, or this is a shifted version, then enforce that the letter 
                # is not mapped to that key. 
                keyslots = get_keyslots()
                characters = get_characters()
                for k_index in range(0,len(keyslots)):
                    k = keyslots[k_index]
                    if "Shift" in k:
                        #unshifted version should not be assigned to shifted version of keyslots
                        for c, s_c in capitals.iteritems():
                            if c in characters and s_c in characters: #only if the capital version is in the to-be-mapped characters
                                c_index = characters.index(c)
                                #x(i,k) = 0
                                s = "x(%i,%i) = 0\n"%(c_index, k_index)
                                new_lp.write(s)
                    else:
                        if k+"_Shift" in keyslots:
                            #if character is assigned to this key, its capital version must be assigned to shifted version of the key
                            for c,s_c in capitals.iteritems():
                                if c in characters and s_c in characters: #only if the capital version is in the to-be-mapped characters
                                    k_shifted_index = keyslots.index(k+"_Shift")
                                    c_index = characters.index(c)
                                    s_index = characters.index(s_c)
                                    #x(i,k) - x(j,l) = 0
                                    s = "x(%i,%i) - x(%i,%i) = 0\n"%(c_index, k_index, s_index, k_shifted_index)
                                    new_lp.write(s)
                        else:
                            #unshifted version should not be assigned to key where shifted version is not available
                            for c in characters and c,s_c in capitals.iteritems():
                                if c in characters and s_c in characters: #only if the capital version is in the to-be-mapped characters
                                    c_index = characters.index(c)
                                    #x(i,k) = 0
                                    s = "x(%i,%i) = 0\n"%(c_index, k_index)
                                    new_lp.write(s)
    new_lp.close()
    lp_original.close()
    return new_path

    
def local_optimization(mapping, w_p=0.25, w_a=0.25, w_f=0.25, w_e=0.25, corpus_weights={}):
    """
    For a given mapping computes the local optimum in the neighborhood of that mapping (swapping two characters)
    """
    #read in mapping as dict
    if type(mapping)==str or type(mapping)==unicode:
        if mapping.split(".")[-1] == "mst":
            mapping, obj = create_map_from_reformulation(mapping)
        elif mapping.split(".")[-1] == "txt":
            mapping = create_map_from_txt(mapping)
        
    #Get all input data and costs
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

    prob_sim_matrix = get_quadratic_prob_similarity_matrix(characters,\
                           keyslots,\
                           p_single,\
                           similarity_c_c, similarity_c_l)

    #Function to evaluate a mapping
    def evaluate_mapping(new_map):
        P=0
        A=0
        F=0
        E=0
        for c, s in new_map.iteritems():        
            P+=x_P[c,s]            
            A+=x_A[c,s]
            F+=x_F[c,s]
            E+=x_E[c,s] 
        for (c1,c2) in similarity_c_c:
            if c1 in new_map and c2 in new_map:
                s1 = new_map[c1]
                s2 = new_map[c2]                
                v = prob_sim_matrix[c1,c2]*distance_level_0[s1,s2]
                A += v 

        objective =  w_p*P + w_a*A + w_f*F + w_e*E
        return objective, P, A, F, E

    #switch with each other character and see how the costs change
    print("Swapping characters")
    
    for c1 in characters:
        s1 = mapping[c1]
        objective, P, A, F, E = evaluate_mapping(mapping)
        min_obj = objective
        min_char = c1
        for c2 in characters:           
            new_mapping = mapping.copy()
            new_mapping[c1] = mapping[c2]
            new_mapping[c2] = s1
            objective_new, P_new, A_new, F_new, E_new = evaluate_mapping(new_mapping) 
            if objective_new < min_obj:
                min_obj = objective_new
                min_char = c2
        
        #change mapping
        if min_char != c1:
            mapping[c1] = mapping[min_char]
            mapping[min_char] = s1
            print("Swapped %s and %s"%(c1,min_char))
        
    return mapping

def check_capitalization_constraints(mapping):
    """ 
    for a given mapping checks if it fulfills the capitalization constraints
    """    
    characters = mapping.keys()
    for c, s_c in capitals.iteritems():
        if c in characters and s_c in characters:
            k = mapping[c]
            if mapping[s_c] != k+"_Shift":
                return False
    return True