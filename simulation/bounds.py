"""
Module with functions to calculate and update the simulated x bounds
"""

from __future__ import annotations

import data.variables as generalVars

from typing import List, Tuple

import numpy as np
import numpy.typing as npt

#GUI Imports for warnings
from tkinter import messagebox

# --------------------------------------------------------- #
#                                                           #
#       FUNCTIONS TO UPDATE X BOUNDS AND REBIND DATA        #
#                                                           #
# --------------------------------------------------------- #

# Calculate the x bounds from the simulated transition energy and width data (excluing satellite transitions)
def getBounds(x: List[List[float]], w: List[List[float]]) -> Tuple[List[float], float, float]:
    """
    Function to calculate the x bounds from the simulated transition energy and width data (excluing satellite transitions)
        
        Args:
            x: energy values for the simulated diagram transitions
            w: width values for the simulated diagram transitions
        
        Returns:
            deltaE: difference between the max and min energy of each transition
            max_value: maximum value to be simulated, taking into consideration all transition energies and widths
            min_value: minimum value to be simulated, taking into consideration all transition energies and widths
    """
    deltaE = []
    # Loop the values of x and calulate the range of each transition
    for j, k in enumerate(x):
        if k != []:
            deltaE.append(max(x[j]) - min(x[j]))

    # Calculate the automatic min and max values of x to be plotted
    max_value = max([max(x[i]) for i in range(len(x)) if x[i] != []]) + 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
    min_value = min([min(x[i]) for i in range(len(x)) if x[i] != []]) - 4 * max([max(w[i]) for i in range(len(w)) if w[i] != []])
    
    return deltaE, max_value, min_value

# Calculate the x bound from the simulated satellite transition energy and width data
def getSatBounds(xs: List[List[List[float]]], ws: List[List[List[float]]]):
    """
    Function to calculate the x bound from the simulated satellite transition energy and width data
        
        Args:
            xs: energy values for the simulated satellite transitions
            ws: width values for the simulated satellite transitions
        
        Returns:
            deltaE: difference between the max and min energy of each transition
            max_value: maximum value to be simulated, taking into consideration all transition energies and widths
            min_value: minimum value to be simulated, taking into consideration all transition energies and widths
    """
    deltaE: List[float] = []
    # Loop the values of x and calulate the range of each satellite transition in each diagram transition
    for j, k in enumerate(xs):
        for l, m in enumerate(xs[j]):
            if m != []:
                deltaE.append(max(m) - min(m))
    
    # Calculate the automatic min and max values of x to be plotted
    max_value = max([max(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) + max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])  # valor max de todos os elementos de xs (satt) que tem 7 linhas(ka1, ka2, etc) e o tamanho da lista label1 dentro de cada linha
    min_value = min([min(xs[i][j]) for i in range(len(xs)) for j in range(len(xs[i])) if xs[i][j] != []]) - max([max(ws[i][j]) for i in range(len(ws)) for j in range(len(ws[i])) if ws[i][j] != []])
    
    return deltaE, max_value, min_value

# Update the bounds for the user selected bounds (Auto or value)
def updateMaxMinVals(x_mx: str, x_mn: str, deltaE: List[float],
                     max_value: float, min_value: float, res: float, enoffset: float,
                     sat_enoffset: float, shkoff_enoffset: float, shkup_enoffset: float):
    """
    Function to update the bounds for the user selected bounds (Auto or value)
        
        Args:
            x_mx: user value for the maximum x value. if set to Auto we calculate it
            x_mn: user value for the minimum x value. if set to Auto we calculate it
            deltaE: delta values for each of the plotted transitions
            max_value: maximum value to be simulated, taking into consideration all transition energies and widths
            min_value: minimum value to be simulated, taking into consideration all transition energies and widths
            res: simulated experimental resolution
            enoffset: simulated energy offset
            sat_enoffset: simulated energy offset
            shkoff_enoffset: simulated energy offset
            shkup_enoffset: simulated energy offset
        
        Returns:
            array_input_max: maximum x value to be plotted
            array_input_min: minimum x value to be plotted
    """
    if x_mn == 'Auto':
        # If we are automaticaly calculating the bounds we add extra space arround the data to show possible tails of transitions
        if res <= 0.2 * (min(deltaE)):
            array_input_min = min_value - 2 * min(deltaE)
        else:
            array_input_min = min_value - 2 * res * min(deltaE)
    else:
        # We use the value in the interface while also accounting for the x offset
        array_input_min = float(x_mn) + enoffset + max([sat_enoffset, shkoff_enoffset, shkup_enoffset])
    
    if x_mx == 'Auto':
        # If we are automaticaly calculating the bounds we add extra space arround the data to show possible tails of transitions
        if res <= 0.2 * (min(deltaE)):
            array_input_max = max_value + 2 * min(deltaE)
        else:
            array_input_max = max_value + 2 * res * (min(deltaE))
    else:
        # We use the value in the interface while also accounting for the x offset
        array_input_max = float(x_mx) + enoffset + max([sat_enoffset, shkoff_enoffset, shkup_enoffset])
    
    return array_input_max, array_input_min

# Bind the experimental values into the chosen bounds
def getBoundedExp(xe: List[float] | npt.NDArray[np.float64], ye: List[float] | npt.NDArray[np.float64], sigma_exp: List[float] | npt.NDArray[np.float64],
                  enoffset: float, num_of_points: int, x_mx: str, x_mn: str):
    """
    Function to bind the experimental values into the chosen bounds.
    If Auto bounds are chosen the simulation will be performed for all the experimental spectrum span
    Otherwise we remove the experimental data that is outside the bounds we want
        
        Args:
            xe: energy values from the experimental spectrum
            ye: intensity values from the experimental spectrum
            sigma_exp: error values from the experimental spectrum
            enoffset: simulated energy offset
            num_of_points: number of simulated points
            x_mx: user value for the maximum x value. if set to Auto we calculate it
            x_mn: user value for the minimum x value. if set to Auto we calculate it
        
        Returns:
            exp_x: list of xe values inside the bounds
            exp_y: list of ye values inside the bounds
            exp_sigma: list of sigma_exp values inside the bounds
    """
    exp_x: List[float] = []
    exp_y: List[float] = []
    exp_sigma: List[float] = []
    
    # When we have an experimental spectrum loaded we use the bounds of this spectrum
    if x_mx == 'Auto':
        max_exp_lim = max(xe)
    else:
        max_exp_lim = float(x_mx)

    if x_mn == 'Auto':
        min_exp_lim = min(xe)
    else:
        min_exp_lim = float(x_mn)

    # Check if the energy value is within the bounds
    for i in range(len(xe)):
        if min_exp_lim <= xe[i] <= max_exp_lim:
            exp_x.append(xe[i])
            exp_y.append(ye[i])
            exp_sigma.append(sigma_exp[i])
    
    generalVars.exp_x = exp_x
    generalVars.exp_y = exp_y
    generalVars.exp_sigma = exp_sigma
    
    return exp_x, exp_y, exp_sigma


def calculate_xfinal(sat: str, x: List[List[float]], w: List[List[float]],
                     xs: List[List[List[float]]], ws: List[List[List[float]]],
                     x_mx: str, x_mn: str, res: float, enoffset: float, sat_enoffset: float,
                     shkoff_enoffset: float, shkup_enoffset: float, num_of_points: int, bad_selection: int):
    """
    Function to calculate the xfinal set of x values to use in the simulation.
    We take into account if an experimental spectrum is loaded, the energy of the transitions and resolution
    
        Args:
            sat: simulation type selected in the interface (diagram, satellite, auger)
            x: energy values for each of the possible transitions
            w: width values for each of the possible transitions
            xs: energy values for each of the possible radiative sattelite transitions for each radiative transition
            ws: width values for each of the possible radiative sattelite transitions for each radiative transition
            x_mx: maximum user x value from the interface
            x_mn: minimum user x value from the interface
            res: energy resolution user value from the interface
            enoffset: energy offset user value from the interface
            sat_enoffset: satellite energy offset user value from the interface
            shkoff_enoffset: shake-off energy offset user value from the interface
            shkup_enoffset: shake-up energy offset user value from the interface
            num_of_points: user value for the number of points to simulate from the interface
            bad_selection: total number of transitions that had no data
            
        Returns:
            Nothing. The xfinal is stored in the variables module to be used globaly while plotting.
    """
    diag = True
    sats = True
    
    try:
        if 'Diagram' in sat or 'Auger' in sat:
            # Get the bounds of the energies and widths to plot
            deltaEdiag, max_valuediag, min_valuediag = getBounds(x, w)
        else:
            diag = False
    except ValueError:
        diag = False
        
        if not bad_selection:
            messagebox.showerror("No Diagram Transition", "No transition was chosen")
        else:
            messagebox.showerror("Wrong Diagram Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
        
    try:
        if 'Satellites' in sat:
            # Get the bounds of the energies and widths to plot
            deltaEsat, max_valuesat, min_valuesat = getSatBounds(xs, ws)
        else:
            sats = False
    except ValueError:
        sats = False
        
        if not bad_selection:
            messagebox.showerror("No Satellite Transition", "No transition was chosen")
        else:
            messagebox.showerror("Wrong Satellite Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
    
    if diag and sats:
        deltaE = max(deltaEdiag, deltaEsat) # type: ignore
        max_value = max(max_valuediag, max_valuesat) # type: ignore
        min_value = min(min_valuediag, min_valuesat) # type: ignore
        
        # Update the bounds considering the resolution and energy offset chosen
        array_input_max, array_input_min = updateMaxMinVals(x_mx, x_mn, deltaE, max_value, min_value, res, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset)
        
        # Calculate the grid of x values to use in the simulation
        generalVars.xfinal = np.linspace(array_input_min, array_input_max, num=num_of_points)
    elif diag:
        deltaE = deltaEdiag # type: ignore
        max_value = max_valuediag # type: ignore
        min_value = min_valuediag # type: ignore
        
        # Update the bounds considering the resolution and energy offset chosen
        array_input_max, array_input_min = updateMaxMinVals(x_mx, x_mn, deltaE, max_value, min_value, res, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset)
        
        # Calculate the grid of x values to use in the simulation
        generalVars.xfinal = np.linspace(array_input_min, array_input_max, num=num_of_points)
    else:
        generalVars.xfinal = np.zeros(num_of_points)

