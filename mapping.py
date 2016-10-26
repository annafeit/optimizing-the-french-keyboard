# -*- coding: utf-8 -*-
import pandas as pd
import codecs
import re
from read_input import *

PYTHONIOENCODING="utf-8"

def get_mapping(mapping_name):
    """
        Reads in the given mapping and returns a dictionary of letters to keys. If the given mapping is a dictionary, 
        does nothing an returns the mapping
    """
    #read in mapping
    if type(mapping_name)==str or type(mapping_name)==unicode:
        if mapping_name.split(".")[-1] == "mst":            
            mapping, obj = create_map_from_reformulation(mapping_name)
        elif mapping_name.split(".")[-1] == "txt":
            mapping = create_map_from_txt(mapping_name)
        return mapping
    else:
        return mapping_name
    
def create_map_from_txt(path):    
    """
    Reads a mapping from a file
    Each line must have the form character - space - key
    lines starting with # are ignored
    """
    mst = codecs.open(path, 'r', encoding="utf-8")    
    all_lines = mst.read().splitlines()

    mapping = {}
    for i in range(0,len(all_lines)):  
        line = all_lines[i]
        if i==0 and "#" in line:
            continue; #skip comments
        else:
            var_val = line.split(" ") 
            mapping[correct_diacritic(var_val[0].strip())] = var_val[1]
            
    mst.close()
    return mapping

def create_map_from_reformulation(path): 
    """ 
        creates the mapping from the refomulated solution .mst file
    """
    #read in characters in keyslots
    keyslots = get_keyslots()
    characters = get_characters()
    
    #read in mst file line by line and create mapping
    mst = codecs.open(path, 'r', encoding="utf-8")
    first_line = mst.readline() #optimization parameters
    snd_line = mst.readline() #objective
    parts = snd_line.split(" ")
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

def mapping_to_lisp(mapping_name, corpus_weights={}, scenario="", character_set="", full_mapping = False):
    """
        Exports the given mapping (path to the mapping) to lisp format needed by Jussi. 
        if full_mapping is set to true, writes only the letters down that are defined in the mapping (e.g. for azerty)
    """
    if scenario != "" and character_set != "":
        set_scenario_files(scenario, character_set)
    mapping = get_mapping(mapping_name)
    azerty = get_azerty()
    letters = get_letters()
    fixed = get_fixed_mapping()
    characters = get_characters()
    
    #clean mapping, remove letters that are not in the character + fixed + letter list (e.g. µ on azerty)
    for c in mapping.keys():
        if c not in letters and c not in characters and c not in fixed.keys():
            del mapping[c]
            print ("removed %s from mapping, not in letters or characters"%c)
    
    
    letter_strings = []

    row_number = {"E":0, "D":2, "C":4, "B":6}
    modifier_addition = {"": [1,0], "Shift": [0,0], "Alt":[1,1], "Alt_Shift":[0,1]}
    #write down the characters from the mapping
    for character, k in mapping.iteritems():
        if not character =="space":
            modifier = "_".join(k.split("_")[1:])
            key = k.split("_")[0]
            row = row_number[key[0]]
            key_number = int(key[1:])
            add = modifier_addition[modifier]
            r = row + add[0]
            c = key_number*2 + add[1]

            s = '("%s" %i %i)\n'%(character,r,c)
            letter_strings.append(s)

    if not full_mapping: #also write down letters and fixed characters
        #write down the letters        
        for l in letters:
            #ignore space
            if not l == "space":
                k = azerty[l]
                modifier = "_".join(k.split("_")[1:])
                key = k.split("_")[0]
                row = row_number[key[0]]
                key_number = int(key[1:])
                add = modifier_addition[modifier]
                r = row + add[0]
                c = key_number*2 + add[1]

                s = '("%s" %i %i)\n'%(l,r,c)
                letter_strings.append(s)

        #write down the fixed characters
        for character, k in fixed.iteritems():
            if not character.lower() in letters:
                modifier = "_".join(k.split("_")[1:])
                key = k.split("_")[0]
                row = row_number[key[0]]
                key_number = int(key[1:])
                add = modifier_addition[modifier]
                r = row + add[0]
                c = key_number*2 + add[1]

                s = '("%s" %i %i)\n'%(character,r,c)
                letter_strings.append(s)

    if type(mapping_name) == str:
        filename = ".".join(mapping_name.split(".")[:-1]) + ".txt"
    else:
        filename = "mappings/mapping.txt"
    f = codecs.open(filename, "w", encoding="utf-8")
    f.writelines(letter_strings)
    f.close()

    #write the probability file
    f_letter, f_bigram = get_probabilities(corpus_weights)
    prob_lines = []
    #accumulate capital letters and non-capital letter (normal letters)
    for l in letters:
        if not l == "space":
            f_letter[l] += f_letter[l.capitalize()]
            del f_letter[l.capitalize()]
    for l,v in f_letter.iteritems():
        s='("%s" %.10f)\n'%(l,v)
        prob_lines.append(s)
    for c,k in mapping.iteritems():
        if c not in f_letter:
            raise ValueError("no probability for %s"%c)
    filename = "mappings/letter_probabilities_jussi.txt"
    f = codecs.open(filename, "w", encoding="utf-8")
    f.writelines(prob_lines)  
    f.close()