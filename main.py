# -*- coding: utf-8 -*-
from optimize import *
from test_model import *
from plotting import *
%matplotlib inline
PYTHONIOENCODING="utf-8"

#Define the weights for:
#w_p: Performance
#w_a: Association
#w_f: Familiarity
#w_e: Ergonomics
w_p, w_a, w_f, w_e = [0.25, 0.25, 0.25, 0.25]

#neighborhood_size: the size of the neighborhood in which we give a bonus if similar characters are close together.
# No bonus for keyslots outside that neighborhood
neighborhood_size = 4

#Define the extra cost for the level of the keyslot added when computing the distance between two keyslots. 
# This is used in familiarity score to punish the assignment to other levels as used on azerty.
#Example: 
#level_cost = {u'':0, u'Shift':1, u'Alt':2, u'Alt_Shift':3}
#distance[E_00, E_00_Alt] = 2
#distance[E_00_Shift, E_00_Alt] = 1
level_cost = {u'':0, u'Shift':1, u'Alt':2, u'Alt_Shift':3}


#optimize, plot, and save mapping
mapping = solve_the_keyboard_Problem(w_p, w_a, w_f, w_e, level_cost, neighborhood_size, quadratic=1)