import matplotlib.pyplot as plt # This is for creating figures 
import numpy as np # This is for creating a matrix for the heatmap 
import matplotlib.colors as mcolors # This is for normalising data with a set centre 
import json 
from collections import deque # This is for adding power labels. 

from utilities import new_entry, predict_depth, predict_width, calculate_ellipsoid_volume

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
    percentage_error_matrix = np.ones((4, 3)) # Creating the numpy array (which is a matrix) to put into the heatmap 
    highest_percentage_error = np.zeros((1)) # To keep track of the highest percent and then eventually define the scale of the heatmap
    option = input("(Enter/anything) To access previous entries | 'n' To create new entries | 'q' To quit: ").lower()
    if (option=="q"):
        quit()
    elif (option=="n"):
        new_entry()
    else: 
        f= open("data.json","r",encoding="utf-8")
        json_data = json.load(f)
        for metal in json_data:
            this_entry = json_data[metal]
            pow_lb = this_entry["pow_lb"] 
            pow_ub = this_entry["pow_ub"]
            pow_interval = this_entry["pow_interval"] 
            pow_num_intervals = this_entry["pow_num_intervals"]
            speed_lb = this_entry["speed_lb"]
            speed_ub = this_entry["speed_ub"]
            speed_interval = this_entry["speed_interval"]
            speed_num_intervals = this_entry["speed_num_intervals"]

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

                    percentage_error = predicted_volume/actual_volume * 100 
                    ## PROCESSING THE PERCENTAGE ERROR BY CHANGING THE SIGN AND BY RE-ASSIGNING WHAT IS THE HIGHEST PERCENTAGE ERROR IF NECESSARY ##
                    if (pow_count<1):
                        speed.append(str(speed_level * (10**3)) + " mms⁻¹") # Creating labels for the horizontal axis. This only needs to be done once, which can be done in the pow_count = 0 iteration
                    if (predicted_volume<actual_volume):
                        percentage_error =-2* percentage_error # If the predicted volume was lower than the actual, this is reflected in the percentage error with the minus sign in front of the percentage
                    if (percentage_error>highest_percentage_error[0]):
                        highest_percentage_error[0] = percentage_error # Likewise, if the predicted volume was actually larger we just keep it in the positives
                    percentage_error_matrix[row][column] = percentage_error 
            print("Loaded!")
            fig, ax = plt.subplots(figsize = (8,8), layout = "constrained")

            fig.suptitle(metal + ": The effect of scanning speed (mm$s^{-1}$) & power (W) on melt pool width & depth (μm)")
            norm = mcolors.TwoSlopeNorm(vmin=-highest_percentage_error, vcenter = 0, vmax = highest_percentage_error)
            im, cbar = heatmap(percentage_error_matrix, power , speed, ax=ax,
                            cmap="bwr", cbarlabel="Percentage error", norm = norm)
            plt.show()
            quit()