import numpy as np # Help create graphs
import matplotlib.pyplot as plt # This is for creating figures. 
import matplotlib.patches as pat # This is for creating shapes on the figures
import json 

from utilities import new_entry, predict_width, predict_depth

metal_fig = plt.figure(figsize=(8,8), layout="constrained") # figsize is in inches. layout = "contrained" means that the features of the subplots are organised so that they don't overlap with other subplots         

def draw(metal): 
    this_entry = json_data[metal]
    pow_lb = this_entry["pow_lb"] 
    pow_ub = this_entry["pow_ub"]
    pow_num_intervals = 0 
    while (pow_num_intervals == 0):
        pow_interval = this_entry["pow_interval"] 
        pow_range = pow_ub - pow_lb 
        while (pow_range - pow_interval >= 0): 
            pow_num_intervals += 1 
            pow_range -= pow_interval
        if pow_num_intervals == 0: 
            print("Step size is too large for range, please enter a smaller step")
            this_entry["pow_interval"] = float(input("What is the step size of power?: "))
    pow_num_intervals += 1 # We include the lower bound graph

    speed_lb = this_entry["speed_lb"]
    speed_ub = this_entry["speed_ub"]
    speed_num_intervals = 0 
    while (speed_num_intervals == 0):
        speed_interval = this_entry["speed_interval"]
        speed_range = speed_ub - speed_lb 
        while (speed_range - speed_interval >= 0): 
            speed_num_intervals += 1 
            speed_range -= speed_interval
        if speed_num_intervals == 0: 
            print("Step size is too large for range, please enter a smaller step")
            this_entry["pow_interval"] = float(input("What is the step size of speed?: "))
    speed_num_intervals += 1 # We include the lower bound graph
    
    metal_fig.canvas.manager.set_window_title("Figure 1 - " + metal)

    metal_fig.suptitle(metal + ": The effect of scanning speed (mm$s^{-1}$) & power (W) on melt pool width & depth(μm) with laser diameter " + str(round(this_entry["sigma"]*(10**6),0)) + "μm")
        
    # Make a collection of subplots (each with their own information) and are sorted by a y-axis for power and an x-axis for speed. Two loops so that we go through all the desired values of power and speed and make graphs out of each combination 
    plot_idx = 1 # Add subplot index starts from 1
    axs = np.empty((pow_num_intervals, speed_num_intervals), dtype=object)
    for pow_count in range(0,pow_num_intervals,1):
        for speed_count in range (0,speed_num_intervals,1):
            ax = metal_fig.add_subplot(pow_num_intervals, speed_num_intervals, plot_idx)
            axs[pow_count, speed_count] = ax
            plot_idx += 1 
    
    for pow_count in range(0,pow_num_intervals,1):
        for speed_count in range (0,speed_num_intervals,1):
            grid_coordinate = (pow_num_intervals-pow_count-1,speed_count) # The coordinate format is rows and columns, so [0,1] is 0th row and 1st column which is the top left area. We will use the for loop counters to get the actual values (e.g. base speed 750 + speed_interval * speed). Since the goal is to have power increasing as we go up and speed increasing as we go across, we can leave speed as is but we need to take the complement of the power count by having the total number of power intervals subtract the current count, and then subtracting 1 to adjust for counting starting at 0 for the coordinates to work. 

            # Current power (W) and speed (ms⁻¹), standard units
            power_level = pow_lb+(pow_count)*pow_interval
            speed_level = speed_lb+(speed_count)*speed_interval

            # Predicted melt pool width and depth plotting for this specific subplot
            pred_width = round((predict_width(power_level,speed_level,json_data, metal)*(10**6)),0) #10^6 scales the very small width so it can be seen on the subplot
            pred_depth = round((predict_depth(power_level,speed_level,json_data, metal)*(10**6)),0)
            annotation_width = str(pred_width) + "μm"
            annotation_depth = str(pred_depth) + " \nμm"
            
            # Add the x-axis and y-axis labels and the labels for the actual shape of the melt pool
            axs[grid_coordinate].set_xlabel("Width (μm)")
            axs[grid_coordinate].set_ylabel("Depth (μm)")
            axs[grid_coordinate].annotate((annotation_width),(-(pred_width/2)+10,pred_depth+30)) # Label for width 
            axs[grid_coordinate].annotate((annotation_depth),((-pred_width/2)-100,90)) # Label for depth
            axs[grid_coordinate].set_title(str(int(speed_level*(10**3))) + "$mms^{-1}$, " + str(int(power_level)) + "W")

            # Create the objects in the graph 
            half_width = pred_width/2
            axs[grid_coordinate].arrow(-half_width, pred_depth, pred_width-15,0, head_width=10, color="black") # x, y (these 2 are the arrow base), dx, dy (the length of the arrow along x and y direction), head width is along x direction
            axs[grid_coordinate].vlines(x=-half_width,ymin=0,ymax=pred_depth, color='black') # The 2 vertical lines 
            axs[grid_coordinate].vlines(x=half_width,ymin=0,ymax=pred_depth, color='black')
            axs[grid_coordinate].invert_yaxis() # Invert since we're looking at depth
            axs[grid_coordinate].set_xticks(np.arange(-300,301,100)) # The little lines you see on the x and y axis 
            axs[grid_coordinate].set_yticks(np.arange(0,300,50))

            # Ellipse assumption for predicted melt pool (arc is an ellipse)
            predicted_melt_pool = pat.Arc((0,0),width = pred_width, height = 2*pred_depth, theta1=0, theta2=180, fc=(1,0,0,0), edgecolor="red", linestyle="dashed")
            axs[grid_coordinate].add_patch(predicted_melt_pool)

            # Ellipse assumption for actual melt pool 
            if "experiment_data" in this_entry: 
                actual_width = this_entry["experiment_data"][str(power_level)+ ","+str(speed_level)][0]*(10**6)
                actual_depth = this_entry["experiment_data"][str(power_level)+ ","+str(speed_level)][1]*(10**6)
                actual_melt_pool = pat.Arc((0,0),width = actual_width, height = 2*actual_depth, theta1=0, theta2=180, fc=(1,0,0,0.3), edgecolor = "red")

                axs[grid_coordinate].add_patch(actual_melt_pool)
    predicted_melt_pool.set_label("Predicted")
    if "experiment_data" in this_entry:
        actual_melt_pool.set_label("Actual")
    metal_fig.legend()
    metal_fig.canvas.draw_idle()
               
i = 0
keys = []
                
def on_key(e): 
    metal_fig.clf()
    global i
    global keys
    if e.key in ("right", "n"):
        i = (i + 1) % len(keys)
    elif e.key in ("left", "p"):
        i = (i - 1) % len(keys)
    draw(keys[i])
    
# Connect key press event
metal_fig.canvas.mpl_connect('key_press_event', on_key)

if (__name__=='__main__'):
    while (True): 
        option = input("Enter anything to access previous entries, or 'n' To create new entries, or 'q' To quit: ").lower()
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