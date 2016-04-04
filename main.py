# -*- coding: utf-8 -*-
from optimize import *
from test_model import *
from plotting import *

PYTHONIOENCODING="utf-8"


optimize_reformulation("french_kbr.lp")

#level_cost = {u'':0, u'Shift':1, u'Alt':2, u'Alt_Shift':3}

#azerty,\
#characters,\
#keyslots,\
#letters,\
#p_single, p_bigram,\
#performance,\
#similarity_c_c, similarity_c_l,\
#distance_level_0, distance_level_1,\
#ergonomics\
# = create_test_model(level_cost)
 
#w_p, w_a, w_f, w_e = [0.25, 0.25, 0.25, 0.25]

#model, mapping, x = solve_the_keyboard_Problem(w_p, w_a, w_f, w_e,\
#                               azerty,\
#                               characters,\
#                               keyslots,\
#                               letters,\
#                               p_single, p_bigram,\
#                               performance,\
#                               similarity_c_c, similarity_c_l,\
#                               distance_level_0, distance_level_1,\
#                               ergonomics, quadratic=1)

#plot_mapping(mapping, plotname="mappings\\final.png", azerty=azerty, letters=letters, objective=model.objVal )
#log_mapping(mapping, "mappings\\final.csv")
