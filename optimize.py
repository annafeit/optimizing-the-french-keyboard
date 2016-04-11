# -*- coding: utf-8 -*-
from gurobipy import *
from plotting import *
from test_model import *
PYTHONIOENCODING="utf-8"

def solve_the_keyboard_Problem(w_p, w_a, w_f, w_e, level_cost, neighborhood_size, quadratic=0):
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
     = create_test_model(level_cost)
                   
    model,mapping =  _solve_the_keyboard_Problem(w_p, w_a, w_f, w_e, neighborhood_size,\
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics, quadratic=quadratic)
    
    obj, P, A, F, E = _get_objectives(mapping, w_p, w_a, w_f, w_e, neighborhood_size,\
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics, quadratic=quadratic)
    plot_mapping(mapping, plotname="mappings\\final.png", azerty=azerty, letters=letters,\
                 objective=obj,\
                 p=P, a=A, f=F, e=E, w_p=w_p,w_a=w_a, w_f=w_f, w_e=w_e)

    log_mapping(mapping, "mappings\\final.mst", objective=obj)
    
    return mapping
    


def _solve_the_keyboard_Problem(w_p, w_a, w_f, w_e, neighborhood_size,
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics, quadratic=0):    
    
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
    
    #Define the objective terms
    P = quicksum(
            ((p_bigram[(c,l)]*performance[(s,azerty[l])]) + (p_bigram[(l,c)]*performance[(azerty[l],s)]))*x[c,s]\
                for c in characters for s in keyslots for l in letters
        )            
    
    A = quicksum(
            (p_single[c] + p_single[l])*similarity_c_l[(c,l)]*distance_level_0[s,azerty[l]]*x[c,s] \
                 for s in keyslots for (c,l) in similarity_c_l)       
    if quadratic: 
        #This part is a *bonus*. If one of those character pairs are close together (in the neighborhood), we give a bonus that corresponds
        #to the frequency*(1-distance)
        #A += quicksum(
        #    (p_single[c1] + p_single[c2])*similarity_c_c[(c1,c2)]*(1-distance_level_1[(s1,s2)])*x[c1,s1]*x[c2,s2]\
        #         for (c1,c2) in similarity_c_c for s1 in keyslots for s2 in keyslots)
                
        A += -1*(quicksum(
            (p_single[c1] + p_single[c2])*(1-distance_level_0[(s1,s2)])*x[c1,s1]*x[c2,s2]\
                 for (c1,c2) in similarity_c_c \
                    for s1 in keyslots \
                        for s2 in neighborhood(s1, neighborhood_size, keyslots, distance_level_0)))
        
    F = quicksum(
            #if that character was previously not on azerty, distance is 0.
            p_single[c] * distance_level_1.get((s, azerty.get(c,"NaN")),0)*x[c,s] \
                 for c in characters for s in keyslots
        )    
        
    E = quicksum(
            ((p_bigram[(c,l)]*ergonomics[(s,azerty[l])]) + (p_bigram[(l,c)]*ergonomics[(azerty[l],s)]))*x[c,s]\
                for c in characters for s in keyslots for l in letters
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
            simple_mst_writer(model, 'mappings\\solution_%.4f.mst'%obj, nodecnt, obj)
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

def optimize_reformulation(lp_path):
    model = read(lp_path)        
    
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
        exit(0)
    elif model.status != GRB.Status.INFEASIBLE:
        print('Optimization was stopped with status %d' % model.status)
        exit(0)
    #print('The model is infeasible; computing IIS')
    #model.computeIIS()
    #print('\nThe following constraint(s) cannot be satisfied:')s
    #for c in model.getConstrs():
    #    if c.IISConstr:
    #        print('%s' % c.constrName)     
    
    #return the model with the fixed solution
    return model, mapping


def get_objectives(mapping, w_p, w_a, w_f, w_e, level_cost, neighborhood_size, quadratic=0):
    """
        A wrapper for the _get_objectives function to use the standard test variabels
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
                   
    return _get_objectives(mapping, w_p, w_a, w_f, w_e, neighborhood_size,\
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics, quadratic=quadratic)

def _get_objectives(mapping, w_p, w_a, w_f, w_e, neighborhood_size,\
                               azerty,\
                               characters,\
                               keyslots,\
                               letters,\
                               p_single, p_bigram,\
                               performance,\
                               similarity_c_c, similarity_c_l,\
                               distance_level_0, distance_level_1,\
                               ergonomics, quadratic=0):
    """
        For a given mapping, returns the objective value for the given weights, and the individual objectives values for P,A,F,E
    """
    #remove letters from mapping
    for m in mapping.keys():
        if not m in characters:
            mapping.pop(m)
                
    P = quicksum(
            ((p_bigram[(c,l)]*performance[(s,azerty[l])]) + (p_bigram[(l,c)]*performance[(azerty[l],s)]))\
                for l in letters for c, s in mapping.iteritems() 
        )

    A = quicksum(
            (p_single[c] + p_single[l])*similarity_c_l.get((c,l),0)*distance_level_0[s,azerty[l]] \
                 for c, s in mapping.iteritems() for l in letters)       
    if quadratic:         
        #A += quicksum(
        #    (p_single[c1] + p_single[c2])*similarity_c_c[(c1,c2)]*(1-distance_level_1[(s1,s2)])*x[c1,s1]*x[c2,s2]\
        #         for (c1,c2) in similarity_c_c for s1 in keyslots for s2 in keyslots)
        #This part is a *bonus*. If one of those character pairs are close together (in the neighborhood), we give a bonus that corresponds
        #to the frequency*(1-distance)        
        A += -1*(quicksum(
            (p_single[c1] + p_single[c2])*similarity_c_c.get((c1,c2),0)*(1-distance_level_0[(mapping[c1],mapping[c2])])\
                 for (c1, s1) in mapping.iteritems() for (c2, s2) in mapping.iteritems() 
            ))
    F = quicksum(
            #if that character was previously not on azerty, distance is 0.
            p_single[c] * distance_level_1.get((s, azerty.get(c,"NaN")),0) \
                 for c, s in mapping.iteritems()
        )    
        
    E = quicksum(
            ((p_bigram[(c,l)]*ergonomics[(s,azerty[l])]) + (p_bigram[(l,c)]*ergonomics[(azerty[l],s)]))\
                for c, s in mapping.iteritems() for l in letters
        )    
    
    return w_p*P.getValue()+ w_a*A.getValue()+w_f*F.getValue()+w_e*E.getValue(),P.getValue(), A.getValue(), F.getValue(), E.getValue()
    
    
def neighborhood(s, n, keyslots, distances):
    return [s2 for s2 in keyslots if distances[s,s2]<= n and (not s == s2)]
    
        
    