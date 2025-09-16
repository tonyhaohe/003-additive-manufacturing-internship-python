import matplotlib.pyplot as plt # This is for creating figures 
import numpy as np # This is for creating a matrix for the heatmap 
import matplotlib.colors as mcolors # This is for normalising data with a set centre 
from matplotlib.patches import Patch
import json 
from collections import deque # This is for adding power labels. 

from utilities import new_entry, predict_depth, predict_width, calculate_ellipsoid_volume

fig = plt.figure(figsize = (8,8))
fig.subplots_adjust(right=0.8)

def draw(metal): 
    this_entry = json_data[metal]
    if "experiment_data" not in this_entry: 
        print("There is no experimental data, the heatmap for " + metal + " can't generate")
        return
    pow_lb = this_entry["pow_lb"] 
    pow_ub = this_entry["pow_ub"]
    pow_interval = this_entry["pow_interval"] 
    pow_num_intervals = 0 
    while (pow_num_intervals == 0):
        pow_range = pow_ub - pow_lb 
        while (pow_range - pow_interval >= 0): 
            pow_num_intervals += 1 
            pow_range -= pow_interval
        if pow_num_intervals == 0: 
            print("Step size is too large for range, please enter a smaller step")
            pow_interval = float(input("What is the step size of power?: "))
    pow_num_intervals += 1 # We include the lower bound graph
    speed_lb = this_entry["speed_lb"]
    speed_ub = this_entry["speed_ub"]
    speed_interval = this_entry["speed_interval"]
    speed_num_intervals = 0 
    while (speed_num_intervals == 0):
        speed_range = speed_ub - speed_lb 
        while (speed_range - speed_interval >= 0): 
            speed_num_intervals += 1 
            speed_range -= speed_interval
        if speed_num_intervals == 0: 
            print("Step size is too large for range, please enter a smaller step")
            speed_interval = float(input("What is the step size of speed?: "))
    speed_num_intervals += 1
    
    percentage_error_matrix = np.ones((pow_num_intervals, speed_num_intervals)) # Creating the numpy array (which is a matrix) to put into the heatmap 
    highest_percentage_error = np.zeros((1)) # To keep track of the highest percent and then eventually define the scale of the heatmap
    
    fig.canvas.manager.set_window_title("Figure 2 - Heatmap of Prediction Error for " + metal)


    power = deque()
    speed = []
    # Two loops so that we go through all the desired values of power and speed and calculate the cross-sectional area of the melt pool 
    for pow_count in range(0,pow_num_intervals,1):
        power_level = pow_lb+(pow_count)*pow_interval
        power.appendleft(str(power_level) + "W") # Creating labels for the vertical axis 
        for speed_count in range (0,speed_num_intervals,1):
            speed_level = speed_lb+(speed_count)*speed_interval
            # Heatmap cell coordinate for this specific combination of power and speed 
            row = pow_num_intervals-pow_count-1
            column = speed_count

            ## PREDICTED MELT POOL VOLUME CALCULATION ##
            # Melt pool width and depth of this specific combination of power and speed
            pred_width = predict_width(power_level,speed_level,json_data, metal)
            pred_depth = predict_depth(power_level,speed_level,json_data, metal)
            predicted_volume = calculate_ellipsoid_volume(pred_width, pred_depth)
            actual_width = this_entry["experiment_data"][str(power_level)+ ","+str(speed_level)][0]
            actual_depth = this_entry["experiment_data"][str(power_level)+ ","+str(speed_level)][1]
            actual_volume = calculate_ellipsoid_volume(actual_width, actual_depth)

            percentage_error = (predicted_volume - actual_volume) /actual_volume * 100 
            print("The percentage error for " + str(power_level) + "W " + str(speed_level) + "mms^-1 is " + str(percentage_error))
            print("This is from calculating the ratio of the predicted volume of " + str(predicted_volume) + " and actual volume of " + str(actual_volume))
            ## PROCESSING THE PERCENTAGE ERROR BY CHANGING THE SIGN AND BY RE-ASSIGNING WHAT IS THE HIGHEST PERCENTAGE ERROR IF NECESSARY ##
            if (pow_count<1):
                speed.append(str(speed_level * (10**3)) + " mms⁻¹") # Creating labels for the horizontal axis. This only needs to be done once, which can be done in the pow_count = 0 iteration
            if (abs(percentage_error)>highest_percentage_error[0]):
                print("ok, so we change highest percentage error to" + str(abs(percentage_error)))
                highest_percentage_error[0] = abs(percentage_error) # Likewise, if the predicted volume was actually larger we just keep it in the positives
            percentage_error_matrix[row][column] = percentage_error - 1e-9 # You need the 1e-9 because it pushes you into the boundary of the cell so the console doesn't start throwing error messages (notice that if you remove this, the bottom left corner of the window for some cells might not even display the value)
    norm = mcolors.TwoSlopeNorm(vmin=-highest_percentage_error, vcenter = 0, vmax = highest_percentage_error)
    ax = fig.add_subplot()
    heatmap(percentage_error_matrix, power , speed, ax=ax,
                        cmap="bwr", cbarlabel="Percentage error", norm = norm)
    legend_elements = [
        Patch(facecolor='red', label='Over-predicted'),
        Patch(facecolor='blue', label='Under-predicted')
    ]
    ax.legend(handles=legend_elements, title='Prediction error', loc='upper left', bbox_to_anchor=(1.25,1), borderaxespad=0)
    ax.set_title(metal + ": The effect of scanning speed (mm$s^{-1}$) & power (W) on melt pool width & depth(μm) with laser diameter " + str(round(this_entry["sigma"]*(10**6),0)) + "μm", wrap=True)
    fig.canvas.draw_idle()
    

i = 0    
keys = []
    
def on_key(e): 
    fig.clf()
    global i
    global keys
    if e.key in ("right", "n"):
        i = (i + 1) % len(keys)
    elif e.key in ("left", "p"):
        i = (i - 1) % len(keys)
    draw(keys[i])

# Connect key press event
fig.canvas.mpl_connect('key_press_event', on_key)

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw=None, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (M, N).
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current Axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if ax is None:
        ax = plt.gca()

    if cbar_kw is None:
        cbar_kw = {}

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # Show all ticks and label them with the respective list entries.
    ax.set_xticks(np.arange(data.shape[1]), labels=col_labels)
    ax.set_yticks(np.arange(data.shape[0]), labels=row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=False, bottom=True,
                   labeltop=False, labelbottom=True)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar

if (__name__=='__main__'):
    option = input("(Enter/anything) To access previous entries | 'n' To create new entries | 'q' To quit: ").lower()
    if (option=="q"):
        quit()
    elif (option=="n"):
        new_entry()
    else: 
        print("Use arrow keys ← Left and → Right to navigate entries")
        json_data = {}
        with open("data.json","r",encoding="utf-8") as f:
            json_data = json.load(f)
        keys = list(json_data)
        draw(keys[0])
        plt.show()
        print("Loaded!")
        quit()