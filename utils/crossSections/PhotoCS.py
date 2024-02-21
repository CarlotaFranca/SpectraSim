
"""
Module that implements the functions for calculating the Photo Ionization cross section.
At the moment only the ELAM database is used.
"""

import data.variables as generalVars

import math

from scipy.interpolate import interp1d

def setupELAMPhotoIoniz():
    found = False
    x = []
    y = []
    
    for line in generalVars.ELAMelement:
        if 'Scatter' in line:
            break
        if found:
            values = line.split()
            x.append(float(values[0]))
            y.append(math.exp(float(values[1])))
        if 'Photo' in line:
            found = True
    
    generalVars.ELAMPhotoSpline = interp1d(x, y)
    print(generalVars.ELAMPhotoSpline)
