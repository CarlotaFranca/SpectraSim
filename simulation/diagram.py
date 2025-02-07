"""
Module with functions that prepare diagram transtion data.
"""

from interface.plotters import stem_ploter

import data.variables as generalVars
import interface.variables as guiVars

from simulation.mults import get_cascadeBoost

from simulation.shake import calculateTotalShake

from data.definitions import Line

from typing import List

#GUI Imports for warnings
from tkinter import messagebox

from matplotlib.pyplot import Axes

# ---------------------------------------------------------------------- #
#                                                                        #
#            FUNCTIONS TO PREPARE THE DIAGRAM TRANSITION DATA            #
#                                                                        #
# ---------------------------------------------------------------------- #

def stick_diagram(graph_area: Axes, diag_stick_val: List[Line], transition: str, bad_selection: int, cs: str = ''):
    """
    Function to check and send the data to the stick plotter function for diagram transitions.
    
        Args:
            diag_stick_val: array with the rates data from the selected diagram transition
            transition: selected transition key
            bad_selection: total number of transitions that had no data
            cs: charge state value for when simulating various charge states
        
        Returns:
            bad: updated value of the total number of transitions that had no data
    """
    bad = bad_selection
    
    # Check if there is no data for the selected transition
    if not diag_stick_val:
        # Make a 0 vector to still have data to plot
        diag_stick_val = [Line() for i in range(16)]
        # Show a warning that this transition has no data and add it to the bad selection count
        messagebox.showwarning("Wrong Transition", transition + " is not Available")
        bad += 1
    
    # Extract the energy values
    x = [row.energy for row in diag_stick_val]
    """
    Energy values for the selected transition
    """
    
    if guiVars.include_cascades.get(): # type: ignore
        if len(generalVars.radBoostMatrixDict) == 0:
            get_cascadeBoost('diagram')
    
    # Plot the transition
    y = [row.effectiveIntensity(-1.0, 1.0, 1.0, guiVars.include_cascades.get(), 'diagram') for row in diag_stick_val] # type: ignore
    """
    Intensity values for the selected diagram or auger transition
    """
    
    JJ = [row.jji for row in diag_stick_val]
    
    graph_area = stem_ploter(graph_area, x, y, JJ,
                             transition if cs == '' else cs + ' ' + transition,
                             'Diagram' if cs == '' else 'Diagram_CS')
    
    return bad, graph_area


def simu_diagram(diag_sim_val: List[Line], beam: float, FWHM: float, shake_amps: dict = {}):
    """
    Function to organize the data to be sent to the plotter function for diagram transitions.
    
        Args:
            diag_sim_val: array with the rates data from the selected diagram transition
            beam: beam energy value from the interface to control if we need to multiply by the overlap
            cs: charge state flag to know if we need to multiply by the mixing fraction
        
        Returns:
            x1: energy values for every line possible within the selected transition
            y1: intensity values for every line possible within the selected transition
            w1: width values for every line possible within the selected transition
    """
    # Extract the energies, intensities and widths of the transition (different j and eigv)
    x1 = [row.energy for row in diag_sim_val]
    w1 = [row.totalWidth for row in diag_sim_val]
    
    if guiVars.include_cascades.get(): # type: ignore
        if len(generalVars.radBoostMatrixDict) == 0:
            get_cascadeBoost('diagram')
    
    if guiVars.exc_mech_var.get() == 'EII': # type: ignore
        crossSection = generalVars.elementMRBEB
    elif guiVars.exc_mech_var.get() == 'PIon': # type: ignore
        #We have the elam photospline but it would make no diference as it would be the same value for all orbitals of the same element
        #TODO: Find a way to calculate this for every orbital, maybe R-matrix
        crossSection = 1.0
    else:
        crossSection = 1.0
    
    y1 = [row.effectiveIntensity(beam, FWHM, crossSection, guiVars.include_cascades.get(), 'diagram', shake_amps = shake_amps) for row in diag_sim_val] # type: ignore
    
    return x1, y1, w1

