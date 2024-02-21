"""
Module with dedicated updater functions for specific interface elements.
"""

#GUI Imports
from tkinter import * # type: ignore

import data.variables as generalVars

import interface.variables as guiVars

from simulation.shake import jj_search

from simulation.lineUpdater import updateRadTransitionVals, updateAugTransitionVals
from simulation.diagram import simu_diagram
from simulation.satellite import simu_sattelite
from simulation.auger import simu_auger

from interface.experimental import loadExp, extractExpVals

from typing import List

# --------------------------------------------------------- #
#                                                           #
#          FUNCTIONS TO UPDATE INTERFACE ELEMENTS           #
#                                                           #
# --------------------------------------------------------- #

# Update the transition that was just selected from the dropdown into the list of transitions to simulate
# This function runs whenever we one transition is selected from the dropdown
def selected(event):
    """
    Function to update the transition that was just selected from the dropdown into the list of transitions to simulate.
    This function runs whenever we one transition is selected from the dropdown
        
        Args:
            event: which dropdown element was selected
        
        Returns:
            Nothing, the selected transition toggled in the dictionary and is added to the label in the interface
    """
    # Read which transition was selected
    text_T = guiVars.drop_menu.get() # type: ignore
    # Update the dictionary for the transition
    dict_updater(text_T)
    
    if guiVars.satelite_var.get() != 'Auger': # type: ignore
        # If the transition added to the selection
        if generalVars.the_dictionary[text_T]["selected_state"]:
            guiVars.transition_list.append(text_T)
        # If it was removed
        elif not generalVars.the_dictionary[text_T]["selected_state"]:
            guiVars.transition_list.remove(text_T)
    else:
        # Same for Auger
        if generalVars.the_aug_dictionary[text_T]["selected_state"]:
            guiVars.transition_list.append(text_T)
        elif not generalVars.the_aug_dictionary[text_T]["selected_state"]:
            guiVars.transition_list.remove(text_T)
    
    # Variable with the text to be shown in the interface with the selected transitions
    to_print = ', '.join(guiVars.transition_list)
    
    # Set the interface label to the text
    guiVars.label_text.set('Selected Transitions: ' + to_print) # type: ignore
    
    # Update the 2J values in the dropdown
    if len(guiVars.transition_list) > 0:
        guiVars.drop_menu_2j['state'] = 'normal' # type: ignore
        jj_vals = jj_search(guiVars.transition_list)
        update_2j_dropdown(jj_vals)
    else:
        guiVars.drop_menu_2j['state'] = 'disabled' # type: ignore

# Function to automatically select all transitions in the dictionary. (bound to a button in the interface)
# Usefull for searching all possible theoretical lines in an experimental spectrum
def select_all_transitions():
    """
    Function to automatically select all transitions in the dictionary
    (bound to the Select All Transitions button in the interface).
    """
    min_x = 0
    max_x = 0
    
    load = guiVars.loadvar.get() # type: ignore
    if load != "No":
        exp_spectrum = loadExp(load)
        # Extract the x, y, and sigma values from the loaded experimental spectrum
        xe, ye, sigma_exp = extractExpVals(exp_spectrum)
        
        min_x = min(xe)
        max_x = max(xe)
    
    sat: str = guiVars.satelite_var.get() # type: ignore
    beam: float = guiVars.excitation_energy.get() # type: ignore
    FWHM: float = guiVars.excitation_energyFWHM.get() # type: ignore
    
    if guiVars.satelite_var.get() != 'Auger': # type: ignore
        for transition in generalVars.the_dictionary:
            _, low_level, high_level, diag_sim_val, sat_sim_val = updateRadTransitionVals(transition, 0, beam, FWHM)
            
            x, y, w = [], [], []
            xs, ys, ws = [], [], []
            if 'Diagram' in sat:
                # Store the values in a list containing all the transitions to simulate
                x, y, w = simu_diagram(diag_sim_val, beam, FWHM)
            if 'Satellites' in sat:
                # Store the values in a list containing all the transitions to simulate
                xs, ys, ws = simu_sattelite(sat_sim_val, low_level, high_level, beam, FWHM)
            
            xs = [x1 for x in xs for x1 in x]
            ws = [w1 for w in ws for w1 in w]
            ys = [y1 for y in ys for y1 in y]
            
            if any([len(i) > 0 for i in [x, y, w, xs, ys, ws]]):
                if any([x1 - w1 / 2 <= max_x and x1 + w1 / 2 > min_x for x1, w1 in zip(x, w)]) or \
                    any([x1 - w1 / 2 <= max_x and x1 + w1 / 2 > min_x for x1, w1 in zip(xs, ws)]):
                    dict_updater(transition)
                    
                    # If the transition added to the selection
                    if generalVars.the_dictionary[transition]["selected_state"]:
                        guiVars.transition_list.append(transition)
                    # If it was removed
                    elif not generalVars.the_dictionary[transition]["selected_state"]:
                        guiVars.transition_list.remove(transition)
    else:
        # Same for Auger
        for transition in generalVars.the_aug_dictionary:
            _, aug_stick_val = updateAugTransitionVals(transition, 0)
            
            # Store the values in a list containing all the transitions to simulate
            x, y, w = simu_auger(aug_stick_val, beam, FWHM)
            
            if any([len(i) > 0 for i in [x, y, w]]):
                if any([x1 - w1 / 2 <= max_x and x1 + w1 / 2 > min_x for x1, w1 in zip(x, w)]):
                    dict_updater(transition)
                    
                    if generalVars.the_aug_dictionary[transition]["selected_state"]:
                        guiVars.transition_list.append(transition)
                    elif not generalVars.the_aug_dictionary[transition]["selected_state"]:
                        guiVars.transition_list.remove(transition)
    
    # Variable with the text to be shown in the interface with the selected transitions
    to_print = ', '.join(guiVars.transition_list)
    
    # Set the interface label to the text
    guiVars.label_text.set('Selected Transitions: ' + to_print) # type: ignore
    
    # Update the 2J values in the dropdown
    if len(guiVars.transition_list) > 0:
        guiVars.drop_menu_2j['state'] = 'normal' # type: ignore
        jj_vals = jj_search(guiVars.transition_list)
        update_2j_dropdown(jj_vals)
    else:
        guiVars.drop_menu_2j['state'] = 'disabled' # type: ignore

# Function to properly reset the x limits in the interface (bound to the reset button)
def reset_limits():
    """
    Function to properly reset the x limits in the interface (bound to the reset button).
    """
    guiVars.number_points.set(500) # type: ignore
    guiVars.x_max.set('Auto') # type: ignore
    guiVars.x_min.set('Auto') # type: ignore

# Function to update the offset entries in the interface (bound to the separate toggle button)
def update_offsets(buttons_frame: Frame):
    """
    Function to update the offset entries in the interface (bound to the separate toggle button).
    """
    if guiVars.separate_offsets.get(): # type: ignore
        buttons_frame.nametowidget('sat_offsetEntry').config(state='disabled') # type: ignore
        buttons_frame.nametowidget('sat_offsetLabel').config(state='disabled') # type: ignore
        buttons_frame.nametowidget('shkoff_offsetEntry').config(state='normal') # type: ignore
        buttons_frame.nametowidget('shkoff_offsetLabel').config(state='normal') # type: ignore
        buttons_frame.nametowidget('shkup_offsetEntry').config(state='normal') # type: ignore
        buttons_frame.nametowidget('shkup_offsetLabel').config(state='normal') # type: ignore
    else:
        buttons_frame.nametowidget('sat_offsetEntry').config(state='normal') # type: ignore
        buttons_frame.nametowidget('sat_offsetLabel').config(state='normal') # type: ignore
        buttons_frame.nametowidget('shkoff_offsetEntry').config(state='disabled') # type: ignore
        buttons_frame.nametowidget('shkoff_offsetLabel').config(state='disabled') # type: ignore
        buttons_frame.nametowidget('shkup_offsetEntry').config(state='disabled') # type: ignore
        buttons_frame.nametowidget('shkup_offsetLabel').config(state='disabled') # type: ignore

# Update the selection state of a transition in the correct dictionary
def dict_updater(transition: str):
    """
    Function to update the selection state of a transition in the correct dictionary
        
        Args:
            transition: which transition to update
        
        Returns:
            Nothing, the transition is updated in the dictionaries
    """
    if guiVars.satelite_var.get() != 'Auger': # type: ignore
        # Toggle the current state of the transition
        generalVars.the_dictionary[transition]["selected_state"] = not generalVars.the_dictionary[transition]["selected_state"]
    else:
        # Toggle the current state of the transition
        generalVars.the_aug_dictionary[transition]["selected_state"] = not generalVars.the_aug_dictionary[transition]["selected_state"]

# Function to update the transitions that can be selected from the dropdown, depending on if we want to simulate radiative or auger
def update_transition_dropdown(cascade_analysis: Menu):
    """
    Function to update the transitions that can be selected from the dropdown, depending on if we want to simulate radiative or auger
    """
    if guiVars.satelite_var.get() != 'Auger': # type: ignore
        # Update the values on the dropdown
        guiVars.drop_menu['values'] = [transition for transition in generalVars.the_dictionary] # type: ignore
        if not any([generalVars.the_dictionary[transition]["selected_state"] for transition in generalVars.the_dictionary]):
            # Reset the interface text
            guiVars.label_text.set('Select a Transition: ') # type: ignore
            guiVars.drop_menu.set('Transitions:') # type: ignore
            # Deselect transitions
            for transition in generalVars.the_aug_dictionary:
                generalVars.the_aug_dictionary[transition]["selected_state"] = False
        
        cascade_analysis.entryconfigure(2, state=DISABLED)
    else:
        # Update the values on the dropdown
        guiVars.drop_menu['values'] = [transition for transition in generalVars.the_aug_dictionary] # type: ignore
        if not any([generalVars.the_aug_dictionary[transition]["selected_state"] for transition in generalVars.the_aug_dictionary]):
            # Reset the interface text
            guiVars.label_text.set('Select a Transition: ') # type: ignore
            guiVars.drop_menu.set('Transitions:') # type: ignore
            # Deselect transitions
            for transition in generalVars.the_dictionary:
                generalVars.the_dictionary[transition]["selected_state"] = False
        
        cascade_analysis.entryconfigure(2, state=NORMAL)

# Function to update the 2j values that can be selected from the dropdown, depending on the selected transitions
def update_2j_dropdown(jj_vals: List[int]):
    """
    Function to update the 2j values that can be selected from the dropdown, depending on the selected transitions
    """
    guiVars.drop_menu_2j['values'] = [str(jj) for jj in jj_vals] # type: ignore
    guiVars.jj_text.set('Select a 2J value: ') # type: ignore
    guiVars.drop_menu_2j.set("2J Values:") # type: ignore


# Update the 2j value that was just selected from the dropdown into the list of 2j values to simulate
# This function runs whenever we one 2j value is selected from the dropdown
def selected_2j(event):
    """
    Update the 2j value that was just selected from the dropdown into the list of 2j values to simulate
    This function runs whenever we one 2j value is selected from the dropdown
    
        Args:
            event: which dropdown element was selected
        
        Returns:
            Nothing, the selected 2j value is added to the label in the interface
    """
    # Read which 2j value was selected
    text_T = guiVars.drop_menu_2j.get() # type: ignore
    
    # If the 2j value was added to the selection
    if text_T not in guiVars.jj_list:
        guiVars.jj_list.append(text_T)
        generalVars.jj_vals.append(int(text_T))
    # If it was removed
    elif text_T in guiVars.jj_list:
        guiVars.jj_list.remove(text_T)
        generalVars.jj_vals.remove(int(text_T))
    
    # Variable with the text to be shown in the interface with the selected 2j values
    to_print = ', '.join(guiVars.jj_list)
    
    # Set the interface label to the text
    guiVars.jj_text.set('Selected 2J values: ' + to_print) # type: ignore

