"""
Module with profile functions for line simulation.
"""

from __future__ import annotations


#Import numpy
import numpy as np

from scipy.special import wofz


from typing import List
import numpy.typing as npt


# --------------------------------------------------------- #
#                                                           #
#            MATH FUNCTIONS FOR LINE PROFILES               #
#                                                           #
# --------------------------------------------------------- #

# Gaussian profile
def G(T: npt.NDArray[np.float64], energy: float, intens: float, res: float, width: float):
    """ 
    Function to calculate the Gaussian line shape at x with HWHM alpha
        
        Args:
            T: list of x values for which we want the y values of the profile
            energy: x value of the profile center
            intens: hight of the profile
            res: experimental resolution to be added to the profile width
            width: natural width of the transition for the profile
        
        Returns:
            y: list of y values for each of the x values in T
    """
    y: npt.NDArray[np.float64] = intens * np.sqrt(np.log(2) / np.pi) / (res + width) * np.exp(-((T - energy) / (res + width)) ** 2 * np.log(2))
    
    return y

# Lorentzian profile
def L(T: npt.NDArray[np.float64], energy: float, intens: float, res: float, width: float):
    """ 
    Function to calculate the Lorentzian line shape at x with HWHM alpha
        
        Args:
            T: list of x values for which we want the y values of the profile
            energy: x value of the profile center
            intens: hight of the profile
            res: experimental resolution to be added to the profile width
            width: natural width of the transition for the profile
        
        Returns:
            y: list of y values for each of the x values in T
    """
    y: npt.NDArray[np.float64] = intens * (0.5 * (width + res) / np.pi) / ((T - energy) ** 2 + (0.5 * (width + res)) ** 2)
    
    return y

# Voigt profile
def V(T: npt.NDArray[np.float64], energy: float, intens: float, res: float, width: float):
    """ 
    Function to calculate the Voigt line shape at x with HWHM alpha
        
        Args:
            T: list of x values for which we want the y values of the profile
            energy: x value of the profile center
            intens: hight of the profile
            res: experimental resolution to be added to the profile width
            width: natural width of the transition for the profile
        
        Returns:
            y: list of y values for each of the x values in T
    """
    sigma: float = res / np.sqrt(2 * np.log(2))
    y: npt.NDArray[np.float64] = np.real(intens * wofz(complex(T - energy, width / 2) / sigma / np.sqrt(2))) / sigma / np.sqrt(2 * np.pi)
    
    return y
