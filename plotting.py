from __future__ import unicode_literals

import pandas as pd
from pandas.tools.plotting import parallel_coordinates
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib as mpl
from matplotlib import cm
import seaborn as sns
import codecs
import re
from objectives import *
from read_input import *
from mapping import *

PYTHONIOENCODING="utf-8"

#box dimensions
key_height = 4
key_width = 4

#keyboard specifics
row_distance = 0.5
column_distance = 0.5
row_shift = {'A':0, 'B':0, 'C':key_width/2, 'D':key_width, 'E':3*key_width/2}
row_numbers = {u"A":0, u"B":1, u"C":2, u"D":3, u"E":4}

#text positions
pos_normal_x = 0.5
pos_normal_y = 0.5
pos_shift_x = 0.5
pos_shift_y = key_height-0.5
pos_alt_x = key_width-0.5
pos_alt_y = 0.5
pos_alt_shift_x = key_width-0.5
pos_alt_shift_y = key_height-0.5


def swap_and_plot(mapping, char1, char2, corpus_weights, w_p, w_a, w_f, w_e, plot=True):
    #read in mapping
    if type(mapping)==str or type(mapping)==unicode:
        if mapping.split(".")[-1] == "mst":
            mapping, obj = create_map_from_reformulation(mapping)
        elif mapping.split(".")[-1] == "txt":
            mapping = create_map_from_txt(mapping)

    if char1 not in mapping:
        print("%s not in mapping"%char1)
        return
    if char2 not in mapping:
        print("%s not in mapping"%char2)
        return
    
    #create swapped mapping
    new_mapping = mapping.copy()
    new_mapping[char1] = mapping[char2]
    new_mapping[char2] = mapping[char1]
    
    
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
    
    objective, P, A, F, E = evaluate_mapping(mapping)
    new_objective, new_P, new_A, new_F, new_E = evaluate_mapping(new_mapping)
    
    plot_mapping(new_mapping, corpus_weights = corpus_weights, 
                 w_p=w_p, w_a=w_a, w_f=w_f, w_e=w_e, 
                 p=new_P, a=new_A, f=new_F, e=new_E, objective=new_objective)
    
    if plot:
        fig,axes = plt.subplots(1,2)
        fig.set_size_inches(10,5)
        w = 0.8

        axes[1].bar([0,1,2,3,4], 
                    [new_objective-objective,new_P-P,new_A-A,new_F-F,new_E-E], width=w)

        axes[1].set_xticks([0+w/2,1+w/2,2+w/2,3+w/2,4+w/2])
        axes[1].set_xticklabels(["obj", "P", "A", "F", "E"])
        axes[1].set_ylabel("Absolute difference")

        axes[0].bar([0,1,2,3,4], 
                    [100*(new_objective-objective) / objective, 100*(new_P-P)/P,100*(new_A-A)/A,100*(new_F-F)/F,100*(new_E-E)/E], width=w)

        axes[0].set_xticks([0+w/2,1+w/2,2+w/2,3+w/2,4+w/2])
        axes[0].set_xticklabels(["obj", "P", "A", "F", "E"])
        axes[0].set_ylabel("Relative difference (%)")

        fig.tight_layout()
    return new_mapping
    
def plot_mapping(mapping, plotname="", azerty=-1, numbers=-1, letters=-1,\
                 corpus_weights=-1, quadratic=1,\
                 objective=-1,\
                 p=-1, a=-1, f=-1, e=-1, w_p=-1,w_a=-1, w_f=-1, w_e=-1 ):
    """
    Plots the given mapping.
    Mapping can be a path to the mapping file, created by the reformulation, or an actual mapping. 
    If no objective is given, it computes the objective values.
    """    
    if type(mapping)==str or type(mapping)==unicode:
        if mapping.split(".")[-1] == "mst":
            mapping, obj = create_map_from_reformulation(mapping)
        elif mapping.split(".")[-1] == "txt":
            mapping = create_map_from_txt(mapping)
        
    if objective==-1:          
            objective, p, a, f, e = get_objectives(mapping, w_p, w_a, w_f, w_e, corpus_weights, quadratic=quadratic)
                    
    if azerty == -1:
        azerty = get_azerty()
    if numbers == -1:
        numbers = get_fixed_characters()
    if letters == -1:
        letters = get_letters()
        
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

    #Add fixed character annotation
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
                fontsize=14,
                fontweight='bold',
                color='k'#(0.4,0.4,0.4)        
                )
            
   
    for l in numbers:
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
            fontsize=14,
            fontweight='bold',
            color= 'k'#(0.4,0.4,0.4)        
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
            fontsize=11,
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
        Stores the given mapping in an txt file with the given path. Format:
        character key
    """
    mstfile = codecs.open(path, 'w', encoding="utf-8")
    for character, key in mapping.iteritems():        
        mstfile.write('%s %s\n' % (character, key))       
    mstfile.close()



def character_swap_with_all(mapping, char, corpus_weights, w_p, w_a, w_f, w_e):
    sns.set_style("whitegrid")
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

    if type(mapping)==str or type(mapping)==unicode:
        if mapping.split(".")[-1] == "mst":
            mapping, obj = create_map_from_reformulation(mapping)
        elif mapping.split(".")[-1] == "txt":
            mapping = create_map_from_txt(mapping)

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
    objective, P, A, F, E = evaluate_mapping(mapping)
    
    df = pd.DataFrame(columns=['P', 'A', 'F', 'E', 'obj'], index=mapping.keys())
    change_P = {}
    change_A = {}
    change_F = {}
    change_E = {}
    change_objective = {}
    for c, s in mapping.iteritems():
        if c!= char:
            new_mapping = mapping.copy()
            new_mapping[c] = mapping[char]
            new_mapping[char] = s
            objective_new, P_new, A_new, F_new, E_new = evaluate_mapping(new_mapping)
            df.loc[c] = [P_new - P, A_new - A, F_new - F, E_new - E, objective_new - objective]    
    
    fig,ax=plt.subplots(1)
    sns.boxplot(data=df, ax=ax, showfliers=False)
    xlims=ax.get_xlim()
    ax.plot(xlims, [0,0], color='k')
    ax.set_xticklabels(["P", "A", "F", "E", "obj"]);
    
    #Use this code to also plot a parallel coordinates plot
    fig, ax=plt.subplots(1)
    df_2 = df.reset_index().reset_index()
    df_2 = df_2.set_index("index")
    df_2.loc[:,"dummy"] = "0"
    df_2.columns = ["letter", "P", "A", "F", "E", "obj", "dummy"]

    min_all = df_2[["P", "A", "F", "E", "obj"]].min().min()
    max_all = df_2[["P", "A", "F", "E", "obj"]].max().max()
    diff = max_all - min_all
    df_2["letter"] = df_2.letter.apply(lambda x: (max_all*x/float(df_2.letter.max())))

    parallel_coordinates(df_2, "dummy", ax=ax)
    xlims=ax.get_xlim()
    ax.plot(xlims, [0,0], color='k')
    fig.set_size_inches(20,10)
    
    


def plot_keyboard_heatmap(values, values_norm, level_considered, title="", unit=""):
    #Plots a heatmap of the keyboard- Values must be a dictionary from key to value used for color value
    azerty = get_azerty()
    letters = get_letters()
    numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

    with open('input\\all_slots.txt') as file:    
        all_slots = file.read().splitlines()
    keyslots = get_keyslots()

    cmap = mpl.cm.winter_r




    fig, ax = plt.subplots(1,1)
    fig.set_size_inches(10,4)

    for slot in all_slots:
        row = row_numbers[slot[0]]
        column = int(slot[1:3])
        level = slot[4:]

        height = key_height
        width = key_width
        #Space
        if row==0 and column == 3:
            width = key_width*5 + 4*row_distance

        x = (column*key_width)+column*column_distance - row_shift[slot[0]]
        y = (row*key_height) + row*row_distance

        if level == "":
            ax.add_patch(
                patches.Rectangle(
                    (x,y),   # (x,y)
                    width,          # width
                    height,          # height
                    fill = False
                )
            )
        #color slots we are interested in    
        if level == level_considered and slot in values:            
            color = cmap(int(np.round(values_norm[slot]*255)))
            color = [color[0], color[1],color[2], 1.0] 

            ax.add_patch(
                patches.Rectangle(
                    (x,y),   # (x,y)
                    width,          # width
                    height,          # height
                    facecolor = color
                )    
            )


    ax.set_xlim([-8,58])
    ax.set_ylim([-1,26])
    plt.axis('off')


    #Add fixed character annotation
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
                fontsize=14,
                #fontweight='bold',
                color=(0.4,0.4,0.4)        
                )

    for l in numbers:
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
            fontsize=14,
            #fontweight='bold',
            color= (0.4,0.4,0.4)        
         )

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)

    # Set the colormap and norm to correspond to the data for which
    # the colorbar will be used.

    norm = mpl.colors.Normalize(vmin=np.min(values.values()), vmax=np.max(values.values()))

    # ColorbarBase derives from ScalarMappable and puts a colorbar
    # in a specified axes, so it has everything needed for a
    # standalone colorbar.  There are many more kwargs, but the
    # following gives a basic continuous colorbar with ticks
    # and labels.
    cb1 = mpl.colorbar.ColorbarBase(cax, cmap=cmap,
                                    norm=norm,
                                    orientation='vertical')
    cb1.set_label(unit)

    ax.set_title(title, fontsize=16)