"""
Module with functions to setup the experimental spectra for the simulation
"""

from typing import List
import numpy as np

# --------------------------------------------------------- #
#                                                           #
#    FUNCTIONS TO USE AND CONFIGURE EXPERIMENTAL SPECTRA    #
#                                                           #
# --------------------------------------------------------- #

# Extract x, y and sigma values from the read experimental file
def extractExpVals(exp_spectrum: List[List[str]]):
    """
    Function to extract x, y and sigma values from the read experimental file
        
        Args:
            exp_spectrum: list with the experimental spectrum to be handled
        
        Returns:
            xe: energy values of the experimental spectrum
            ye: intensity values of the experimental spectrum
            sigma_exp: error values of the experimental spectrum (sqrt(intensity) by default if no data is provided)
    """
    # for i, it in enumerate(exp_spectrum):
    #     # Convert the loaded values to float. Update this to a map function?
    #     for j, itm in enumerate(exp_spectrum[i]):
    #         if exp_spectrum[i][j] != '':
    #             exp_spectrum[i][j] = float(itm)
    
    # Split the values into x and y
    xe = np.array([float(row[0]) for row in exp_spectrum], dtype=np.float64)
    ye = np.array([float(row[1]) for row in exp_spectrum], dtype=np.float64)
    
    # If the spectrum has 3 columns of data then use the third column as the uncertainty
    if len(exp_spectrum[0]) >= 3:
        sigma_exp = np.array([float(row[2]) for row in exp_spectrum], dtype=np.float64)
    else:
        # Otherwise use the sqrt of the count number
        tpy = type(ye)
        sigma_exp: tpy = np.sqrt(ye)
    
    return xe, ye, sigma_exp


