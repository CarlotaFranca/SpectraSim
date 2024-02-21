"""
Module with functions to initialize helper variables to optimize the line filtering and intensity calculation
"""

import data.variables as generalVars


def setupFormationEnergies():
    if type(generalVars.ionizationsrad) != type(None):
        generalVars.formationEnergies['diagram'] = {}
        generalVars.formationEnergies['auger'] = {}
        for level in generalVars.ionizationsrad:
            generalVars.formationEnergies['diagram'][level.keyI()] = level.gEnergy
            generalVars.formationEnergies['auger'][level.keyI()] = level.gEnergy
    
    if type(generalVars.ionizationssat) != type(None):
        generalVars.formationEnergies['satellite'] = {}
        for level in generalVars.ionizationssat:
            generalVars.formationEnergies['satellite'][level.keyI()] = level.gEnergy
    
    if type(generalVars.ionizationsshakeup) != type(None):
        generalVars.formationEnergies['shakeup'] = {}
        for level in generalVars.ionizationsshakeup:
            generalVars.formationEnergies['shakeup'][level.keyI()] = level.gEnergy


def setupPartialWidths():
    if type(generalVars.ionizationsrad) != type(None):
        generalVars.partialWidths['diagram'] = {}
        generalVars.partialWidths['auger'] = {}
        for level in generalVars.ionizationsrad:
            generalVars.partialWidths['diagram'][level.keyI()] = level.totalWidth
            generalVars.partialWidths['auger'][level.keyI()] = level.totalWidth
    
    if type(generalVars.ionizationssat) != type(None):
        generalVars.partialWidths['satellite'] = {}
        for level in generalVars.ionizationssat:
            generalVars.partialWidths['satellite'][level.keyI()] = level.totalWidth
    
    if type(generalVars.ionizationsshakeup) != type(None):
        generalVars.partialWidths['shakeup'] = {}
        for level in generalVars.ionizationsshakeup:
            generalVars.partialWidths['shakeup'][level.keyI()] = level.totalWidth