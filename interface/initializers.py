
import data.variables as generalVars

import interface.variables as guiVars

from simulation.simulation import simulate

from interface.updaters import selected, selected_2j, reset_limits, select_all_transitions, update_offsets, update_transition_dropdown

from interface.base import _quit, restarter

from interface.extras import startMatrixWindow, startBoostWindow, \
                            startCascadeDiagram, startCascadeSatellite, startCascadeAuger, \
                            startConvergenceWindow, configureCSMix, fitOptionsWindow, \
                            configure_shake_params

from utils.misc.fileIO import load, load_effic_file, write_to_xls

#GUI Imports
from tkinter import *
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure

# --------------------------------------------------------- #
#                                                           #
#      FUNCTIONS TO INITIALIZE AND CONFIGURE ELEMENTS       #
#                                                           #
# --------------------------------------------------------- #

# Initialize and configure the simulation plot
def configureSimuPlot():
    """
    Function to initialize and configure the simulation window and plot
        
        Args:
            
        
        Returns:
            sim: tkinter simulation window object
            panel_1: tkinter panel object to hold the simulation frame
            f: matplotlib figure object for the simulation plot
            a: maplotlib plot object where we will plot the simulation data
            figure_frame: tkinter frame object to hold the tkinter simulation figure object
            canvas: tkinter object we can place in the frame which is created from the matplotlib figure
    """
    
    # ---------------------------------------------------------------------------------------------------------------
    # Start a new window for the simulation plot. We use TopLevel as we want this window to be the main interface
    sim = Toplevel(master=guiVars._parent)
    # Define the title
    sim.title("Spectrum Simulation")
    # Pack a panel into the window where we will place our canvas to plot the simulations. This way the window will properly resize
    panel_1 = PanedWindow(sim, orient=VERTICAL)
    panel_1.pack(fill=BOTH, expand=1)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Matplotlib figure where we will place the graph objects
    f = Figure(figsize=(10, 5), dpi=100)
    # Add a plotting space to the figure
    a = f.add_subplot(111)
    # Set labels for the axis
    a.set_xlabel('Energy (eV)')
    a.set_ylabel('Intensity (arb. units)')
    
    
    # ---------------------------------------------------------------------------------------------------------------
    # Frame where we will place the figure with the graph
    figure_frame = Frame(panel_1, relief=GROOVE) # grooved border style
    # Add the frame to the panel
    panel_1.add(figure_frame)
    # Create the tk widget canvas to place the figure in the frame
    canvas = FigureCanvasTkAgg(f, master=figure_frame)
    # pack the canvas in the frame
    canvas.get_tk_widget().pack(fill=BOTH, expand=1)

    # Store the interface objects for use in other functions across the file
    guiVars._a = a
    guiVars._f = f
    guiVars._sim = sim
    guiVars._canvas = canvas
    
    return sim, panel_1, f, a, figure_frame, canvas

# Initialize and configure the areas where we will place the buttons, entries and labels for the simulation parameters
def configureButtonArea(sim: Toplevel, canvas: FigureCanvasTkAgg):
    """
    Function to initialize and configure the areas where we will place the buttons, entries and labels for the simulation parameters
        
        Args:
            sim: tkinter simulation window object
            canvas: tkinter object we can place in the frame which is created from the matplotlib figure
        
        Returns:
            panel_2: tkinter panel placed below the simulation plot
            toolbar_frame: tkinter frame for the matplotlib graph buttons
            toolbar: tkinter object for the matplotlib default toolbar
            full_frame: tkinter frame for the remaining buttons
            buttons_frame: tkinter frame for the transition dropdown
            buttons_frame2: tkinter frame for the bounds entries and reset button
            buttons_frame3: tkinter frame for the simulation parameters entries (offsets, resolution, calculate button)
            buttons_frame4: tkinter frame for the progress bar
    """
    # Panel for the area below the plot
    panel_2 = PanedWindow(sim, orient=VERTICAL)
    panel_2.pack(fill=X, expand=0)

    # Matplotlib toolbar
    toolbar_frame = Frame(panel_2, bd=1, relief=GROOVE)
    panel_2.add(toolbar_frame)
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)

    # Frame for the buttons
    full_frame = Frame(panel_2, relief=GROOVE)
    panel_2.add(full_frame)
    buttons_frame = Frame(full_frame, bd=1, relief=GROOVE)
    buttons_frame.pack(fill=BOTH, expand=1)
    # Max, min & Points Frame
    buttons_frame2 = Frame(full_frame, bd=1, relief=GROOVE)
    buttons_frame2.pack(fill=BOTH, expand=1)
    # Frame  yoffset, Energy offset and Calculate
    buttons_frame3 = Frame(full_frame, bd=1, relief=GROOVE, name='buttons_frame3')
    buttons_frame3.pack(fill=BOTH, expand=1)
    # Frame progress bar
    buttons_frame4 = Frame(full_frame)
    buttons_frame4.pack(fill=BOTH, expand=1)

    guiVars._toolbar = toolbar
    
    return panel_2, toolbar_frame, toolbar, full_frame, buttons_frame, buttons_frame2, buttons_frame3, buttons_frame4

# Setup the variables to hold the values of the interface entries
def setupVars(p: Tk):
    """
    Function to setup the variables to hold the values of the interface entries
        
        Args:
            p: tkinter parent object
        
        Returns:
            Nothing, all the variables initalized in the function are global module variables that can be used in other modules directly
    """
    # setup the parent object to bind stuff to
    guiVars._parent = p
    
    # ---------------------------------------------------------------------------------------------------------------
    # Variable to know if we need to show the total y in the plot
    guiVars.totalvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totalvar.set('No')
    # Variable to know if we need to show the total diagram y in the plot
    guiVars.totaldiagvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totaldiagvar.set('No')
    # Variable to know if we need to show the total satellite y in the plot
    guiVars.totalsatvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totalsatvar.set('No')
    # Variable to know if we need to show the total shake-off y in the plot
    guiVars.totalshkoffvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totalshkoffvar.set('No')
    # Variable to know if we need to show the total shake-up y in the plot
    guiVars.totalshkupvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totalshkupvar.set('No')
    # Variable to know if we need to show the total extra fit y in the plot
    guiVars.totalextrafitvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.totalextrafitvar.set('No')
    # Variable to know if we need to make the y axis logarithmic or linear
    guiVars.yscale_log = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.yscale_log.set('No')
    # Variable to know if we need to make the x axis logarithmic or linear
    guiVars.xscale_log = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.xscale_log.set('No')
    # Variable to know if we need to perform an autofit of the simulation to experimental data
    guiVars.autofitvar = StringVar(master = guiVars._parent)
    # Initialize it as false
    guiVars.autofitvar.set('No')
   
    # Variable to know what normalization we need to perform (no normalization, normalize to unity, normalize to experimental maximum)
    guiVars.normalizevar = StringVar(master = guiVars._parent)
    # Initialize to no normalization
    guiVars.normalizevar.set('No')
    # Variable to know if we need to load an experimental spectrum and if so where it is located
    guiVars.loadvar = StringVar(master = guiVars._parent)
    # Initialize to no file
    guiVars.loadvar.set('No')
    # Variable to know if we need to load detector efficiency data and if so where it is located
    guiVars.effic_var = StringVar(master = guiVars._parent)
    # Initialize to no file
    guiVars.effic_var.set('No')

    # Variable to hold the experimental resolution value introduced in the interface
    guiVars.exp_resolution = DoubleVar(master = guiVars._parent, value=1.0)
    # Variable to hold the experimental background offset value introduced in the interface
    guiVars.yoffset = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the experimental energy offset value introduced in the interface
    guiVars.energy_offset = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the experimental satellite energy offset value introduced in the interface
    guiVars.sat_energy_offset = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the experimental shake-off energy offset value introduced in the interface
    guiVars.shkoff_energy_offset = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the experimental shake-up energy offset value introduced in the interface
    guiVars.shkup_energy_offset = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the excitation/beam energy value introduced in the interface
    guiVars.excitation_energy = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the excitation/beam energy FWHM value introduced in the interface
    guiVars.excitation_energyFWHM = DoubleVar(master = guiVars._parent, value=0.0)
    # Variable to hold the number of points to simulate introduced in the interface
    guiVars.number_points = IntVar(master = guiVars._parent, value=500)
    
    # Variable to hold the maximum x value to be simulated introduced in the interface
    guiVars.x_max = StringVar(master = guiVars._parent)
    # Initialize to be calculated automatically
    guiVars.x_max.set('Auto')
    # Variable to hold the minimum x value to be simulated introduced in the interface
    guiVars.x_min = StringVar(master = guiVars._parent)
    # Initialize to be calculated automatically
    guiVars.x_min.set('Auto')
    
    # Variable to hold the percentage of current progress to be displayed in the bottom of the interface
    guiVars.progress_var = DoubleVar(master = guiVars._parent)
    
    # Variable to hold the text with the selected transitions that will be shown in the interface label
    guiVars.label_text = StringVar(master = guiVars._parent)
    
    # Variable to hold the text with the selected 2j values that will be shown in the interface label
    guiVars.jj_text = StringVar(master = guiVars._parent)
    
    # Initialize the transition type to diagram
    guiVars.satelite_var = StringVar(value='Diagram')
    # Initialize the simulation type to simulation
    guiVars.choice_var = StringVar(value='Simulation')
    # Initialize the profile type to lorentzian
    guiVars.type_var = StringVar(value='Lorentzian')
    # Initialize the exitation mechanism to empty as this is not yet implemented
    guiVars.exc_mech_var = StringVar(value='')
    
    # Initialize the cascade flag as false
    guiVars.include_cascades = BooleanVar(value=False)
    # Initialize the separate offsets flag as false
    guiVars.separate_offsets = BooleanVar(value=False)
    # Initialize the separate offsets flag as false
    guiVars.fit_shake_prob = BooleanVar(value=False)
    # Initialize the 2J colors flag as false
    guiVars.JJ_colors = BooleanVar(value=False)
 
# Setup the buttons in the button area
def setupButtonArea(buttons_frame: Frame, buttons_frame2: Frame, buttons_frame3: Frame, buttons_frame4: Frame):
    """
    Function to setup the buttons in the button area
        
        Args:
            buttons_frame: tkinter frame for the transition dropdown
            buttons_frame2: tkinter frame for the bounds entries and reset button
            buttons_frame3: tkinter frame for the simulation parameters entries (offsets, resolution, calculate button)
            buttons_frame4: tkinter frame for the progress bar
        
        Returns:
            Nothing, we just configure the interface elements in the various button frames below the simulation plot
    """
    
    # Before selecting any transition we show this
    guiVars.label_text.set('Select a Transition: ') # type: ignore
    Label(buttons_frame, textvariable=guiVars.label_text).grid(row=0, column=1) # type: ignore
    
    # Before selecting any 2j value we show this
    guiVars.jj_text.set('Select a 2J value: ') # type: ignore
    Label(buttons_frame, textvariable=guiVars.jj_text).grid(row=0, column=3) # type: ignore
    
    
    # Transitions dropdown
    guiVars.drop_menu = ttk.Combobox(buttons_frame, value=[transition for transition in generalVars.the_dictionary], height=5, width=10) # type: ignore
    guiVars.drop_menu.set('Transitions:')
    guiVars.drop_menu.bind("<<ComboboxSelected>>", selected)
    guiVars.drop_menu.grid(row=0, column=0)
    
    # 2J dropdown
    guiVars.drop_menu_2j = ttk.Combobox(buttons_frame, value=["N/A"], height=5, width=10, state='disabled') # type: ignore
    guiVars.drop_menu_2j.set('2J values:')
    guiVars.drop_menu_2j.bind("<<ComboboxSelected>>", selected_2j)
    guiVars.drop_menu_2j.grid(row=0, column=2)
    
    
    # N Points
    ttk.Label(buttons_frame2, text="Points").pack(side=LEFT)
    ttk.Entry(buttons_frame2, width=7, textvariable=guiVars.number_points).pack(side=LEFT) # type: ignore
    # X max
    ttk.Label(buttons_frame2, text="x Max").pack(side=LEFT)
    ttk.Entry(buttons_frame2, width=7, textvariable=guiVars.x_max).pack(side=LEFT) # type: ignore
    # X min
    ttk.Label(buttons_frame2, text="x Min").pack(side=LEFT)
    ttk.Entry(buttons_frame2, width=7, textvariable=guiVars.x_min).pack(side=LEFT) # type: ignore
    # Reset limits button
    ttk.Button(master=buttons_frame2, text="Reset", command=lambda: reset_limits()).pack(side=LEFT, padx=(10, 0))
    # Select all transitions
    ttk.Button(master=buttons_frame2, text="Select All Transitions", command=lambda: select_all_transitions()).pack(side=LEFT, padx=(30, 0))
    # Include cascades in simulated intensity
    ttk.Checkbutton(buttons_frame2, text='Cascades', variable=guiVars.include_cascades, onvalue=1, offvalue=0, width=10).pack(side=LEFT, padx=(20, 5)) # type: ignore
    # Swap between all satellite offset and separate shake-off and shake-up offsets
    ttk.Checkbutton(buttons_frame2, text='Separate offsets', variable=guiVars.separate_offsets, command=lambda: update_offsets(buttons_frame3), state='', onvalue=1, offvalue=0, width=15).pack(side=LEFT, padx=(5, 5)) # type: ignore
    # Additional fit parameters for the shake probabilities
    ttk.Checkbutton(buttons_frame2, text='Fit Shake Probabilities', variable=guiVars.fit_shake_prob, command=lambda: configure_shake_params(), state='', onvalue=1, offvalue=0, width=20).pack(side=LEFT, padx=(5, 30)) # type: ignore
    # Plot each 2J with a seperate color (only for stick plots)
    ttk.Checkbutton(buttons_frame2, text='2J Colors (stick)', variable=guiVars.JJ_colors, state='', onvalue=1, offvalue=0, width=15).pack(side=LEFT, padx=(20, 30)) # type: ignore
    
    # Calculate button
    ttk.Style().configure('red/black.TButton', foreground='red', background='black')
    ttk.Button(master=buttons_frame3, text="Calculate", command=lambda: simulate(guiVars._sim, guiVars._f, guiVars._a), style='red/black.TButton').pack(side=RIGHT, padx=(30, 0)) # type: ignore
    # yoffset
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.yoffset).pack(side=RIGHT) # type: ignore
    ttk.Label(buttons_frame3, text="y Offset").pack(side=RIGHT)
    # Shake-up En. Offset
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.shkup_energy_offset, name='shkup_offsetEntry', state='disabled').pack(side=RIGHT, padx=(0, 30)) # type: ignore
    ttk.Label(buttons_frame3, text="Shake-up offset (eV)", name='shkup_offsetLabel', state='disabled').pack(side=RIGHT)
    # Shake-off En. Offset
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.shkoff_energy_offset, name='shkoff_offsetEntry', state='disabled').pack(side=RIGHT, padx=(0, 5)) # type: ignore
    ttk.Label(buttons_frame3, text="Shake-off offset (eV)", name='shkoff_offsetLabel', state='disabled').pack(side=RIGHT)
    # Satellite En. Offset
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.sat_energy_offset, name='sat_offsetEntry').pack(side=RIGHT, padx=(0, 5)) # type: ignore
    ttk.Label(buttons_frame3, text="Satellite offset (eV)", name='sat_offsetLabel').pack(side=RIGHT)
    # En. Offset
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.energy_offset).pack(side=RIGHT, padx=(0, 5)) # type: ignore
    ttk.Label(buttons_frame3, text="En. offset (eV)").pack(side=RIGHT)
    # Beam Energy
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.excitation_energy).pack(side=RIGHT, padx=(0, 30)) # type: ignore
    ttk.Label(buttons_frame3, text="Beam Energy (eV)").pack(side=RIGHT)
    # Beam Energy FWHM
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.excitation_energyFWHM).pack(side=RIGHT, padx=(0, 5)) # type: ignore
    ttk.Label(buttons_frame3, text="Beam FWHM (eV)").pack(side=RIGHT)
    # Energy Resolution
    ttk.Label(buttons_frame3, text="Experimental Resolution (eV)").pack(side=LEFT)
    ttk.Entry(buttons_frame3, width=7, textvariable=guiVars.exp_resolution).pack(side=LEFT) # type: ignore
    
    # Progress Bar
    ttk.Progressbar(buttons_frame4, variable=guiVars.progress_var, maximum=100).pack(fill=X, expand=1) # type: ignore

# Setup the dropdown menus on the top toolbar
def setupMenus(CS_exists: bool):
    """
    Function to setup the dropdown menus on the top toolbar
        
        Args:
            CS_exists: boolean if the charge states folder exists for the current element
        
        Returns:
            Nothing, we just setup the top toolbar and bind the necessary variables and functions to the interface elements
    """
    
    # Initialize the menus
    my_menu = Menu(guiVars._sim)
    guiVars._sim.config(menu=my_menu) # type: ignore
    options_menu = Menu(my_menu, tearoff=0)
    total_menu = Menu(my_menu, tearoff=0)
    stick_plot_menu = Menu(my_menu, tearoff=0)
    transition_type_menu = Menu(my_menu, tearoff=0)
    line_type_menu = Menu(my_menu, tearoff=0)
    fitting_menu = Menu(my_menu, tearoff=0)
    fitting_method = Menu(fitting_menu,tearoff=0)
    norm_menu = Menu(my_menu, tearoff=0)
    exc_mech_menu = Menu(my_menu, tearoff=0)
    tool_menu = Menu(my_menu, tearoff=0)
    cascade_analysis = Menu(my_menu, tearoff=0)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Options dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Options", menu=options_menu)
    options_menu.add_cascade(label="Show Total Y", menu=total_menu)
    total_menu.add_checkbutton(label='Total Y', variable=guiVars.totalvar, onvalue='Total', offvalue='No') # type: ignore
    total_menu.add_checkbutton(label='Total Diagram Y', variable=guiVars.totaldiagvar, onvalue='Total', offvalue='No') # type: ignore
    total_menu.add_checkbutton(label='Total Satellite Y', variable=guiVars.totalsatvar, onvalue='Total', offvalue='No') # type: ignore
    total_menu.add_checkbutton(label='Total Shake-off Y', variable=guiVars.totalshkoffvar, onvalue='Total', offvalue='No') # type: ignore
    total_menu.add_checkbutton(label='Total Shake-up Y', variable=guiVars.totalshkupvar, onvalue='Total', offvalue='No') # type: ignore
    total_menu.add_checkbutton(label='Total Extra Fit Y', variable=guiVars.totalextrafitvar, onvalue='Total', offvalue='No', state='disabled') # type: ignore
    guiVars.total_menu = total_menu
    options_menu.add_separator()
    options_menu.add_checkbutton(label='Log Scale Y Axis', variable=guiVars.yscale_log, onvalue='Ylog', offvalue='No') # type: ignore
    options_menu.add_checkbutton(label='Log Scale X Axis', variable=guiVars.xscale_log, onvalue='Xlog', offvalue='No') # type: ignore
    options_menu.add_separator()
    options_menu.add_command(label="Load Experimental Spectrum", command=lambda: load(guiVars.loadvar)) # type: ignore
    options_menu.add_checkbutton(label="Import Detector Efficiency", command=lambda: load_effic_file(guiVars.effic_var)) # type: ignore
    options_menu.add_separator()
    options_menu.add_command(label="Export Spectrum", command=lambda: write_to_xls(guiVars.satelite_var.get(), guiVars.energy_offset.get(), guiVars.sat_energy_offset.get(), guiVars.shkoff_energy_offset.get(), guiVars.shkup_energy_offset.get(), guiVars.excitation_energy.get(), guiVars.excitation_energyFWHM.get(), guiVars.yoffset.get(), guiVars._residues_graph)) # type: ignore
    options_menu.add_separator()
    options_menu.add_command(label="Choose New Element", command=restarter)
    options_menu.add_command(label="Quit", command=_quit)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Spectrum type dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Spectrum Type", menu=stick_plot_menu)
    stick_plot_menu.add_checkbutton(label='Stick', variable=guiVars.choice_var, onvalue='Stick', offvalue='') # type: ignore
    stick_plot_menu.add_checkbutton(label='Simulation', variable=guiVars.choice_var, onvalue='Simulation', offvalue='') # type: ignore
    stick_plot_menu.add_checkbutton(label='CS Mixture: Stick', variable=guiVars.choice_var, onvalue='M_Stick', offvalue='', command=lambda: configureCSMix(), state='disabled') # type: ignore
    stick_plot_menu.add_checkbutton(label='CS Mixture: Simulation', variable=guiVars.choice_var, onvalue='M_Simulation', offvalue='', command=lambda: configureCSMix(), state='disabled') # type: ignore
    # Active and deactivate the charge state mixture options if they exist
    if CS_exists:
        stick_plot_menu.entryconfigure(2, state=NORMAL)
        # Good TK documentation: https://tkdocs.com/tutorial/menus.html
        stick_plot_menu.entryconfigure(3, state=NORMAL)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Transition type dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Transitions Type", menu=transition_type_menu)
    transition_type_menu.add_checkbutton(label='Diagram', variable=guiVars.satelite_var, onvalue='Diagram', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis)) # type: ignore
    transition_type_menu.add_checkbutton(label='Satellites', variable=guiVars.satelite_var, onvalue='Satellites', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis)) # type: ignore
    transition_type_menu.add_checkbutton(label='Diagram + Satellites', variable=guiVars.satelite_var, onvalue='Diagram + Satellites', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis)) # type: ignore
    transition_type_menu.add_checkbutton(label='Auger', variable=guiVars.satelite_var, onvalue='Auger', offvalue='', command=lambda: update_transition_dropdown(cascade_analysis)) # type: ignore
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Line type dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Line Type", menu=line_type_menu)
    line_type_menu.add_checkbutton(label='Voigt', variable=guiVars.type_var, onvalue='Voigt', offvalue='') # type: ignore
    line_type_menu.add_checkbutton(label='Lorentzian', variable=guiVars.type_var, onvalue='Lorentzian', offvalue='') # type: ignore
    line_type_menu.add_checkbutton(label='Gaussian', variable=guiVars.type_var, onvalue='Gaussian', offvalue='') # type: ignore
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Fitting dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Fitting", menu=fitting_menu)
    fitting_menu.add_cascade(label = "Fit Method", menu = fitting_method)
    fitting_method.add_checkbutton(label='LMFit', variable=guiVars.autofitvar, onvalue='LMFit', offvalue='') # type: ignore
    fitting_method.add_checkbutton(label='iminuit', variable=guiVars.autofitvar, onvalue='iminuit', offvalue='')
    fitting_menu.add_command(label='Aditional Fitting Options', command=lambda: fitOptionsWindow())
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Normalization options dropdown menu and the buttons bound to the corresponding variables and functions
    my_menu.add_cascade(label="Normalization Options", menu=norm_menu)
    norm_menu.add_checkbutton(label='to Experimental Maximum', variable=guiVars.normalizevar, onvalue='ExpMax', offvalue='No') # type: ignore
    norm_menu.add_checkbutton(label='to Unity', variable=guiVars.normalizevar, onvalue='One', offvalue='No') # type: ignore
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the Excitation mechanism dropdown menu and the buttons bound to the corresponding variables and functions (disables as it is not implemented)
    my_menu.add_cascade(label="Excitation Mechanism", menu=exc_mech_menu)
    exc_mech_menu.add_checkbutton(label='Nuclear Electron Capture', variable=guiVars.exc_mech_var, onvalue='NEC', offvalue='', state="disabled") # type: ignore
    exc_mech_menu.add_checkbutton(label='Photoionization (ELAM database)', variable=guiVars.exc_mech_var, onvalue='PIon', offvalue='', state="disabled") # type: ignore
    exc_mech_menu.add_checkbutton(label='Electron Impact Ionization (MRBEB Model)', variable=guiVars.exc_mech_var, onvalue='EII', offvalue='', state="disabled") # type: ignore
    
    if generalVars.meanR_exists:
        exc_mech_menu.entryconfigure(2, state=NORMAL)
    if generalVars.ELAM_exists:
        exc_mech_menu.entryconfigure(1, state=NORMAL)
    
    # ---------------------------------------------------------------------------------------------------------------
    # Add the tools dropdown menu and the buttons bound to the corresponding functions
    my_menu.add_cascade(label="Tools", menu=tool_menu)
    tool_menu.add_command(label="Rate Matrix Analysis", command=lambda: startMatrixWindow(True))
    tool_menu.add_command(label="Boost Matrix Analysis", command=lambda: startBoostWindow(True))
    
    tool_menu.add_cascade(label="Cascade Analysis", menu=cascade_analysis)
    cascade_analysis.add_command(label="Diagram Cascade", command=lambda: startCascadeDiagram())
    cascade_analysis.add_command(label="Satellite Cascade", command=lambda: startCascadeSatellite())
    cascade_analysis.add_command(label="Auger Cascade", command=lambda: startCascadeAuger(), state=DISABLED)
    
    tool_menu.add_command(label="Convergence Analysis", command=lambda: startConvergenceWindow())
    