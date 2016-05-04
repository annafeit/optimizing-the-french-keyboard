from __future__ import unicode_literals

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import codecs
import re
from objectives import *

PYTHONIOENCODING="utf-8"


def plot_mapping(mapping, plotname="", azerty=-1, numbers=-1, letters=-1,\
                 level_cost=-1, quadratic=-1,\
                 objective=-1,\
                 p=-1, a=-1, f=-1, e=-1, w_p=-1,w_a=-1, w_f=-1, w_e=-1 ):
    """
    Plots the given mapping.
    Mapping can be a path to the mapping file, created by the reformulation, or an actual mapping. 
    If no objective is given, it computes the objective values.
    """
    if type(mapping)==string:       
        mapping, obj = create_map_from_reformulation(path)
        
    if objective==-1:        
        if not level_cost == -1:
            objective, p, a, f, e = get_objectives(mapping, w_p, w_a, w_f, w_e, level_cost, quadratic=quadratic)
                    
    if azerty == -1:
        azerty = pd.read_csv("input\\azerty.csv", index_col=1, sep="\t", encoding='utf-8', quoting=3).to_dict()["keyslot"]
    if numbers == -1:
        numbers = pd.read_csv("input\\numbers.csv", index_col=1, sep="\t", encoding='utf-8', quoting=3).to_dict()["keyslot"]
    if letters == -1:
        with codecs.open('input\\letters.txt', encoding='utf-8') as file:
            letters = file.read().splitlines()   
        
    with open('input\\all_slots.txt') as file:    
        all_slots = file.read().splitlines()    
    #box dimensions
    key_height = 4
    key_width = 4

    #keyboard specifics
    row_distance = 0.5
    column_distance = 0.5
    row_shift = {'A':0, 'B':0, 'C':key_width/2, 'D':key_width, 'E':3*key_width/2}

    #text positions
    pos_normal_x = 0.5
    pos_normal_y = 0.5
    pos_shift_x = 0.5
    pos_shift_y = key_height-0.5
    pos_alt_x = key_width-0.5
    pos_alt_y = 0.5
    pos_alt_shift_x = key_width-0.5
    pos_alt_shift_y = key_height-0.5


    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(10,4)
    row_numbers = {u"A":0, u"B":1, u"C":2, u"D":3, u"E":4}
    for slot in all_slots:
        row = row_numbers[slot[0]]
        column = int(slot[1:3])
        level = slot[4:]

        if level == "":
            height = key_height
            width = key_width
            #Space
            if row==0 and column == 3:
                width = key_width*5 + 4*row_distance

            x = (column*key_width)+column*column_distance - row_shift[slot[0]]
            y = (row*key_height) + row*row_distance

            ax.add_patch(
                patches.Rectangle(
                    (x,y),   # (x,y)
                    width,          # width
                    height,          # height
                    fill=False
                )
    )

    #Add letter annotation
    for l in letters:
        if not l == "space":
            slot = azerty[l]
            row = row_numbers[slot[0]]
            column = int(slot[1:3])
            level = slot[4:]

            if level == "":
                pos_x = pos_normal_x
                pos_y = pos_normal_y
                ha = 'left'
                va = 'bottom'
            if level == "Shift":
                pos_x = pos_shift_x
                pos_y = pos_shift_y
                ha = 'left'
                va = 'top'
            if level == "Alt":
                pos_x = pos_alt_x
                pos_y = pos_alt_y
                ha = 'right'
                va = 'bottom'
            if level == "Alt_Shift":
                pos_x = pos_alt_shift_x
                pos_y = pos_alt_shift_y
                ha = 'right'
                va = 'top'
            x = (column*key_width)+column*column_distance + pos_x - row_shift[slot[0]]
            y = (row*key_height) + row*row_distance + pos_y

            ax.text(x,y,l,            
                horizontalalignment=ha,
                verticalalignment=va,
                fontsize=10,
                color=(0.4,0.4,0.4)        
                )
            
    #Add number annotation
    for (l,slot) in numbers.iteritems():                    
        row = row_numbers[slot[0]]
        column = int(slot[1:3])
        level = slot[4:]

        if level == "":
            pos_x = pos_normal_x
            pos_y = pos_normal_y
            ha = 'left'
            va = 'bottom'
        if level == "Shift":
            pos_x = pos_shift_x
            pos_y = pos_shift_y
            ha = 'left'
            va = 'top'
        if level == "Alt":
            pos_x = pos_alt_x
            pos_y = pos_alt_y
            ha = 'right'
            va = 'bottom'
        if level == "Alt_Shift":
            pos_x = pos_alt_shift_x
            pos_y = pos_alt_shift_y
            ha = 'right'
            va = 'top'
        x = (column*key_width)+column*column_distance + pos_x - row_shift[slot[0]]
        y = (row*key_height) + row*row_distance + pos_y

        ax.text(x,y,l,            
            horizontalalignment=ha,
            verticalalignment=va,
            fontsize=10,
            color=(0.4,0.4,0.4)        
         )
           
    #Add mapping annotation
    for (l,slot) in mapping.iteritems():        
        row = row_numbers[slot[0]]
        column = int(slot[1:3])
        level = slot[4:]        

        if level == "":
            pos_x = pos_normal_x
            pos_y = pos_normal_y
            ha = 'left'
            va = 'bottom'
        if level == "Shift":
            pos_x = pos_shift_x
            pos_y = pos_shift_y
            ha = 'left'
            va = 'top'
        if level == "Alt":
            pos_x = pos_alt_x
            pos_y = pos_alt_y
            ha = 'right'
            va = 'bottom'
        if level == "Alt_Shift":
            pos_x = pos_alt_shift_x
            pos_y = pos_alt_shift_y
            ha = 'right'
            va = 'top'
        x = (column*key_width)+column*column_distance + pos_x - row_shift[slot[0]]
        y = (row*key_height) + row*row_distance + pos_y

        if u"d" in l: #dead key
            l = re.sub('d', '', l)
            c = "#C44E52"
        else:
            c = "#4C72B0"
            
        ax.text(x,y,l,            
            horizontalalignment=ha,
            verticalalignment=va,
            fontsize=12,
            color=c        
            )
    title = ""
    if not objective==-1:
        #print objective values
        title = "Objective value: %.3f"%objective
    if not (a==-1 or e==-1 or f==-1 or p==-1):
        title = title+ " \n Performance: %.2f * %.3f \n Association: %.2f * %.3f \n Familiarity: %.2f * %.3f \n\
        Ergonomics: %.2f * %.3f "%(w_p, p, w_a, a, w_f, f, w_e, e)
    ax.set_title(title, horizontalalignment="right")
    ax.set_xlim([-8,58])
    ax.set_ylim([-1,26])
    plt.axis('off')
    if not plotname=="":
        fig.savefig(plotname, dpi=300, bbox_inches='tight')	    
    
def log_mapping(mapping, path, objective=""):
    """
        Stores the given mapping in an mst file with the given path. Format:
        character key
    """
    mstfile = open(path, 'w')
    varlist = model.getVars()
    soln    = model.cbGetSolution(varlist)
    if not objective=="":
        mstfile.write('# Objective %e\n' %(obj))
    mapping = {}    
    for character, key in mapping.iteritems():        
        mstfile.write('%s %i\n' % (character, key))
        
    mstfile.close()

def create_map_from_mst(path):    
    mst = codecs.open(path, 'r', encoding="utf-8")
    first_line = mst.readline()
    parts = first_line.split(" ")
    objective = float(parts[-1])
    all_lines = mst.read().splitlines()

    mapping = {}
    for line in all_lines:
        var_val = line.split(" ")
        if var_val[1] == "1":
            maps = var_val[0].split("_to_")
            mapping[maps[0]] = maps[1]
    return mapping, objective

def create_map_from_reformulation(path): 
    """ 
        creates the mapping from the refomulated solution .mst file
    """
    #read in characters in keyslots
    with codecs.open('input\\characters.txt', encoding='utf-8') as f:
        characters = f.read().splitlines()
    with codecs.open('input\\variable_slots.txt', encoding='utf-8') as f:    
        keyslots = f.read().splitlines()   
    numbers = pd.read_csv("input\\numbers.csv", index_col=1, sep="\t", encoding='utf-8', quoting=3).to_dict()["keyslot"]
    #remove number keys from free keyslots
    for n_slot in numbers.values():        
        keyslots.remove(n_slot)

    #read in mst file line by line and create mapping
    mst = codecs.open(path, 'r', encoding="utf-8")
    first_line = mst.readline()
    parts = first_line.split(" ")
    objective = float(parts[-1])
    all_lines = mst.read().splitlines()

    mapping = {}
    for line in all_lines:        
        var_val = line.split(" ")
        variable = var_val[0]
        #take only "x" decision variables which are set to 1
        if var_val[1] == "1" and variable[0] =="x":
            #decode number
            maps = variable[2:-1].split(",")
            c_number = int(maps[0])
            s_number = int(maps[1])
            #map number to character/keyslot
            if c_number < len(characters):
                character = characters[c_number]
                slot = keyslots[s_number]
                mapping[character] = slot
    return mapping, objective