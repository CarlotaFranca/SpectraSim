"""
Module to calculate the values necessary to take into account both shake-off and shake-up processes probabilities.
"""

import data.variables as generalVars
import interface.variables as guiVars

from data.definitions import Line

from scipy.interpolate import interp1d

from typing import List


# Variable to store the realtionships between shake probabilities for each shell
# This is used to manintain the relationships during the shake fitting algorithm
shake_relations = {}
"""
Variable to store the realtionships between shake probabilities for each shell.
This is used to manintain the relationships during the shake fitting algorithm
"""

# Variable to hold the existing shakeups in the spectrum
existing_shakeups = {}
"""
Variable to hold the existing shakeups in the spectrum
"""
# Variable to hold the existing shakeoffs in the spectrum
existing_shakeoffs = {}
"""
Variable to hold the existing shakeoffs in the spectrum
"""

# --------------------------------------------------------- #
#                                                           #
#        FUNCTIONS TO HANDLE THE SHAKE PROBABILITIES        #
#                                                           #
# --------------------------------------------------------- #


def setupShake():
    """
    Function to setup the shake-up spline interpolations to calculate the probability, even if we don't have the specific excitation.
    """
    global existing_shakeoffs, existing_shakeups, shake_relations
    
    if generalVars.Shakeup_exists:
        shakeValues = {}
        shakeOrbitals = {}
        
        for shake in generalVars.shakeup:
            if shake[2] != 'SUM':
                if shake[1] + '_' + shake[3] in shakeValues and shake[1] + '_' + shake[3] in shakeOrbitals:
                    shakeValues[shake[1] + '_' + shake[3]].append(float(shake[4]))
                    shakeOrbitals[shake[1] + '_' + shake[3]].append(int(shake[2][:-1]))
                else:
                    shakeValues[shake[1] + '_' + shake[3]] = [float(shake[4])]
                    shakeOrbitals[shake[1] + '_' + shake[3]] = [int(shake[2][:-1])]
        
        for key in shakeValues:
            generalVars.shakeUPSplines[key] = interp1d(shakeOrbitals[key], shakeValues[key])
        
        
        # Setup the missing shake-up probabilities
        
        existing_shakeups = dict.fromkeys([row.Shelli[2:4] + "_" + str(row.jji) for row in generalVars.lineshakeup], 0.0)
        found_excitations = {}
        
        for row in generalVars.lineshakeup:
            key = row.Shelli[2:4]
            if key + "_" + str(row.jji) not in found_excitations:
                found_excitations[key + "_" + str(row.jji)] = []
            
            if row.Shelli[4:-1] not in found_excitations[key + "_" + str(row.jji)]:
                existing_shakeups[key + "_" + str(row.jji)] += get_shakeup(key, row.Shelli[4:], row.jji)
                found_excitations[key + "_" + str(row.jji)].append(row.Shelli[4:-1])
        
        shakeup_sums = {}
        
        for shake in generalVars.shakeup:
            key = shake[1]
            if shake[2] == 'SUM':
                shakeup_sums[key + "_" + shake[3]] = float(shake[4])
        
        for key in existing_shakeups:
            generalVars.missing_shakeup[key] = (shakeup_sums[key] - existing_shakeups[key]) / len(found_excitations[key])
        
        # Setup shakeup relations
        
        for shake1 in generalVars.shakeup:
            shake_relations[shake1[1] + "_" + shake1[3]] = {}
            for shake2 in generalVars.shakeup:
                if shake1 != shake2:
                    shake_relations[shake1[1] + "_" + shake1[3]][shake2[1] + "_" + shake2[3]] = \
                            ">" if float(shake1[4]) > float(shake2[4]) else "<="
        
        # print(existing_shakeups)
        # print(generalVars.missing_shakeup)
    
    # Setup the missing shake-off probabilities
    
    existing_shakeoffs = {}
    
    for row in generalVars.linesatellites:
        key = row.Shelli[2:4]
        if key not in existing_shakeoffs:
            existing_shakeoffs[key] = get_shakeoff(key)
    
    missing_shakeoff = {}
    for shake in generalVars.shakeoff:
        key = shake[1]
        if key not in existing_shakeoffs:
            missing_shakeoff[key + "_" + shake[2]] = float(shake[3])
    
    missing_shake = 0.0
    missing_shake_key = dict.fromkeys(generalVars.label1, 0.0)
    missing_shake_key_jjs = dict.fromkeys(generalVars.label1, 0)
    for key_ms in missing_shakeoff:
        missing_shake_key[key_ms.split("_")[0]] += missing_shakeoff[key_ms] * (int(key_ms.split("_")[1]) + 1)
        missing_shake_key_jjs[key_ms.split("_")[0]] += int(key_ms.split("_")[1]) + 1
    
    for key_ms in missing_shake_key:
        missing_shake += (missing_shake_key[key_ms] / missing_shake_key_jjs[key_ms]) if missing_shake_key[key_ms] > 0.0 else 0.0
    
    missing_shake /= (len(generalVars.label1) - (len(missing_shakeoff) / 2))
    generalVars.missing_shakeoff = missing_shake
    
    
    # Setup shakeoff relations
    
    for shake1 in generalVars.shakeoff:
        shake_relations[shake1[1]] = {}
        for shake2 in generalVars.shakeoff:
            if shake1 != shake2:
                shake_relations[shake1[1]][shake2[1]] = \
                        ">" if float(shake1[3]) > float(shake2[3]) else "<="

    
    

# Calculate the total shake probability from shake-up and shake-off probabilities
def calculateTotalShake(JJ2: int, shake_amps: dict = {}) -> float:
    """
    Function to calculate the total shake probabilities for a transition with an initial level with 2J of JJ2
    
        Args:
            JJ2: 2*J value of the transition for which we want the total shake probability
        
        Returns:
            sum of the total shake-up + shake-off probabilities to modify the population of an initial level with 2*J value of JJ2
    """
    if len(generalVars.shakeup) > 0 and len(generalVars.shakeup[0]) > 1:
        totalShakeup = sum([float(shake[4]) * \
                            (shake_amps['shakeup_amps_' + shake[1]] if 'shakeup_amps_' + shake[1] in shake_amps else 1.0) \
                            for shake in generalVars.shakeup if int(shake[3]) == JJ2 and shake[2] == 'SUM'])
    else:
        totalShakeup = 0.0
    
    return sum([float(shake[3]) * \
                (shake_amps['shake_amps_' + shake[1]] if 'shake_amps_' + shake[1] in shake_amps else 1.0) \
                for shake in generalVars.shakeoff if int(shake[2]) == JJ2]) + \
            totalShakeup

# Calculate the average total shake probability for all 2J ground state values
def calculateAvgTotalShake(shake_amps: dict = {}) -> float:
    """
    Function to calculate the average shake probabilities for all 2J values
    
        Args:
            shake_amps: parameters to multiply the shake probabilities during fitting
        
        Returns:
            average of the total shake-up + shake-off probabilities to modify the population of an initial level with 2*J value of JJ2
    """
    if len(generalVars.shakeup) > 0 and len(generalVars.shakeup[0]) > 1:
        avgShakeup = sum([float(shake[4]) * \
                            (shake_amps['shakeup_amps_' + shake[1]] if 'shakeup_amps_' + shake[1] in shake_amps else 1.0) \
                            for shake in generalVars.shakeup if shake[2] == 'SUM']) / \
                        sum(list(set([int(shake[3]) + 1 for shake in generalVars.shakeup])))
    else:
        avgShakeup = 0.0
    
    return (sum([float(shake[3]) * \
                (shake_amps['shake_amps_' + shake[1]] if 'shake_amps_' + shake[1] in shake_amps else 1.0) \
                for shake in generalVars.shakeoff]) / \
            sum(list(set([int(shake[2]) + 1 for shake in generalVars.shakeoff])))) + \
            avgShakeup


# Search for the shake-off probability for the shake electron key
def get_shakeoff(key: str):
    """
    Function to search for the shake-off probability for a shake electron from the orbital key
    
        Args:
            key: electron shake-off orbital label
        
        Returns:
            shake-off probability for the requested level
    """
    probs = []
    for shake in generalVars.shakeoff:
        if shake[1] == key:
            probs.append(shake)
    
    total_shakeoff = sum([float(prob[3]) * (int(prob[2]) + 1) for prob in probs]) / sum([(int(prob[2]) + 1) for prob in probs])
    
    return total_shakeoff + generalVars.missing_shakeoff


# Search for the shake-up probability for the shake electron key and 2*J value JJ2
def get_shakeup(key: str, shakeF: str, JJ2: int) -> float:
    """
    Function to search for the shake-up probability for a shake electron from the orbital key with an initial level with 2JJ of JJ2
    
        Args:
            key: electron shake-up orbital label
            JJ2: 2*J value of the transition for which we want the shake-up probability
        
        Returns:
            shake-up probability for the requested level
    """
    if key + '_' + str(JJ2) not in generalVars.shakeUPSplines:
        return 0.0
    
    if key + '_' + str(JJ2) not in generalVars.missing_shakeup:
        try:
            return generalVars.shakeUPSplines[key + '_' + str(JJ2)](int(shakeF[:-1]))
        except ValueError:
            # print("Warning: Out of bounds excitation orbital in shake-up probability calculation!")
            return 0.0
    else:
        try:
            return generalVars.shakeUPSplines[key + '_' + str(JJ2)](int(shakeF[:-1])) + generalVars.missing_shakeup[key + "_" + str(JJ2)]
        except ValueError:
            # print("Warning: Out of bounds excitation orbital in shake-up probability calculation!")
            return 0.0


# Search for the 2j values possible for the selected transitions in the transition_list
def jj_search(transition_list: List[str]):
    """
    Function to search for the 2j values possible for the selected transitions in the transition_list
        
        Args:
            transition_list: transitions names list to search for
        
        Returns:
            jj_vals: list of 2j values possible for the selected transitions
    """
    spectype = guiVars.choice_var.get() # type: ignore
    sat = guiVars.satelite_var.get() # type: ignore
    
    jj_vals: List[int] = []
    
    if spectype == 'Simulation' or spectype == 'Stick':
        if sat != 'Auger':
            lines_to_search = generalVars.lineradrates
            
            for transition in transition_list:
                low_level: str = generalVars.the_dictionary[transition]["low_level"] # type: ignore
                high_level: str = generalVars.the_dictionary[transition]["high_level"] # type: ignore
                
                jj_vals += [line.jji for line in lines_to_search if line.filterLevel(low_level, high_level, strict='na')]
            
            if 'Satellites' in sat:
                lines_to_search = generalVars.linesatellites
                for transition in transition_list:
                    low_level: str = generalVars.the_dictionary[transition]["low_level"] # type: ignore
                    high_level: str = generalVars.the_dictionary[transition]["high_level"] # type: ignore
                    
                    jj_vals += [line.jji for line in lines_to_search if line.filterLevel(low_level, high_level, strict='na')]
            
        else:
            lines_to_search = generalVars.lineauger
            
            for transition in transition_list:
                low_level: str = generalVars.the_aug_dictionary[transition]["low_level"] # type: ignore
                high_level: str = generalVars.the_aug_dictionary[transition]["high_level"] # type: ignore
            
                jj_vals += [line.jji for line in lines_to_search if line.filterLevel(low_level, high_level, strict='na')]
    else:
        if sat != 'Auger':
            lines_to_search_PCS = generalVars.lineradrates_PCS
            lines_to_search_NCS = generalVars.lineradrates_NCS
            
            # Initialize the charge states we have to loop through
            charge_states = generalVars.rad_PCS + generalVars.rad_NCS

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
                if cs_index < len(generalVars.rad_PCS):
                    mix_val = guiVars.PCS_radMixValues[cs_index].get()
                else:
                    mix_val = guiVars.NCS_radMixValues[cs_index - len(generalVars.rad_PCS)].get()
                    ncs = True

                # Check if the mix value is not 0, otherwise no need to plot the transitions for this charge state
                if mix_val != '0.0':
                    ploted_cs.append(cs)
                    cs_type.append(ncs)

            
            # Loop the charge states to plot
            for cs_index, cs in enumerate(ploted_cs):
                # -------------------------------------------------------------------------------------------
                # Read the selected transitions
                # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
                for transition in transition_list:
                    low_level: str = generalVars.the_dictionary[transition]["low_level"] # type: ignore
                    high_level: str = generalVars.the_dictionary[transition]["high_level"] # type: ignore
                    
                    if not cs_type[cs_index]:
                        jj_vals += [line.jji for i, lines in enumerate(lines_to_search_PCS) for line in lines if line.filterLevel(low_level, high_level, strict='na') and generalVars.rad_PCS[i] == cs]
                    else:
                        jj_vals += [line.jji for i, lines in enumerate(lines_to_search_NCS) for line in lines if line.filterLevel(low_level, high_level, strict='na') and generalVars.rad_NCS[i] == cs]
            
            if 'Satellites' in sat:
                lines_to_search_PCS = generalVars.linesatellites_PCS
                lines_to_search_NCS = generalVars.linesatellites_NCS
                
                # Loop the charge states to plot
                for cs_index, cs in enumerate(ploted_cs):
                    # -------------------------------------------------------------------------------------------
                    # Read the selected transitions
                    # In this case we first store all the values for the transitions and then we calculate the y values to be plotted according to a profile
                    for transition in transition_list:
                        low_level: str = generalVars.the_dictionary[transition]["low_level"] # type: ignore
                        high_level: str = generalVars.the_dictionary[transition]["high_level"] # type: ignore
                        
                        if not cs_type[cs_index]:
                            jj_vals += [line.jji for i, lines in enumerate(lines_to_search_PCS) for line in lines if line.filterLevel(low_level, high_level, strict='na') and generalVars.rad_PCS[i] == cs]
                        else:
                            jj_vals += [line.jji for i, lines in enumerate(lines_to_search_NCS) for line in lines if line.filterLevel(low_level, high_level, strict='na') and generalVars.rad_NCS[i] == cs]
        else:
            lines_to_search_PCS = generalVars.lineaugrates_PCS
            lines_to_search_NCS = generalVars.lineaugrates_NCS
            
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

            # Loop the charge states to plot
            for cs_index, cs in enumerate(ploted_cs):
                # Loop the possible auger transitions
                for transition in transition_list:
                    low_level: str = generalVars.the_aug_dictionary[transition]["low_level"] # type: ignore
                    high_level: str = generalVars.the_aug_dictionary[transition]["high_level"] # type: ignore
                    
                    if not cs_type[cs_index]:
                        jj_vals += [line.jji for i, lines in enumerate(lines_to_search_PCS) for line in lines if line.filterLevel(low_level, high_level, strict='na') and generalVars.aug_PCS[i] == cs]
                    else:
                        jj_vals += [line.jji for i, lines in enumerate(lines_to_search_NCS) for line in lines if line.filterLevel(low_level, high_level, strict='na') and generalVars.aug_PCS[i] == cs]
        
    jj_vals = list(set(jj_vals))
    jj_vals.sort()
    
    return jj_vals


def avgDiagramOverlap(diagram_source: List[Line], beam: float, FWHM: float):
    """Function to calculate the average diagram overlap with the beam for a set of diagram lines.
    This is used to scale/modulate the formation rate of shake transitions with the diagram overlap

    Args:
        diagram_source (List[Line]): list of the diagram lines to use
        beam (float): beam energy to consider in the total intensity calculation
        FWHM (float): beam FWHM to consider in the total intensity calculation

    Returns:
        float: average diagram overlap
    """
    from simulation.mults import get_overlap
    
    if len(diagram_source) == 0:
        return 0.0
    
    return sum([get_overlap(line, beam, FWHM) for line in diagram_source]) / len(diagram_source)