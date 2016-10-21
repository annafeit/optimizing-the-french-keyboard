from objectives import * 
import subprocess
from read_input import *
from plotting import *
from reformulation_input import *
from evaluate_reformualtion_solution import * 
from optimize import *
import sys

PYTHONIOENCODING="utf-8"

if len(sys.argv)==7: #first argument is the name
	w_p = float(sys.argv[1])
	w_a = float(sys.argv[2])
	w_f = float(sys.argv[3])
	w_e = float(sys.argv[4])
	scenario = sys.argv[5]
	char_set = sys.argv[6]
else:
	#Define scenario and weights
	w_p, w_a, w_f, w_e =  [0.25,0.25,0.25,0.25]
	scenario = "scenarioMIN"
	char_set = "setFULL"	
	
corpus_weights = {'formal':0.5, 'twitter':0.3, 'code':0.2}

set_scenario_files(scenario, char_set)

#prepare input file to reformulate the problem
filename=scenario+char_set+"_even"
create_reformulation_input(w_p, w_a, w_f, w_e, corpus_weights, filename,
                           quadratic=1)
						   
#run c++ code to reformulate the problem
print("REFORMULATE")						   
filein = open("reformulation/input/"+filename+".txt")
fileout = open("reformulation/input/"+filename+".lp", 'w')
subprocess.call('./reformulation/kaufmanbroeckx', stdin=filein, stdout=fileout, shell=True)
fileout.flush()

#optimize the reformulation
optimize_reformulation("reformulation/input/"+filename+".lp", capitalization=1)
