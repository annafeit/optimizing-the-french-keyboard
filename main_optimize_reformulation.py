# -*- coding: utf-8 -*-
from objectives import * 
from optimize import *
from read_input import *
from plotting import *
from reformulation_input import *


PYTHONIOENCODING="utf-8"


'''
Defines weights and level costs, optimizes the reformulated problem and plots the results (with objectives according to the weights defined here)
'''

#Define the weights for:
#w_p: Performance
#w_a: Association
#w_f: Familiarity
#w_e: Ergonomics
w_p, w_a, w_f, w_e = [0.25, 0.25, 0.25, 0.25]

scenario = 'scenario3'
#Define the extra cost for the level of the keyslot added when computing the distance between two keyslots. 
# This is used in familiarity score to punish the assignment to other levels as used on azerty.
#Example: 
#level_cost = {u'':0, u'Shift':1, u'Alt':2, u'Alt_Shift':3}
#distance[E_00, E_00_Alt] = 2
#distance[E_00_Shift, E_00_Alt] = 1
level_cost = {u'':0, u'Shift':1, u'Alt':2, u'Alt_Shift':3}
set_scenario_files(scenario)

model, mapping = optimize_reformulation("reformulation/reformulation_input_scenario3_even.lp")
plot_mapping(mapping, plotname="optimum.png", w_p=w_p, w_a=w_a, w_f=w_f, w_e=w_e, level_cost=level_cost, quadratic=1)