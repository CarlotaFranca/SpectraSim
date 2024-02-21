"""
Module for the functions that setup the experimental spectrum GUI elements
"""

import data.variables as generalVars

import interface.variables as guiVars

#Experimental spectrum plotter
from interface.plotters import plotExp

#Experimental spectrum data
from utils.misc.fileIO import loadExp

#Experimental bounds
from simulation.bounds import getBoundedExp

#Experimental spectrum
from utils.experimental.expSpectra import extractExpVals

from matplotlib import gridspec
from matplotlib.figure import Figure

import numpy as np

# --------------------------------------------------------- #
#                                                           #
#           FUNCTIONS TO PLOT EXPERIMENTAL DATA             #
#                                                           #
# --------------------------------------------------------- #

# Function to setup the experimental plot when we load one and the residue plot
def setupExpPlot(f: Figure, load: str, element_name: str):
    """
    Function to setup the experimental plot when we load one and the residue plot
        
        Args:
            f: matplotlib figure object
            load: file path to the experimental spectrum selected
            element_name: name of the element we are simulating
        
        Returns:
            graph_area: new matplotlib plot configured to make space for the residue graph
            residues_graph: matplotlib plot for the residue data
            exp_spectrum: experimental spectrum data loaded from file
    """
    
    # Clear the plot
    f.clf()
    # Split the figure plot into two with the first having 3 times the height
    gs = gridspec.GridSpec(2, 1, height_ratios=np.array([3, 1]))
    # Add the first subplot to the figure
    graph_area = f.add_subplot(gs[0])
    
    # Set the logarithmic axes if needed
    if guiVars.yscale_log.get() == 'Ylog': # type: ignore
        graph_area.set_yscale('log')
    if guiVars.xscale_log.get() == 'Xlog': # type: ignore
        graph_area.set_xscale('log')
    # Add the name of the plot
    graph_area.legend(title=element_name)
    # Add the second subplot for the residues
    residues_graph = f.add_subplot(gs[1])
    # Set the axes labels
    residues_graph.set_xlabel('Energy (eV)')
    residues_graph.set_ylabel('Residues (arb. units)')
    
    # Read and load the experimental spectrum file
    exp_spectrum = loadExp(load)
    
    guiVars._residues_graph = residues_graph
    
    return graph_area, residues_graph, exp_spectrum


def initialize_expElements(f: Figure, load: str, enoffset: float, sat_enoffset: float,
                           shkoff_enoffset: float, shkup_enoffset: float, num_of_points: int,
                           x_mx: str, x_mn: str, normalize: str):
    """
    Function to initialize the elements necessary when loading an experimental spectrum.
        
        Args:
            f: matplotlib figure object where to plot the data
            load: path to the experimental spectrum loaded in the interface ('No' if no spectrum has been loaded)
            enoffset: energy offset user value from the interface
            num_of_points: user value for the number of points to simulate from the interface
            x_mx: maximum user x value from the interface
            x_mn: minimum user x value from the interface
        
        Returns:
            Nothing. The elements are initialized and the interface is updated.
    """
    # Initialize the residue plot and load the experimental spectrum
    graph_area, residues_graph, exp_spectrum = setupExpPlot(f, load, str(generalVars.element_name))
    # Extract the x, y, and sigma values from the loaded experimental spectrum
    xe, ye, sigma_exp = extractExpVals(exp_spectrum)
    # Bind the experimental spectrum to the calculated bounds
    generalVars.exp_x, generalVars.exp_y, generalVars.exp_sigma = getBoundedExp(xe, ye, sigma_exp, enoffset + max([sat_enoffset, shkoff_enoffset, shkup_enoffset]), num_of_points, x_mx, x_mn)
    # Calculate the final energy values
    generalVars.xfinal = np.array(np.linspace(min(generalVars.exp_x) + enoffset + max([sat_enoffset, shkoff_enoffset, shkup_enoffset]), max(generalVars.exp_x) + enoffset + max([sat_enoffset, shkoff_enoffset, shkup_enoffset]), num=num_of_points))
    # plot the experimental spectrum and residues graph
    plotExp(graph_area, residues_graph, generalVars.exp_x, generalVars.exp_y, generalVars.exp_sigma, normalize)
    
    return graph_area, exp_spectrum
