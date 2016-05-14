import os
import glob
from plotting import * 

def evaluate_optimized_reformulation(w_p, w_a, w_f, w_e, level_cost, quadratic=1):
    """
        Searches for the last (=best) mapping produced by the solver, stores a human-readable format, 
        computes its objective values and plots it. 
    """
    #find the newest mapping
    newest = max(glob.iglob('mappings\\*.mst'), key=os.path.getctime)    
    #save in human-readable format
    mapping, objective = create_map_from_reformulation(newest)    
    log_mapping(mapping, (".").join(newest.split(".")[0:-1])+".txt")
    
    #create plot
    plot_mapping(mapping, plotname=newest+".png", w_p=w_p, w_a=w_a, w_f=w_f, w_e=w_e, level_cost=level_cost, quadratic=1)