"""
Module with functions to update the line list that needs to be simulated into the spectra.
"""

import data.variables as generalVars

import interface.variables as guiVars

from simulation.shake import avgDiagramOverlap

from data.definitions import Line

from typing import List


# --------------------------------------------------------- #
#                                                           #
#      FUNCTIONS TO UPDATE THE TRANSITIONS TO SIMULATE      #
#                                                           #
# --------------------------------------------------------- #


# Update the radiative and satellite rates for the selected transition
def updateRadTransitionVals(transition: str, num: int, beam: float, FWHM: float):
    """
    Function to update the radiative and satellite rates for the selected transition
        
        Args:
            transition: which transition to fetch the rates of
            num: total number of transitions processed
            beam: beam energy user value from the interface
        
        Returns:
            num_of_transitions: total number of transitions processed
            low_level: low level of the selected transition
            high_level: high level of the selected transition
            diag_stick_val: rates data for the selected transition
            sat_stick_val: rates data for the possible satellite transitions for the selected transition
    """
    # Update the number of transitions loaded (this could be done by reference as well)
    num_of_transitions = num + 1
    # Get the low and high levels for the selected transition
    low_level: str = generalVars.the_dictionary[transition]["low_level"] # type: ignore
    high_level: str = generalVars.the_dictionary[transition]["high_level"] # type: ignore
    
    if len(generalVars.jj_vals) == 0:
        # Filter the radiative and satellite rates data for the selected transition
        diag_stick_val = [line for line in generalVars.lineradrates if line.filterLevel(low_level, high_level, strict='h')]
        avgDOverlap = avgDiagramOverlap(diag_stick_val, beam, FWHM)
        
        sat_stick_val = [line.setDiagramOverlap(avgDOverlap) for line in generalVars.linesatellites if line.filterLevel(low_level, high_level, strict='na')]
        
        # Filter the shake-up satellite rates data for the selected transition
        if generalVars.Shakeup_exists:
            sat_stick_val += [line.setDiagramOverlap(avgDOverlap) for line in generalVars.lineshakeup if line.filterLevel(low_level, high_level, strict='na')]
        
    else:
        # Filter the radiative and satellite rates data for the selected transition
        diag_stick_val = [line for line in generalVars.lineradrates if line.filterLevel(low_level, high_level, strict='h') and line.filterJJI()]
        avgDOverlap = avgDiagramOverlap(diag_stick_val, beam, FWHM)
        
        sat_stick_val = [line.setDiagramOverlap(avgDOverlap) for line in generalVars.linesatellites if line.filterLevel(low_level, high_level, strict='na') and line.filterJJI()]
        
        # Filter the shake-up satellite rates data for the selected transition
        if generalVars.Shakeup_exists:
            sat_stick_val += [line.setDiagramOverlap(avgDOverlap) for line in generalVars.lineshakeup if line.filterLevel(low_level, high_level, strict='na') and line.filterJJI()]
        
    return num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val

# Update the satellite rates for the selected transition
def updateSatTransitionVals(low_level: str, high_level: str, key: str, sat_stick_val: List[Line], free: bool = False):
    """
    Function to update the satellite rates for the selected transition and shake level
        
        Args:
            low_level: low level of the selected transition
            high_level: high level of the selected transition
            key: shake level of the satellite transition
            sat_stick_val: list with all the possible satellite transitions for the current diagram transition
            beam: beam energy user value from the interface
        
        Returns:
            sat_stick_val_ind: list with the satellite rates for the selected diagram transition and shake level
    """
    if not free:
        # Filter the satellite rates data for the combinations of selected levels
        sat_stick_val_ind1 = [line for line in sat_stick_val if line.filterLevel(low_level + key, key + high_level, strict='na')]
        sat_stick_val_ind2 = [line for line in sat_stick_val if line.filterLevel(low_level + key, high_level + key, strict='na')]
        sat_stick_val_ind3 = [line for line in sat_stick_val if line.filterLevel(key + low_level, key + high_level, strict='na')]
        sat_stick_val_ind4 = [line for line in sat_stick_val if line.filterLevel(key + low_level, high_level + key, strict='na')]
    else:
        # Filter the satellite rates data for the combinations of selected levels
        sat_stick_val_ind1 = [line for line in sat_stick_val if low_level + key in line.Shelli]
        sat_stick_val_ind2 = [line for line in sat_stick_val if low_level + key in line.Shelli]
        sat_stick_val_ind3 = [line for line in sat_stick_val if key + low_level in line.Shelli]
        sat_stick_val_ind4 = [line for line in sat_stick_val if key + low_level in line.Shelli]
    
    sat_stick_val_ind = sat_stick_val_ind1 + sat_stick_val_ind2 + sat_stick_val_ind3 + sat_stick_val_ind4
    
    return sat_stick_val_ind

# Update the auger rates for the selected transition
def updateAugTransitionVals(transition: str, num: int):
    """
    Function to update the auger rates for the selected transition
        
        Args:
            transition: which transition to fetch the rates of
            num: total number of transitions processed
            beam: beam energy user value from the interface
        
        Returns:
            num_of_transitions: total number of transitions processed
            aug_stick_val: rates data for the selected transition
    """
    # Update the number of transitions loaded (this could be done by reference as well)
    num_of_transitions = num + 1
    # Get the low, high and auger levels for the selected transition
    low_level: str = the_aug_dictionary[transition]["low_level"] # type: ignore
    high_level: str = the_aug_dictionary[transition]["high_level"] # type: ignore
    auger_level: str = the_aug_dictionary[transition]["auger_level"] # type: ignore

    if len(generalVars.jj_vals) == 0:
        # Filter the auger rates data for the selected transition
        aug_stick_val = [line for line in generalVars.lineauger if line.filterLevel(low_level, high_level, auger_level, strict='na')]
    else:
        # Filter the auger rates data for the selected transition
        aug_stick_val = [line for line in generalVars.lineauger if line.filterLevel(low_level, high_level, auger_level, strict='na') and line.filterJJI()]

    return num_of_transitions, aug_stick_val

# Update the radiative and satellite rates for the selected transition and charge state
def updateRadCSTrantitionsVals(transition: str, num: int, ncs: bool, cs: str):
    """
    Function to update the radiative and satellite rates for the selected transition and charge state
        
        Args:
            transition: which transition to fetch the rates of
            num: total number of transitions processed
            ncs: boolean selecting if this is a negative charge state or not
            cs: value of the charge state
            beam: beam energy user value from the interface
        
        Returns:
            num_of_transitions: total number of transitions processed
            low_level: low level of the selected transition and charge state
            high_level: high level of the selected transition and charge state
            diag_stick_val: rates data for the selected transition and charge state
            sat_stick_val: rates data for the possible satellite transitions for the selected transition and charge state
    """
    # Update the number of transitions loaded (this could be done by reference as well)
    num_of_transitions = num + 1
    # Get the low and high levels for the selected transition
    low_level: str = generalVars.the_dictionary[transition]["low_level"] # type: ignore
    high_level: str = generalVars.the_dictionary[transition]["high_level"] # type: ignore
    
    if len(generalVars.jj_vals) == 0:
        # Filter the radiative and satellite rates data for the selected transition and charge state
        if not ncs:
            diag_stick_val = [line.setMixValue(float(guiVars.PCS_radMixValues[i].get())) for i, linerad in enumerate(generalVars.lineradrates_PCS) for line in linerad if line.filterLevel(low_level, high_level, strict='h') and generalVars.rad_PCS[i] == cs]
        else:
            diag_stick_val = [line.setMixValue(float(guiVars.NCS_radMixValues[i].get())) for i, linerad in enumerate(generalVars.lineradrates_NCS) for line in linerad if line.filterLevel(low_level, high_level, strict='h') and generalVars.rad_NCS[i] == cs]

        if not ncs:
            sat_stick_val = [line.setMixValue(float(guiVars.PCS_radMixValues[generalVars.rad_PCS.index(cs)].get())) for i, linesat in enumerate(generalVars.linesatellites_PCS) for line in linesat if line.filterLevel(low_level, high_level, strict='na') and generalVars.sat_PCS[i] == cs]
        else:
            sat_stick_val = [line.setMixValue(float(guiVars.NCS_radMixValues[generalVars.rad_NCS.index(cs)].get())) for i, linesat in enumerate(generalVars.linesatellites_NCS) for line in linesat if line.filterLevel(low_level, high_level, strict='na') and generalVars.sat_NCS[i] == cs]
    else:
        # Filter the radiative and satellite rates data for the selected transition and charge state
        if not ncs:
            diag_stick_val = [line.setMixValue(float(guiVars.PCS_radMixValues[i].get())) for i, linerad in enumerate(generalVars.lineradrates_PCS) for line in linerad if line.filterLevel(low_level, high_level, strict='h') and generalVars.rad_PCS[i] == cs and line.filterJJI()]
        else:
            diag_stick_val = [line.setMixValue(float(guiVars.NCS_radMixValues[i].get())) for i, linerad in enumerate(generalVars.lineradrates_NCS) for line in linerad if line.filterLevel(low_level, high_level, strict='h') and generalVars.rad_NCS[i] == cs and line.filterJJI()]

        if not ncs:
            sat_stick_val = [line.setMixValue(float(guiVars.PCS_radMixValues[generalVars.rad_PCS.index(cs)].get())) for i, linesat in enumerate(generalVars.linesatellites_PCS) for line in linesat if line.filterLevel(low_level, high_level, strict='na') and generalVars.sat_PCS[i] == cs and line.filterJJI()]
        else:
            sat_stick_val = [line.setMixValue(float(guiVars.NCS_radMixValues[generalVars.rad_NCS.index(cs)].get())) for i, linesat in enumerate(generalVars.linesatellites_NCS) for line in linesat if line.filterLevel(low_level, high_level, strict='na') and generalVars.sat_NCS[i] == cs and line.filterJJI()]
        
    return num_of_transitions, low_level, high_level, diag_stick_val, sat_stick_val

# Update the auger rates for the selected transition and charge state
def updateAugCSTransitionsVals(transition: str, num: int, ncs: bool, cs: str):
    """
    Function to update the auger rates for the selected transition and charge state
        
        Args:
            transition: which transition to fetch the rates of
            num: total number of transitions processed
            ncs: boolean selecting if this is a negative charge state or not
            cs: value of the charge state
            beam: beam energy user value from the interface
        
        Returns:
            num_of_transitions: total number of transitions processed
            aug_stick_val: rates data for the selected transition and charge state
    """
    # Update the number of transitions loaded (this could be done by reference as well)
    num_of_transitions = num + 1
    # Get the low, high and auger levels for the selected transition
    low_level: str = the_aug_dictionary[transition]["low_level"] # type: ignore
    high_level: str = the_aug_dictionary[transition]["high_level"] # type: ignore
    auger_level: str = the_aug_dictionary[transition]["auger_level"] # type: ignore
    
    if len(generalVars.jj_vals) == 0:
        # Filter the auger rates data for the selected transition and charge state
        if not ncs:
            aug_stick_val = [line.setMixValue(float(guiVars.PCS_augMixValues[i].get())) for i, lineaug in enumerate(generalVars.lineaugrates_PCS) for line in lineaug if line.filterLevel(low_level, high_level, auger_level, strict='na') and generalVars.aug_PCS[i] == cs]
        else:
            aug_stick_val = [line.setMixValue(float(guiVars.NCS_augMixValues[i].get())) for i, lineaug in enumerate(generalVars.lineaugrates_NCS) for line in lineaug if line.filterLevel(low_level, high_level, auger_level, strict='na') and generalVars.aug_PCS[i] == cs]
    else:
        # Filter the auger rates data for the selected transition and charge state
        if not ncs:
            aug_stick_val = [line.setMixValue(float(guiVars.PCS_augMixValues[i].get())) for i, lineaug in enumerate(generalVars.lineaugrates_PCS) for line in lineaug if line.filterLevel(low_level, high_level, auger_level, strict='na') and generalVars.aug_PCS[i] == cs and line.filterJJI()]
        else:
            aug_stick_val = [line.setMixValue(float(guiVars.NCS_augMixValues[i].get())) for i, lineaug in enumerate(generalVars.lineaugrates_NCS) for line in lineaug if line.filterLevel(low_level, high_level, auger_level, strict='na') and generalVars.aug_PCS[i] == cs and line.filterJJI()]

    return num_of_transitions, aug_stick_val
