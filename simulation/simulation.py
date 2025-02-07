"""
Module with functions that group the data to be simulated and send it to the plotters in the correct format.
"""

import data.variables as generalVars
import interface.variables as guiVars

# Transition lines to simulate updater functions
from simulation.lineUpdater import updateRadTransitionVals, updateAugTransitionVals, \
                                    updateRadCSTrantitionsVals, updateAugCSTransitionsVals

# Transition simulation functions
from simulation.diagram import stick_diagram
from simulation.satellite import stick_satellite
from simulation.auger import stick_auger

# preprocessing functions to determine x, y, w lists
from simulation.preprocessors import process_simulation, process_Msimulation

#Shake vaulues setup
from simulation.shake import setupShake

# Bad selection reporting functions
from utils.experimental.detector import initialize_detectorEfficiency

from simulation.ycalc import y_calculator, normalizer, add_fitting_components
from simulation.bounds import calculate_xfinal
from simulation.fitting import calculateResidues, execute_autofit,execute_autofit_minuit

#Cross section functions import
from utils.crossSections.EIICS import setupMRBEB
from utils.crossSections.PhotoCS import setupELAMPhotoIoniz
from utils.crossSections.energies import setupFormationEnergies, setupPartialWidths

from interface.plotters import simu_plot, Msimu_plot, format_legend
from interface.experimental import initialize_expElements

from datetime import datetime

#GUI Imports for warnings
from tkinter import messagebox

from matplotlib.pyplot import Axes
from matplotlib.figure import Figure

from tkinter import Toplevel

# ---------------------------------------------------------------------- #
#                                                                        #
#  FUNCTIONS TO PREPARE THE SIMULATION DATA AND SEND IT TO THE PLOTERS   #
#                                                                        #
# ---------------------------------------------------------------------- #


def make_stick(sim: Toplevel, graph_area: Axes):
    """
    Function to calculate the values that will be sent to the stick plotter function.
        
        Args:
            sim: tkinter simulation window to update the progress bar
            graph_area: matplotlib graph to plot the simulated transitions
        
        Returns:
            Nothing, the sticks that need to be plotted are calculated and the data is sent to the plotting functions.
    """
    # Variable for the total number of plotted transitions
    num_of_transitions = 0
    # Variable for the number of transitions that were selected but no rates were found
    bad_selection = 0
    
    sat = guiVars.satelite_var.get() # type: ignore
    beam = guiVars.excitation_energy.get() # type: ignore
    FWHM = guiVars.excitation_energyFWHM.get() # type: ignore
    
    # Reset the 2J colors dictionary if needed
    if guiVars.JJ_colors.get(): # type: ignore
        generalVars.colors_2J = {}
    
    # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
    if sat != 'Auger':
        # Loop possible radiative transitions
        for transition in generalVars.the_dictionary:
            # If the transition was selected
            if generalVars.the_dictionary[transition]["selected_state"]:
                # Filter the radiative and satellite rates corresponding to this transition
                num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val = updateRadTransitionVals(transition, num_of_transitions, beam, FWHM)
                
                # -------------------------------------------------------------------------------------------
                if 'Diagram' in sat:
                    bad_selection, graph_area = stick_diagram(graph_area, diag_stick_val, transition, bad_selection)
                if 'Satellites' in sat:
                    bad_selection, graph_area = stick_satellite(sim, graph_area, sat_stick_val, transition, low_level, high_level, bad_selection)
            
    else:
        # Loop possible auger transitions
        for transition in generalVars.the_aug_dictionary:
            # If the transition is selected
            if generalVars.the_aug_dictionary[transition]["selected_state"]:
                # Filter the auger rates for this transition
                num_of_transitions, aug_stick_val = updateAugTransitionVals(transition, num_of_transitions)
                
                bad_selection, graph_area = stick_auger(graph_area, aug_stick_val, transition, bad_selection)
    
    # Set the labels for the axis
    graph_area.set_xlabel('Energy (eV)')
    graph_area.set_ylabel('Intensity (arb. units)')

    if num_of_transitions == 0:
        messagebox.showerror("No Transition", "No transition was chosen")
    elif bad_selection != 0:
        messagebox.showerror("Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
    
    return graph_area


def make_simulation(sim: Toplevel, f: Figure, graph_area: Axes, time_of_click: datetime, plotSimu: bool = True):
    """
    Function to calculate the values that will be sent to the plot function.
        
        Args:
            sim: tkinter simulation window to update the progress bar
            f: matplotlib figure object where to plot the data
            graph_area: matplotlib graph to plot the simulated transitions
            time_of_click: timestamp to use when saving files for this simulation plot
        
        Returns:
            Nothing, the simulation is performed, the transitions are plotted and the interface is updated
    """
    sat = guiVars.satelite_var.get() # type: ignore
    
    x, y, w, xs, ys, ws, bad_selection = process_simulation()

    # -------------------------------------------------------------------------------------------
    # Calculate the xfinal set of x values to use in the simulation
    num_of_points = guiVars.number_points.get() # type: ignore
    x_mx = guiVars.x_max.get() # type: ignore
    x_mn = guiVars.x_min.get() # type: ignore
    enoffset = guiVars.energy_offset.get() # type: ignore
    sat_enoffset = guiVars.sat_energy_offset.get() # type: ignore
    shkoff_enoffset = guiVars.shkoff_energy_offset.get() # type: ignore
    shkup_enoffset = guiVars.shkup_energy_offset.get() # type: ignore
    res = guiVars.exp_resolution.get() # type: ignore
    
    calculate_xfinal(sat, x, w, xs, ws, x_mx, x_mn, res, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, bad_selection)

    # ---------------------------------------------------------------------------------------------------------------
    # Load and plot the experimental spectrum
    generalVars.exp_x = []
    generalVars.exp_y = []
    generalVars.exp_sigma = []
    min_exp_lim = 0
    max_exp_lim = 0
    
    # Initialize needed elements if we have loaded an experimental spectrum
    load = guiVars.loadvar.get() # type: ignore
    
    if load != 'No':
        graph_area, exp_spectrum = initialize_expElements(f, load, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, x_mx, x_mn, guiVars.normalizevar.get()) # type: ignore

    # ---------------------------------------------------------------------------------------------------------------
    # Read the efficiency file if it was loaded
    energy_values = []
    efficiency_values = []
    
    effic_file_name = guiVars.effic_var.get() # type: ignore
    
    if effic_file_name != 'No':
        energy_values, efficiency_values = initialize_detectorEfficiency(effic_file_name)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Calculate the final y values
    peak = guiVars.type_var.get() # type: ignore
    
    generalVars.ytot, generalVars.ydiagtot, generalVars.ysattot, generalVars.yshkofftot, \
        generalVars.yshkuptot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, generalVars.xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset)

    # Add the extra fitting components
    if len(generalVars.extra_fitting_functions) > 0:
        generalVars.yextras.resize((len(generalVars.extra_fitting_functions), len(generalVars.xfinal)))
        print(generalVars.extra_fitting_functions)
        for i, key in enumerate(generalVars.extra_fitting_functions):
            function = key.split("_")[1]
            pars = generalVars.extra_fitting_functions[key]
            
            if function == 'Gaussian':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), pars['GwidthParVal'])
            elif function == 'Lorentzian':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), 0.0, pars['LwidthParVal'])
            elif function == 'Voigt':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), pars['GwidthParVal'], pars['LwidthParVal'])
        
    # ---------------------------------------------------------------------------------------------------------------
    # Calculate the normalization multiplyer
    y0 = guiVars.yoffset.get() # type: ignore
    
    if load != 'No':
        normalization_var = normalizer(y0, max(generalVars.exp_y), max(generalVars.ytot))
    else:
        # If we try to normalize without an experimental spectrum
        if guiVars.normalizevar.get() == 'ExpMax': # type: ignore
            messagebox.showwarning("No experimental spectrum is loaded", "Choose different normalization option")
            # Reset the normalizer to the default
            guiVars.normalizevar.set('No') # type: ignore
        normalization_var = normalizer(y0, 1, max(generalVars.ytot))
    
    # ---------------------------------------------------------------------------------------------------------------
    # Autofit:
    number_of_fit_variables = 0
    if guiVars.autofitvar.get() == 'LMFit': # type: ignore
        #guiVars.autofitvar_minuit.set("No")
        # We can only fit if we have an experimental spectrum
        if load != 'No':
            number_of_fit_variables, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, normalization_var, extra_pars = execute_autofit(sim, sat, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, num_of_points, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, time_of_click)
        else:
            messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
    else:
    #if guiVars.autofitvar.get() == 'iminuit': # type: ignore
        #guiVars.autofitvar_lmfit.set("No")
        # We can only fit if we have an experimental spectrum
        if load != 'No':
            number_of_fit_variables, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, normalization_var, extra_pars = execute_autofit_minuit(sim, sat, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, num_of_points, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, time_of_click)
        else:
            messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Plot the selected lines
    graph_area = simu_plot(sat, graph_area, normalization_var, y0, plotSimu) # type: ignore
    # print(generalVars.ytot)
    # print(normalization_var)
    # ------------------------------------------------------------------------------------------------------------------------
    # Calculate the residues
    if load != 'No':
        calculateResidues(generalVars.exp_x, generalVars.exp_y, generalVars.exp_sigma, generalVars.xfinal, normalization_var, guiVars.normalizevar.get(), y0, number_of_fit_variables, guiVars._residues_graph) # type: ignore
    
    if plotSimu:
        # ------------------------------------------------------------------------------------------------------------------------
        # Set the axis labels
        graph_area.set_ylabel('Intensity (arb. units)')
        graph_area.legend(title=generalVars.element_name, title_fontsize='large')
        if load == 'No':
            graph_area.set_xlabel('Energy (eV)')
        
        # ------------------------------------------------------------------------------------------------------------------------
        # Automatic legend formating
        format_legend(graph_area)
    
    return graph_area



def make_Mstick(sim: Toplevel, graph_area: Axes):
    """
    Function to calculate the values that will be sent to the stick plotter function when simulating a mixture of charge states.
        
        Args:
            sim: tkinter simulation window to update the progress bar
            graph_area: matplotlib graph to plot the simulated transitions
        
        Returns:
            Nothing, the sticks that need to be plotted are calculated and the data is sent to the plotting functions.
    """
    # Variable for the total number of plotted transitions
    num_of_transitions = 0
    # Variable for the number of transitions that were selected but no rates were found
    bad_selection = 0
    
    sat: str = guiVars.satelite_var.get() # type: ignore
    beam: float = guiVars.excitation_energy.get() # type: ignore
    FWHM: float = guiVars.excitation_energyFWHM.get() # type: ignore
    
    # Reset the 2J colors dictionary if needed
    if guiVars.JJ_colors.get(): # type: ignore
        generalVars.colors_2J = {}
    
    # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
    if sat != 'Auger':
        # Initialize the charge states we have to loop through
        charge_states = generalVars.rad_PCS + generalVars.rad_NCS

        # Loop the charge states
        for cs_index, cs in enumerate(charge_states):
            # Initialize the mixture value chosen for this charge state
            mix_val = '0.0'
            # Flag to check if this is a negative or positive charge state
            ncs = False

            # Check if this charge state is positive or negative and get the mix value
            if cs_index < len(generalVars.rad_PCS):
                mix_val = guiVars.PCS_radMixValues[cs_index].get()
            else:
                mix_val = guiVars.NCS_radMixValues[cs_index - len(generalVars.rad_PCS)].get()
                ncs = True
            
            # Check if the mix value is not 0, otherwise no need to plot the transitions for this charge state
            if mix_val != '0.0':
                # Loop the possible radiative transitions
                for transition in generalVars.the_dictionary:
                    # If the transition is selected
                    if generalVars.the_dictionary[transition]["selected_state"]:
                        # Filter the radiative and satellite rates for this transition and charge state
                        num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val = updateRadCSTrantitionsVals(transition, num_of_transitions, ncs, cs)
                        
                        if 'Diagram' in sat:
                            bad_selection, graph_area = stick_diagram(graph_area, diag_stick_val, transition, bad_selection, cs)
                        if 'Satellites' in sat:
                            bad_selection, graph_area = stick_satellite(sim, graph_area, sat_stick_val, transition, low_level, high_level, bad_selection, cs)
                    
    else:
        # Initialize the charge states we have to loop through
        charge_states = generalVars.aug_PCS + generalVars.aug_NCS

        # Loop the charge states
        for cs_index, cs in enumerate(charge_states):
            # Initialize the mixture value chosen for this charge state
            mix_val = '0.0'
            # Flag to check if this is a negative or positive charge state
            ncs = False

            # Check if this charge state is positive or negative and get the mix value
            if cs_index < len(generalVars.aug_PCS):
                mix_val = guiVars.PCS_augMixValues[cs_index].get()
            else:
                mix_val = guiVars.NCS_augMixValues[cs_index - len(generalVars.aug_PCS)].get()
                ncs = True
            
            # Check if the mix value is not 0, otherwise no need to plot the transitions for this charge state
            if mix_val != '0.0':
                # Loop the possible auger transitions
                for transition in generalVars.the_aug_dictionary:
                    # If the transition is selected
                    if generalVars.the_aug_dictionary[transition]["selected_state"]:
                        # Filter the auger rates for this transition and charge state
                        num_of_transitions, aug_stick_val = updateAugCSTransitionsVals(transition, num_of_transitions, ncs, cs)
                        
                        bad_selection, graph_area = stick_auger(graph_area, aug_stick_val, transition, bad_selection, cs)

    # Set the labels for the axis
    graph_area.set_xlabel('Energy (eV)')
    graph_area.set_ylabel('Intensity (arb. units)')

    if num_of_transitions == 0:
        messagebox.showerror("No Transition", "No transition was chosen")
    elif bad_selection != 0:
        messagebox.showerror("Wrong Transition", "You chose " + str(bad_selection) + " invalid transition(s)")
    
    return graph_area


def make_Msimulation(sim: Toplevel, f: Figure, graph_area: Axes, time_of_click: datetime):
    """
    Function to calculate the values that will be sent to the plot function.
        
        Args:
            sim: tkinter simulation window to update the progress bar
            f: matplotlib figure object where to plot the data
            graph_area: matplotlib graph to plot the simulated transitions
            time_of_click: timestamp to use when saving files for this simulation plot
            
        Returns:
            Nothing, the simulation is performed, the transitions are plotted and the interface is updated
    """
    sat = guiVars.satelite_var.get() # type: ignore

    x, y, w, xs, ys, ws, bad_selection = process_Msimulation()
    
    # -------------------------------------------------------------------------------------------
    # Calculate the xfinal set of x values to use in the simulation
    enoffset = guiVars.energy_offset.get() # type: ignore
    sat_enoffset = guiVars.sat_energy_offset.get() # type: ignore
    shkoff_enoffset = guiVars.shkoff_energy_offset.get() # type: ignore
    shkup_enoffset = guiVars.shkup_energy_offset.get() # type: ignore
    res = guiVars.exp_resolution.get() # type: ignore
    num_of_points = guiVars.number_points.get() # type: ignore
    x_mx = guiVars.x_max.get() # type: ignore
    x_mn = guiVars.x_min.get() # type: ignore
    
    calculate_xfinal(sat, x, w, xs, ws, x_mx, x_mn, res, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, bad_selection)

    # ---------------------------------------------------------------------------------------------------------------
    # Load and plot the experimental spectrum
    generalVars.exp_x = []
    generalVars.exp_y = []
    generalVars.exp_sigma = []
    min_exp_lim = 0
    max_exp_lim = 0
    
    # If we have loaded an experimental spectrum
    load = guiVars.loadvar.get() # type: ignore
    
    if load != 'No':
        graph_area, exp_spectrum = initialize_expElements(f, load, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, num_of_points, x_mx, x_mn, guiVars.normalizevar.get()) # type: ignore

    # ---------------------------------------------------------------------------------------------------------------
    # Read the efficiency file if it was loaded
    efficiency_values = []
    energy_values = []
    
    effic_file_name = guiVars.effic_var.get() # type: ignore
    
    if effic_file_name != 'No':
        energy_values, efficiency_values = initialize_detectorEfficiency(effic_file_name)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Calculate the final y values
    peak = guiVars.type_var.get() # type: ignore
    
    generalVars.ytot, generalVars.ydiagtot, generalVars.ysattot, generalVars.yshkofftot, \
        generalVars.yshkuptot, generalVars.yfinal, generalVars.yfinals = y_calculator(sim, sat, peak, generalVars.xfinal, x, y, w, xs, ys, ws, res, energy_values, efficiency_values, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset)
    
    # Add the extra fitting components
    if len(generalVars.extra_fitting_functions) > 0:
        generalVars.yextras.resize((len(generalVars.extra_fitting_functions), len(generalVars.xfinal)))
        for i, key in enumerate(generalVars.extra_fitting_functions):
            function = key.split("_")[1]
            pars = generalVars.extra_fitting_functions[key]
            
            if function == 'Gaussian':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), pars['GwidthParVal'])
            elif function == 'Lorentzian':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), 0.0, pars['LwidthParVal'])
            elif function == 'Voigt':
                generalVars.yextras[i] = add_fitting_components(generalVars.xfinal, function, pars['xParVal'], pars['ampParVal'] * max(generalVars.ytot), pars['GwidthParVal'], pars['LwidthParVal'])
    
    # ---------------------------------------------------------------------------------------------------------------
    # Calculate the normalization multiplyer
    y0 = guiVars.yoffset.get() # type: ignore
    
    if load != 'No':
        normalization_var = normalizer(y0, max(generalVars.exp_y), max(generalVars.ytot))
    else:
        # If we try to normalize without an experimental spectrum
        if guiVars.normalizevar.get() == 'ExpMax': # type: ignore
            messagebox.showwarning("No experimental spectrum is loaded", "Choose different normalization option")
            # Reset the normalizer to the default
            guiVars.normalizevar.set('No') # type: ignore
        normalization_var = normalizer(y0, 1, max(generalVars.ytot))
    
    # ---------------------------------------------------------------------------------------------------------------
    # Autofit:
    number_of_fit_variables = 0
    if guiVars.autofitvar_lmfit.get() == 'Yes': # type: ignore
        # We can only fit if we have an experimental spectrum
        if load != 'No':
            number_of_fit_variables, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, normalization_var, extra_pars = execute_autofit(sim, sat, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, num_of_points, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, time_of_click)
        else:
            messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
    if guiVars.autofitvar_minuit.get() == 'Yes': # type: ignore
        # We can only fit if we have an experimental spectrum
        if load != 'No':
            number_of_fit_variables, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, ytot_max, normalization_var, extra_pars = execute_autofit_minuit(sim, sat, enoffset, sat_enoffset, shkoff_enoffset, shkup_enoffset, y0, res, num_of_points, peak, x, y, w, xs, ys, ws, energy_values, efficiency_values, time_of_click)
        else:
            messagebox.showerror("Error", "Autofit is only avaliable if an experimental spectrum is loaded")
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Plot the selected lines
    graph_area = Msimu_plot(ploted_cs, sat, graph_area, normalization_var, y0) # type: ignore
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Calculate the residues
    if load != 'No':
        calculateResidues(generalVars.exp_x, generalVars.exp_y, generalVars.exp_sigma, generalVars.xfinal, normalization_var, guiVars.normalizevar.get(), y0, number_of_fit_variables, guiVars._residues_graph) # type: ignore
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Set the axis labels
    graph_area.set_ylabel('Intensity (arb. units)')
    graph_area.legend(title=generalVars.element_name, title_fontsize='large')
    if load == 'No':
        graph_area.set_xlabel('Energy (eV)')
    
    # ------------------------------------------------------------------------------------------------------------------------
    # Automatic legend formating
    format_legend(graph_area)
    
    return graph_area



# Profile plotter. Plots each transition, applying the selected profile
def simulate(sim: Toplevel, f: Figure, graph_area: Axes):
    """
    Profile plotter function. Plots each transition, applying the selected profile
        
        Args:
            sim: tkinter simulation window to update the progress bar
            f: matplotlib figure object where to plot the data
            graph_area: matplotlib graph to plot the simulated transitions
            
        Returns:
            Nothing, the simulation is performed, the transitions are plotted and the interface is updated
    """
    # Get the timestamp to use when saving files for this simulation plot
    time_of_click = datetime.now()
    """
    Timestamp to use when saving files for this simulation plot
    """
    
    generalVars.exp_x = None
    """
    List of experimental spectrum energies
    """
    generalVars.exp_y = None
    """
    List of experimental spectrum intensities
    """
    
    # Reset the plot with the configurations selected
    graph_area.clear()
    if guiVars.yscale_log.get() == 'Ylog': # type: ignore
        graph_area.set_yscale('log')
    if guiVars.xscale_log.get() == 'Xlog': # type: ignore
        graph_area.set_xscale('log')
    
    graph_area.legend(title=generalVars.element_name)
    
    number_of_fit_variables = 0
    
    spectype = guiVars.choice_var.get() # type: ignore
    
    if generalVars.meanR_exists:
        setupMRBEB()
    if generalVars.ELAM_exists:
        setupELAMPhotoIoniz()

    setupShake()
    
    setupFormationEnergies()
    setupPartialWidths()
    
    # --------------------------------------------------------------------------------------------------------------------------
    if spectype == 'Stick':
        graph_area = make_stick(sim, graph_area)
    # --------------------------------------------------------------------------------------------------------------------------
    elif spectype == 'M_Stick':
        graph_area = make_Mstick(sim, graph_area)
    # --------------------------------------------------------------------------------------------------------------------------
    elif spectype == 'Simulation':
        graph_area = make_simulation(sim, f, graph_area, time_of_click)
        # CODE FOR AUTOMATIC BEAM ENERGY INCREMENTATION
        import numpy as np
        #for energ in np.linspace(8970, 10500, 5100, endpoint=True):
        #for energ in np.linspace(9955, 10045, 300, endpoint=True):
        # for energ in [9950, 10050, 10200, 10300, 10400, 10500, 18000, 20000]:
           #guiVars.excitation_energy.set(energ) # type: ignore
        #graph_area = make_simulation(sim, f, graph_area, time_of_click, False)
    # --------------------------------------------------------------------------------------------------------------------------------------
    elif spectype == 'M_Simulation':
        graph_area = make_Msimulation(sim, f, graph_area, time_of_click)
    
    f.canvas.draw()

