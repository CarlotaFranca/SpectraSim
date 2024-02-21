# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 09:54:04 2024

@author: Carlota
"""
import matplotlib.pyplot as plt
import numpy as np

from typing import List, Tuple
import numpy.typing as npt
from scipy.interpolate import interp1d
from iminuit import Minuit


## criar dados experimentais

energies = np.linspace(0, 300, 75)
pico_exp = 35
sigma_exp = 5
intensidades_exp =  np.exp(-(energies - pico_exp)**2 / (2 * sigma_exp**2))
plt.plot(energies,intensidades_exp)


## dados simulados

energies_sim = np.linspace(0,100)




def intensidades(params)  :
  pico, sigma = params
  intensidades_sim =  np.exp(-(energies_sim - pico)**2 / (2 * sigma**2))
  return intensidades_sim

def minimize (params):
    
    intensidades_sim = intensidades(params)
    
    f_interpolate = interp1d(energies_sim, intensidades_sim, kind='cubic')
    
    intens_interp: List[float]=[] ## aramzenar os valores esxepimentais
    exp_intensidades_f: List[float] = []  ## valores experimentais
    
   
    for g, h in enumerate(energies):
       
        if h > min(energies_sim) and h < max(energies_sim):  
            
            intens_interp.append(f_interpolate(h))
            exp_intensidades_f.append(intensidades_exp[g]) 
    ##print(intens_interp)
    ##print(exp_intensidades_f)            
     
    return (sum((np.array(intens_interp) - np.array(exp_intensidades_f))**2))
 



def execute(params):
   
    m = Minuit(minimize,params)
    result = m.migrad()
    print(result)
    

execute((35, 5))



   
