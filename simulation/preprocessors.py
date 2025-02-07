import interface.variables as guiVars
import data.variables as generalVars

from simulation.diagram import simu_diagram
from simulation.auger import simu_auger
from simulation.satellite import simu_sattelite

from simulation.initializers import initialize_XYW

from simulation.lineUpdater import updateRadTransitionVals, updateAugTransitionVals,\
                                    updateRadCSTrantitionsVals, updateAugCSTransitionsVals

from utils.misc.badReporters import simu_check_bads, Msimu_check_bads, report_MbadSelection

from typing import List


def process_simulation(shake_amps: dict = {}, prompt: bool = True):
    sat: str = guiVars.satelite_var.get() # type: ignore
    beam: float = guiVars.excitation_energy.get() # type: ignore
    FWHM: float = guiVars.excitation_energyFWHM.get() # type: ignore
    
    # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
    if sat != 'Auger':
        # Initialize the x, y and w arrays for both the non satellites and satellites (xs, ys, ws) transitions
        x, y, w, xs, ys, ws = initialize_XYW('Radiative')
        
        # Read the selected transitions
        # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
        for index, transition in enumerate(generalVars.the_dictionary):
            if generalVars.the_dictionary[transition]["selected_state"]:
                # Same filter as the sticks but we dont keep track of the number of selected transitions
                _, low_level, high_level, diag_sim_val, sat_sim_val = updateRadTransitionVals(transition, 0, beam, FWHM)
                
                if 'Diagram' in sat:
                    # Store the values in a list containing all the transitions to simulate
                    x[index], y[index], w[index] = simu_diagram(diag_sim_val, beam, FWHM, shake_amps)
                if 'Satellites' in sat:
                    # Store the values in a list containing all the transitions to simulate
                    xs[index], ys[index], ws[index] = simu_sattelite(sat_sim_val, low_level, high_level, beam, FWHM, shake_amps)
        
        # -------------------------------------------------------------------------------------------
        # Check if there are any transitions with missing rates
        bad_selection, bads = simu_check_bads(x, xs, True, prompt)
        for index in bads:
            x[index] = []
        
    else:
        # Initialize the x, y and w arrays for both the non satellites and satellites (xs, ys, ws) transitions
        x, y, w, xs, ys, ws = initialize_XYW('Auger')
        
        # Loop possible auger transitions
        for index, transition in enumerate(generalVars.the_aug_dictionary):
            if generalVars.the_aug_dictionary[transition]["selected_state"]:
                # Same as the stick but we dont care about the number of transitions
                _, aug_stick_val = updateAugTransitionVals(transition, 0)
                
                # Store the values in a list containing all the transitions to simulate
                x[index], y[index], w[index] = simu_auger(aug_stick_val, beam, FWHM, shake_amps)

        # -------------------------------------------------------------------------------------------
        # Check if there are any transitions with missing rates
        bad_selection, bads = simu_check_bads(x, xs, False, prompt)
        for index in bads:
            x[index] = []
    
    return x, y, w, xs, ys, ws, bad_selection




def process_Msimulation(shake_amps: dict = {}, prompt: bool = True):
    sat = guiVars.satelite_var.get() # type: ignore  ## saber que tipo de transição 
    beam = guiVars.excitation_energy.get() # type: ignore  ## Variável para manter o valor da energia de excitação/feixe introduzida pelo utilizador na interface
    FWHM = guiVars.excitation_energyFWHM.get() # type: ignore  ##Variável para manter o valor da energia de excitação/feixe FWHM introduzida pelo utilizador na interface  (largura total a meia altura)
    
    bad_selection = 0
    
    # Radiative and Auger code has to be split due to the different dictionaries used for the transitions
    if sat != 'Auger':
        # Initialize the charge states we have to loop through
        charge_states: List[str] = generalVars.rad_PCS + generalVars.rad_NCS

        # Before plotting we filter the charge state that need to be plotted (mix_val != 0)
        # And store the charge state values in this list
        ploted_cs: List[str] = []
        # Also store if the charge state is positive or negative
        cs_type: List[bool] = []

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
                ploted_cs.append(cs)
                cs_type.append(ncs)

        # Initialize the x, y and w arrays, taking into account the number of charge states to plot, for both the non satellites and satellites (xs, ys, ws) transitions
        x, y, w, xs, ys, ws = initialize_XYW('Radiative_CS', ploted_cs)


        bad_lines = {}
        
        # Loop the charge states to plot
        for cs_index, cs in enumerate(ploted_cs):
            # -------------------------------------------------------------------------------------------
            # Read the selected transitions
            # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
            for index, transition in enumerate(generalVars.the_dictionary):
                if generalVars.the_dictionary[transition]["selected_state"]:
                    # Same as sticks but we dont care about the number of transitions
                    _, low_level, high_level, diag_sim_val, sat_sim_val = updateRadCSTrantitionsVals(transition, 0, cs_type[cs_index], cs)
                    
                    if 'Diagram' in sat:
                        # Store the values in a list containing all the transitions and charge states to simulate
                        x[cs_index * len(generalVars.the_dictionary) + index], y[cs_index * len(generalVars.the_dictionary) + index], w[cs_index * len(generalVars.the_dictionary) + index] = simu_diagram(diag_sim_val, beam, FWHM, shake_amps)
                    if 'Satellites' in sat:
                        # Store the values in a list containing all the charge states and transitions to simulate
                        xs[cs_index * len(generalVars.the_dictionary) + index], ys[cs_index * len(generalVars.the_dictionary) + index], ws[cs_index * len(generalVars.the_dictionary) + index] = simu_sattelite(sat_sim_val, low_level, high_level, beam, FWHM, shake_amps)

            # -------------------------------------------------------------------------------------------
            # Check if there are any transitions with missing rates
            bad_selection, bad_lines = Msimu_check_bads(cs_index, cs, x, xs, True)
        
        if prompt:
            report_MbadSelection(bad_lines, ploted_cs)
    else:
        # Initialize the charge states we have to loop through
        charge_states = generalVars.aug_PCS + generalVars.aug_NCS

        # Before plotting we filter the charge state that need to be plotted (mix_val != 0)
        # And store the charge state values in this list
        ploted_cs = []
        # Also store if the charge state is positive or negative
        cs_type = []

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
                ploted_cs.append(cs)
                cs_type.append(ncs)

        # Initialize the x, y and w arrays, taking into account the number of charge states to plot, for both the non satellites and satellites (xs, ys, ws) transitions
        x, y, w, xs, ys, ws = initialize_XYW('Auger_CS', ploted_cs)
        
        bad_lines = {}
        
        # Loop the charge states to plot
        for cs_index, cs in enumerate(ploted_cs):
            # Loop the possible auger transitions
            for index, transition in enumerate(generalVars.the_aug_dictionary):
                if generalVars.the_aug_dictionary[transition]["selected_state"]:
                    # Same as stick but we dont care about the number of transitions
                    _, aug_sim_val = updateAugCSTransitionsVals(transition, 0, cs_type[cs_index], cs)
                    
                    # Store the values in a list containing all the transitions to simulate
                    x[cs_index * len(generalVars.the_aug_dictionary) + index], y[cs_index * len(generalVars.the_aug_dictionary) + index], w[cs_index * len(generalVars.the_aug_dictionary) + index] = simu_auger(aug_sim_val, beam, FWHM, shake_amps)

            # -------------------------------------------------------------------------------------------
            # Check if there are any transitions with missing rates
            bad_selection, bad_lines = Msimu_check_bads(cs_index, cs, x, xs, False)
        
        if prompt:
            report_MbadSelection(bad_lines, ploted_cs)
    
    
    return x, y, w, xs, ys, ws, bad_selection