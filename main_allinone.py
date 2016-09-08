from objectives import * 
from read_input import *
from plotting import *
from reformulation_input import *
from evaluate_reformualtion_solution import * 
from optimize import *

PYTHONIOENCODING="utf-8"

'''
Defines weights and level costs and creates the input file for reformulating the problem
'''


#Define the weights for:
#w_p: Performance
#w_a: Association
#w_f: Familiarity
#w_e: Ergonomics
w_p, w_a, w_f, w_e = [1.0,0.0,0.0,0.0]
corpus_weights = {'formal':0.5, 'twitter':0.3, 'code':0.2}

set_scenario_files("scenario3")



#Define the extra cost for the level of the keyslot added when computing the distance between two keyslots. 
# This is used in familiarity score to punish the assignment to other levels as used on azerty.
#Example: 
#level_cost = {u'':0, u'Shift':1, u'Alt':2, u'Alt_Shift':3}
#distance[E_00, E_00_Alt] = 2
#distance[E_00_Shift, E_00_Alt] = 1
level_cost = {u'':0, u'Shift':1, u'Alt':2, u'Alt_Shift':3}

solve_the_keyboard_Problem(w_p, w_a, w_f, w_e, level_cost, corpus_weights, quadratic=0)
#Create input file for reformulating the problem
#create_reformulation_input(w_p, w_a, w_f, w_e, level_cost)

#solve reformulated problem
#model, mapping = optimize_reformulation("reformulation\\reformulation.lp")

#plot best soltion (if not stoped before)
#plot_mapping(mapping, plotname="optimum.png", w_p=w_p, w_a=w_a, w_f=w_f, w_e=w_e, level_cost=level_cost, quadratic=1)