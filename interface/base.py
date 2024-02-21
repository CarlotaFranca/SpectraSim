"""
Module with base window management functions.
"""

from __future__ import annotations

import data.variables as generalVars

import interface.variables as guiVars

from interface.updaters import dict_updater

#GUI Imports
from tkinter import Tk, Toplevel

# --------------------------------------------------------- #
#                                                           #
#               WINDOW MANAGEMENT FUNCTIONS                 #
#                                                           #
# --------------------------------------------------------- #

# Function to destroy the window and free memory properly
def destroy(window: Tk | Toplevel):
    """
    Function to destroy the window and free memory properly
    
        Args:
            window: the window to be disposed of
        
        Returns:
            Nothing, the window is disposed of and the program continues
    """
    window.destroy()

# Function to deselect all selected transitions when exiting the simulation window
def _quit():
    """
    Private function to deselect all selected transitions when exiting the simulation window
        
        Args:
            
        
        Returns:
            Nothing, the transition dictionaries are reset and the simulation window is disposed of
    """
    original = guiVars.satelite_var.get() # type: ignore

    guiVars.satelite_var.set('Diagram') # type: ignore

    for transition in generalVars.the_dictionary:
        if generalVars.the_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    guiVars.satelite_var.set('Auger') # type: ignore

    for transition in generalVars.the_aug_dictionary:
        if generalVars.the_aug_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    guiVars.satelite_var.set(original) # type: ignore

    guiVars._sim.quit()  # stops mainloop # type: ignore
    guiVars._sim.destroy()  # this is necessary on Windows to prevent fatal Python Error: PyEval_RestoreThread: NULL tstate # type: ignore

# Function to deselect all selected transitions and restart the whole app
def restarter():
    """
    Private function to deselect all selected transitions and restart the whole application
        
        Args:
            
        
        Returns:
            Nothing, the transition dictionaries are reset and the tkinter windows are disposed of
    """
    original = guiVars.satelite_var.get() # type: ignore

    guiVars.satelite_var.set('Diagram') # type: ignore

    for transition in generalVars.the_dictionary:
        if generalVars.the_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    guiVars.satelite_var.set('Auger') # type: ignore

    for transition in generalVars.the_aug_dictionary:
        if generalVars.the_aug_dictionary[transition]["selected_state"]:
            dict_updater(transition)

    guiVars.satelite_var.set(original) # type: ignore

    guiVars._sim.quit()  # stops mainloop # type: ignore
    guiVars._sim.destroy() # type: ignore
    guiVars._parent.destroy() # type: ignore
    main()  # this is necessary on Windows to prevent fatal Python Error: PyEval_RestoreThread: NULL tstate # type: ignore

