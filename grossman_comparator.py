# To do: 
# 1. Find out the correct final significant figures by looking into the precision of the values. Perhaps don't use float to avoid precision loss. 
import numpy as np # Help create graphs
import matplotlib.pyplot as plt # This is for creating figures. 
import matplotlib.patches as pat # This is for creating shapes on the figures
import json 

from utilities import new_entry, predict_width, predict_depth

if (__name__=='__main__'):
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

            metal_fig, axs = plt.subplots(pow_num_intervals,speed_num_intervals,figsize=(8,8), layout="constrained") # This creates a pow_num_intervals * speed_num_intervals grid of subplots (aka Axes) which you can plot on. figsize is in inches. layout = "contrained" means that the features of the subplots are organised so that they don't overlap with other subplots. 
            metal_fig.suptitle(metal + ": The effect of scanning speed (mm$s^{-1}$) & power (W) on melt pool width & depth(μm)")
            legend_count = 0
            
            # Make a collection of subplots (each with their own information) and are sorted by a y-axis for power and an x-axis for speed. Two loops so that we go through all the desired values of power and speed and make graphs out of each combination. The loop counters are used to help get these values, they are not the values themselves as you'll see below. 
            for pow_count in range(0,pow_num_intervals,1):
                for speed_count in range (0,speed_num_intervals,1):
                    grid_coordinate = (pow_num_intervals-pow_count-1,speed_count) #The coordinate format is rows and columns, so [0,1] is 0th row and 1st column which is the top left area. We will use the for loop counters to get the actual values (e.g. base speed 750 + speed_interval * speed). Since the goal is to have power increasing as we go up and speed increasing as we go across, we can leave speed as is but we need to take the complement of the power count by having the total number of power intervals subtract the current count, and then subtracting 1 to adjust for counting starting at 0 for the coordinates to work. 

                    # Current power (W) and speed (ms⁻¹), standard units
                    power_level = pow_lb+(pow_count)*pow_interval
                    speed_level = speed_lb+(speed_count)*speed_interval

                    ## Predicted melt pool shape plotting - Melt pool width and depth of this specific subplot calculations
                    pred_width = round((predict_width(power_level,speed_level,json_data, metal)*(10**6)),0) #10^6 is there so it can be seen on the subplot
                    pred_depth = round((predict_depth(power_level,speed_level,json_data, metal)*(10**6)),0)
                    # To help you with debugging if needed
                    # print(str(speed_level)*10 + "$mms^{-1}$, " + str(power_level) + "W depth is " + str(depth))
                    # print("The current power and speed coordinates are: " + str(pow_num_intervals-1-pow_count) + " for power and " + str(speed_count) + " for speed")  
                    annotation_width = str(pred_width) + "μm"
                    annotation_depth = str(pred_depth) + " \nμm"
                    
                    # Adding the labels to the graphs, so the basic x-axis and y-axis labels and then the labels for the actual shape of the melt pool
                    axs[grid_coordinate].set_xlabel("Width (μm)")
                    axs[grid_coordinate].set_ylabel("Depth (μm)")
                    axs[grid_coordinate].annotate((annotation_width),(-(pred_width/2)+10,pred_depth+30)) # This annotates the label for the width of the melt pool onto the graph
                    axs[grid_coordinate].annotate((annotation_depth),((-pred_width/2)-100,90)) # This annotates the label for the depth of the melt pool on to the graph
                    axs[grid_coordinate].set_title(str(int(speed_level*(10**3))) + "$mms^{-1}$, " + str(int(power_level)) + "W")

                    # Creating the objects in the graph 
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
                    actual_width = this_entry["experiment_data"][str(power_level)+ ","+str(speed_level)][0]*(10**6)
                    actual_depth = this_entry["experiment_data"][str(power_level)+ ","+str(speed_level)][1]*(10**6)
                    actual_melt_pool = pat.Arc((0,0),width = actual_width, height = 2*actual_depth, theta1=0, theta2=180, fc=(1,0,0,0.3), edgecolor = "red")

                    axs[grid_coordinate].add_patch(actual_melt_pool)

                    # The legend only needs to be added once
                    if (legend_count==0):
                        predicted_melt_pool.set_label("Predicted")
                        actual_melt_pool.set_label("Actual")
                        legend_count+=1
                        metal_fig.legend()
        print("Loaded!")
        plt.show()
        quit()