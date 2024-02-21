"""
Module with the plotting functions.
"""

import data.variables as generalVars

import interface.variables as guiVars

import numpy as np

from matplotlib.pyplot import Axes
from matplotlib.markers import MarkerStyle

import mplcursors

from typing import List


# --------------------------------------------------------- #
#                                                           #
#                   FUNCTIONS TO PLOT DATA                  #
#                                                           #
# --------------------------------------------------------- #

# Set of colors to choose from when plotting
col2 = [['b'], ['g'], ['r'], ['c'], ['m'], ['y'], ['k']]
"""
Set of colors to choose from when plotting
"""

# Stick plotter. Plots a stick for the transition
def stem_ploter(a: Axes, x: List[float], y: List[float], JJ: List[int], transition: str, spec_type: str, ind: int = 0, key: str = '', x_up: List[float] = [], y_up: List[float] = [], JJ_up: List[int] = []):
    """
    Stick plotter function. Plots a stick for the transition
        
        Args:
            a: matplotlib axes object where to plot the stems
            x: list of the transition energies
            y: list of the transition intensities
            JJ: list of the transition 2js
            transition: the selected transition to plot
            spec_type: simulation type selected in the interface (diagram, satellite, auger, diagram_cs, satellite_cs, auger_cs)
            ind: shake level index to use when plotting a satellite transition
            key: shake level label to use when plotting a satellite transition
            x_up: list of the shake-up transition energies
            y_up: list of the shake-up transition intensities
            JJ_up: list of the shake-up transition 2js
        
        Returns:
            Nothing, the transition is plotted and the interface is updated
    """
    
    JJs = list(set(JJ))
    JJs_up = list(set(JJ_up))
    
    ys: List[List[float]] = [[] for _ in JJs]
    ys_up: List[List[float]] = [[] for _ in JJs_up]
    xs: List[List[float]] = [[] for _ in JJs]
    xs_up: List[List[float]] = [[] for _ in JJs_up]
    
    if guiVars.JJ_colors.get(): # type: ignore
        for h, j in enumerate(JJ):
            if j not in generalVars.colors_2J:
                generalVars.colors_2J[j] = col2[np.random.randint(0, len(col2))][0]

            i = JJs.index(j)
            ys[i].append(y[h])
            xs[i].append(x[h])
        
        for h, j in enumerate(JJ_up):
            if j not in generalVars.colors_2J:
                generalVars.colors_2J[j] = col2[np.random.randint(0, len(col2))][0]

            i = JJs_up.index(j)
            ys_up[i].append(y_up[h])
            xs_up[i].append(x_up[h])
    
    # Add extra values before and after to make the y start and terminate on 0
    max_value = max(x)
    min_value = min(x)
    x.insert(0, 2 * min_value - max_value)
    x.append(2 * max_value - min_value)
    
    # Calculate the y's weighted with the shake weights depending on the spectrum type and plot the sticks
    # In the case of charge state simulation the y's are also weighted by the selected mixture percentages
    if spec_type == 'Diagram' or spec_type == 'Auger':
        if not guiVars.JJ_colors.get(): # type: ignore
            y.insert(0, 0)
            y.append(0)
            a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, len(col2))][0]), label=str(transition), use_line_collection=True)
            a.legend(loc='best', numpoints=1)
        else:
            for i in range(len(xs)):
                ys[i].insert(0, 0)
                ys[i].append(0)
                a.stem(xs[i], ys[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ[i]]), label=str(transition) + "_" + str(JJ[i]), use_line_collection=True)
                a.legend(loc='best', numpoints=1)
    elif spec_type == 'Satellites':
        if not guiVars.JJ_colors.get(): # type: ignore
            y.insert(0, 0)
            y.append(0)
            a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, len(col2))][0]), label=transition + ' - ' + generalVars.labeldict[key], use_line_collection=True)  # Plot a stemplot
            a.legend(loc='best', numpoints=1)
            
            y_up.insert(0, 0)
            y_up.append(0)
            a.stem(x_up, y_up, markerfmt=' ', linefmt=str(col2[np.random.randint(0, len(col2))][0]), label=transition + ' - ' + generalVars.labeldict[key] + ' - shakeup', use_line_collection=True)  # Plot a stemplot
            a.legend(loc='best', numpoints=1)
        else:
            for i in range(len(xs)):
                ys[i].insert(0, 0)
                ys[i].append(0)
                a.stem(xs[i], ys[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ[i]]), label=transition + ' - ' + generalVars.labeldict[key] + '_' + str(JJ[i]), use_line_collection=True)  # Plot a stemplot
                a.legend(loc='best', numpoints=1)
            
            for i in range(len(xs_up)):
                ys_up[i].insert(0, 0)
                ys_up[i].append(0)
                a.stem(xs_up[i], ys_up[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ_up[i]]), label=transition + ' - ' + generalVars.labeldict[key] + ' - shakeup_' + str(JJ_up[i]), use_line_collection=True)  # Plot a stemplot
                a.legend(loc='best', numpoints=1)
    elif spec_type == 'Diagram_CS' or spec_type == 'Auger_CS':
        if not guiVars.JJ_colors.get(): # type: ignore
            y.insert(0, 0)
            y.append(0)
            a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, len(col2))][0]), label=str(transition), use_line_collection=True)
            a.legend(loc='best', numpoints=1)
        else:
            for i in range(len(xs)):
                ys[i].insert(0, 0)
                ys[i].append(0)
                a.stem(xs[i], ys[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ[i]]), label=str(transition) + "_" + str(JJ[i]), use_line_collection=True)
                a.legend(loc='best', numpoints=1)
    elif spec_type == 'Satellites_CS':
        if not guiVars.JJ_colors.get(): # type: ignore
            y.insert(0, 0)
            y.append(0)
            a.stem(x, y, markerfmt=' ', linefmt=str(col2[np.random.randint(0, len(col2))][0]), label=transition + ' - ' + generalVars.labeldict[key], use_line_collection=True)  # Plot a stemplot
            a.legend(loc='best', numpoints=1)
            
            y_up.insert(0, 0)
            y_up.append(0)
            a.stem(x_up, y_up, markerfmt=' ', linefmt=str(col2[np.random.randint(0, len(col2))][0]), label=transition + ' - ' + generalVars.labeldict[key] + ' - shakeup', use_line_collection=True)  # Plot a stemplot
            a.legend(loc='best', numpoints=1)
        else:
            for i in range(len(xs_up)):
                ys[i].insert(0, 0)
                ys[i].append(0)
                a.stem(xs[i], ys[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ[i]]), label=transition + ' - ' + generalVars.labeldict[key] + "_" + str(JJ[i]), use_line_collection=True)  # Plot a stemplot
                a.legend(loc='best', numpoints=1)
                
                ys_up[i].insert(0, 0)
                ys_up[i].append(0)
                a.stem(xs_up[i], ys_up[i], markerfmt=' ', linefmt=str(generalVars.colors_2J[JJ_up[i]]), label=transition + ' - ' + generalVars.labeldict[key] + ' - shakeup_' + str(JJ_up[i]), use_line_collection=True)  # Plot a stemplot
                a.legend(loc='best', numpoints=1)
    
    # --------------------------------------------------------------------------------------------------------------------------
    # Automatic legend formating
    a.legend(title=generalVars.element_name, title_fontsize='large')
    a.legend(title=generalVars.element_name)
    # Number of total labels to place in the legend
    number_of_labels = len(a.legend().get_texts())
    # Initialize the numeber of legend columns
    legend_columns = 1
    # Initialize the number of legends in each columns
    labels_per_columns = number_of_labels / legend_columns
    
    # While we have more than 10 labels per column
    while labels_per_columns > 10:
        # Add one more column
        legend_columns += 1
        # Recalculate the number of labels per column
        labels_per_columns = number_of_labels / legend_columns
    
    # Place the legend with the final number of columns
    a.legend(ncol=legend_columns)
    
    return a

# Profile simulation plotter. Plots the transitions with a line profile shape
def simu_plot(sat: str, graph_area: Axes, normalization_var: float, y0: float, plotSimu: bool = True):
    """
    Function to plot the simulation values according to the selected transition types.
    
        Args:
            sat: simulation type selected in the interface (diagram, satellite, auger)
            graph_area: matplotlib graph to plot the simulated transitions
            normalization_var: normalization multiplier to normalize intensity when plotting
            y0: intensity offset user value from the interface
        
        Returns:
            graph_area. The updated interface graph_area object.
    """
    
    totalDiagInt = []
    if 'Diagram' in sat:
        for index, key in enumerate(generalVars.the_dictionary):
            if generalVars.the_dictionary[key]["selected_state"]:
                totalDiagInt.append(sum(generalVars.yfinal[index]))
                if plotSimu:
                    # Plot the selected transition
                    graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal[index]) * normalization_var) + y0, label=key, gid=key, color=str(col2[np.random.randint(0, len(col2))][0]))  # Plot the simulation of all lines
                    graph_area.legend()
    if 'Satellites' in sat:
        totalShakeoffInt = []
        totalShakeupInt = []
        for index, key in enumerate(generalVars.the_dictionary):
            if generalVars.the_dictionary[key]["selected_state"]:
                for l, m in enumerate(generalVars.yfinals[index]):
                    # Dont plot the satellites that have a max y value of 0
                    if max(m) != 0:
                        if l < len(generalVars.label1):
                            totalShakeoffInt.append(sum(m))
                        else:
                            totalShakeupInt.append(sum(m))
                        if plotSimu:
                            # Plot the selected transition
                            if l < len(generalVars.label1):
                                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinals[index][l]) * normalization_var) + y0, label=key + ' - ' + generalVars.labeldict[generalVars.label1[l]], gid=key + ' - ' + generalVars.labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, len(col2))][0]))  # Plot the simulation of all lines
                            else:
                                graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinals[index][l]) * normalization_var) + y0, label=key + ' - ' + generalVars.labeldict[generalVars.label1[l - len(generalVars.label1)]] + ' - shake-up', gid=key + ' - ' + generalVars.labeldict[generalVars.label1[l - len(generalVars.label1)]] + ' - shake-up', color=str(col2[np.random.randint(0, len(col2))][0]))  # Plot the simulation of all lines
                            graph_area.legend()
        print(str(guiVars.excitation_energy.get()) + "; " + str(sum(totalDiagInt)) + "; " + str(sum(totalShakeoffInt)) + "; " + str(sum(totalShakeupInt))) # type: ignore
    if sat == 'Auger':
        for index, key in enumerate(generalVars.the_aug_dictionary):
            if generalVars.the_aug_dictionary[key]["selected_state"]:
                if plotSimu:
                    # Plot the selected transition
                    graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal[index]) * normalization_var) + y0, label=key, gid=key, color=str(col2[np.random.randint(0, len(col2))][0]))  # Plot the simulation of all lines
                    graph_area.legend()
    
    if guiVars.totalvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.ytot) * normalization_var) + y0, label='Total', gid='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totaldiagvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.ydiagtot) * normalization_var) + y0, label='Total Diagram', gid='Total Diagram', ls='--', lw=2, color='r')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totalsatvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.ysattot) * normalization_var) + y0, label='Total Satellite', gid='Total Satellite', ls='--', lw=2, color='b')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totalshkoffvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkofftot) * normalization_var) + y0, label='Total Shake-off', gid='Total Shake-off', ls='--', lw=2, color='g')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totalshkupvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkuptot) * normalization_var) + y0, label='Total Shake-up', gid='Total Shake-up', ls='--', lw=2, color='m')  # Plot the simulation of all lines
        graph_area.legend()
    
    if len(generalVars.yextras) > 0:
        for i, key in enumerate(generalVars.extra_fitting_functions):
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextras[i]) * normalization_var) + y0, label=key, gid=key, ls=':', lw=2, color=str(col2[np.random.randint(0, len(col2))][0]))
            graph_area.legend()
        
        if guiVars.totalextrafitvar.get() == 'Total': # type: ignore
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextrastot) * normalization_var) + y0, label='Total Extra Fit', gid='Total Extra Fit', ls='--', lw=2, color='y')
            graph_area.legend()
    
    if plotSimu:
        lines = graph_area.get_lines()
        
        cursor = mplcursors.cursor(lines, hover=True)
        cursor.connect('add', lambda sel: sel.annotation.set_text(sel.artist.get_label()))
    
    return graph_area

# Profile simulation plotter for charge state mixtures. Plots the transitions with a line profile shape
def Msimu_plot(ploted_cs: List[str], sat: str, graph_area: Axes,
               normalization_var: float, y0: float):
    """
    Function to plot the simulation values according to the selected transition types.
    
        Args:
            ploted_cs: list of the charge states to be plotted
            sat: simulation type selected in the interface (diagram, satellite, auger)
            graph_area: matplotlib graph to plot the simulated transitions
            normalization_var: normalization multiplier to normalize intensity when plotting
            y0: intensity offset user value from the interface
            total: flag from the interface to plot the total intensity
        
        Returns:
            Nothing. The interface is updated with the new simulation data.
    """
    
    if 'Diagram' in sat:
        for cs_index, cs in enumerate(ploted_cs):
            for index, key in enumerate(generalVars.the_dictionary):
                if generalVars.the_dictionary[key]["selected_state"]:
                    # Plot the selected transition
                    graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal[cs_index * len(generalVars.the_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, gid=cs + ' ' + key, color=str(col2[np.random.randint(0, len(col2))][0]))  # Plot the simulation of all lines
                    graph_area.legend()
    if 'Satellites' in sat:
        for cs_index, cs in enumerate(ploted_cs):
            for index, key in enumerate(generalVars.the_dictionary):
                if generalVars.the_dictionary[key]["selected_state"]:
                    for l, m in enumerate(generalVars.yfinals[cs_index * len(generalVars.the_dictionary) + index]):
                        # Dont plot the satellites that have a max y value of 0
                        if max(m) != 0:
                            # Plot the selected transition
                            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinals[cs_index * len(generalVars.the_dictionary) + index][l]) * normalization_var) + y0, label=cs + ' ' + key + ' - ' + generalVars.labeldict[generalVars.label1[l]], gid=cs + ' ' + key + ' - ' + generalVars.labeldict[generalVars.label1[l]], color=str(col2[np.random.randint(0, len(col2))][0]))  # Plot the simulation of all lines
                            graph_area.legend()
    if sat == 'Auger':
        for cs_index, cs in enumerate(ploted_cs):
            for index, key in enumerate(generalVars.the_aug_dictionary):
                if generalVars.the_aug_dictionary[key]["selected_state"]:
                    # Plot the selected transition
                    graph_area.plot(generalVars.xfinal, (np.array(generalVars.yfinal[cs_index * len(generalVars.the_aug_dictionary) + index]) * normalization_var) + y0, label=cs + ' ' + key, gid=cs + ' ' + key, color=str(col2[np.random.randint(0, len(col2))][0]))  # Plot the simulation of all lines
                    graph_area.legend()
    if guiVars.totalvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.ytot) * normalization_var) + y0, label='Total', gid='Total', ls='--', lw=2, color='k')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totaldiagvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.ydiagtot) * normalization_var) + y0, label='Total Diagram', gid='Total Diagram', ls='--', lw=2, color='r')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totalsatvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.ysattot) * normalization_var) + y0, label='Total Satellite', gid='Total Satellite', ls='--', lw=2, color='b')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totalshkoffvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkofftot) * normalization_var) + y0, label='Total Shake-off', gid='Total Shake-off', ls='--', lw=2, color='g')  # Plot the simulation of all lines
        graph_area.legend()
    if guiVars.totalshkupvar.get() == 'Total': # type: ignore
        # Plot the selected transition
        graph_area.plot(generalVars.xfinal, (np.array(generalVars.yshkuptot) * normalization_var) + y0, label='Total Shake-up', gid='Total Shake-up', ls='--', lw=2, color='m')  # Plot the simulation of all lines
        graph_area.legend()
    
    if len(generalVars.yextras) > 0:
        for i, key in enumerate(generalVars.extra_fitting_functions):
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextras[i]) * normalization_var) + y0, label=key, gid=key, ls=':', lw=2, color=str(col2[np.random.randint(0, len(col2))][0]))
            graph_area.legend()
        
        if guiVars.totalextrafitvar.get() == 'Total': # type: ignore
            graph_area.plot(generalVars.xfinal, (np.array(generalVars.yextrastot) * normalization_var) + y0, label='Total Extra Fit', gid='Total Extra Fit', ls='--', lw=2, color='y')
            graph_area.legend()

    lines = graph_area.get_lines()
    cursor = mplcursors.cursor(lines, hover=True)
    cursor.connect('add', lambda sel: sel.annotation.set_text(sel.artist.get_label()))
    
    return graph_area

# Function to plot the experimental data and std deviation on the residue plot
def plotExp(graph_area: Axes, residues_graph: Axes, exp_x: List[float], exp_y: List[float], exp_sigma: List[float], normalize: str):
    """
    Function to plot the experimental data and std deviation on the residue plot
    
        Args:
            graph_area: new matplotlib plot configured to make space for the residue graph
            residues_graph: matplotlib plot for the residue data
            exp_x: energy values from the experimental spectrum
            exp_y: intensity values from the experimental spectrum
            exp_sigma: error values from the experimental spectrum
            normalize: normalization type selected in the interface
        
        Returns:
            Nothing, the function plots the normalized experimetnal spectrum in the simulation plot and the experimental errors in the residue plot
    """
    if normalize == 'One':
        # Plot experimental data normalized to unity
        graph_area.scatter(np.array(exp_x), np.array(exp_y) / max(exp_y), marker=MarkerStyle('.'), label='Exp.')
        # Plot std deviation in the residue graph (positive line)
        residues_graph.plot(np.array(exp_x), np.array(exp_sigma) / max(exp_y), 'k--')
        # Plot std deviation in the residue graph (negative line)
        residues_graph.plot(np.array(exp_x), -np.array(exp_sigma) / max(exp_y), 'k--')
    else:
        # Plot experimental data with the current normalization
        graph_area.scatter(np.array(exp_x), np.array(exp_y), marker=MarkerStyle('.'), label='Exp.')
        # Plot std deviation in the residue graph (positive line)
        residues_graph.plot(np.array(exp_x), np.array(exp_sigma), 'k--')
        # Plot std deviation in the residue graph (negative line)
        residues_graph.plot(np.array(exp_x), -np.array(exp_sigma), 'k--')
    
    graph_area.legend()



def format_legend(graph_area: Axes):
    """
    Function to format the legend.
    
        Args:
            graph_area: matplotlib graph to plot the simulated transitions
        
        Returns:
            Nothing. The legend is formated and updated on the interface.
    """
    
    # Number of total labels to place in the legend
    number_of_labels = len(graph_area.legend().get_texts())
    # Initialize the numeber of legend columns
    legend_columns = 1
    # Initialize the number of legends in each columns
    labels_per_columns = number_of_labels / legend_columns
    # While we have more than 10 labels per column
    while labels_per_columns > 15:
        # Add one more column
        legend_columns += 1
        # Recalculate the number of labels per column
        labels_per_columns = number_of_labels / legend_columns
    
    # Place the legend with the final number of columns
    graph_area.legend(ncol=legend_columns)

