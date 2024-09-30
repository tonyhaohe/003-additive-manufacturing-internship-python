import json 
import math # This is for sqrt and other maths 
import numpy as np # This is for creating a matrix for the heatmap 
import matplotlib.pyplot as plt # This is for creating figures. 

def new_entry():
    print("## NAME ##")
    metal = input("Powder formula: ")
    json_data = {}
    this_entry = {}

    print("## POWER & SPEED ##")
    pow_lb = float(input("Lower bound of power range (W): "))
    pow_ub = float(input("Upper bound of power range (W): "))
    pow_interval = float(input("What is the size of the interval of power?: "))
    pow_num_intervals = int((pow_ub-pow_lb)//pow_interval) + 1
    speed_lb = float(input("Lower bound of speed range in mm⁻ˢ: "))*(10**-3)
    speed_ub = float(input("Upper bound of speed range in mm⁻ˢ: ")) *(10**-3)
    speed_interval = float(input("What is the size of the interval of speed?: "))*(10**-3)
    speed_num_intervals = int((speed_ub-speed_lb)//speed_interval) + 1

    this_entry["pow_lb"] = pow_lb 
    this_entry["pow_ub"] = pow_ub
    this_entry["pow_interval"] = pow_interval
    this_entry["pow_num_intervals"]=pow_num_intervals 
    this_entry["speed_lb"] = speed_lb 
    this_entry["speed_ub"] = speed_ub 
    this_entry["speed_interval"] = speed_interval 
    this_entry["speed_num_intervals"] = speed_num_intervals

    print("## WIDTH EQUATION VARIABLES ##")
    const = float(input("Proportionality constant C (has no units): "))
    # rho = 2690-0.19*(melting_temp-293.15) 
    # cp = 536.1+0.035*melting_temp
    rho = float(input("Powder density (kgm⁻³): "))
    cp = float(input("Effective specific heat capacity (Jkg⁻¹K⁻¹): "))
    initial_temp = float(input ("Initial temperature (K, most likely enter 298): "))
    melting_temp = float(input("Melting temperature (K): "))
    temp_change = melting_temp-initial_temp #This represents delta Tl which is the change in temperature between initial state and liquid state of the powder 
    this_entry["const"] = const
    this_entry["rho"] = rho
    this_entry["cp"] = cp
    this_entry["temp_change"] = temp_change

    print("## DEPTH EQUATION VARIABLES ##")
    # conductivity = 113+1.06*(10**-5)*melting_temp
    conductivity = float(input("Conductivity (Wm⁻¹K⁻¹): "))
    ts = float(input("Solidus temperature (K): "))
    t0 = float(input("Plate temperature (K): "))
    hf = float(input("Heat of fusion (Jkg⁻¹): "))
    a = float(input("Absorptivity of the metal (has no units): "))
    thermal_diffusivity = conductivity/(rho*cp)
    sigma = float(input("Laser beam diameter (μm): "))*(10**-6) #So sigma is now in m and in standard units, no need to convert later
    melt_pool_depth_coefficient = float(input("Melt pool depth coefficient (μm): ")) *(10**-6) #So coefficient is in standard units
    this_entry["conductivity"] = conductivity
    this_entry["ts"] = ts
    this_entry["t0"] = t0
    this_entry["hf"] = hf
    this_entry["a"] = a
    this_entry["thermal_diffusivity"] = thermal_diffusivity
    this_entry["sigma"]=sigma 
    this_entry["melt_pool_depth_coefficient"] = melt_pool_depth_coefficient

    print("## EXPERIMENT MELT POOL WIDTH AND DEPTH VALUES ##")
    experiment_data = input("Input experiment values for melt pool width & depth? (y/n): ")
    if (experiment_data =="y"):
        experiment_data = {}
        for pow_count in range (0, pow_num_intervals, 1):
            for speed_count in range (0, speed_num_intervals, 1):
                power_level = pow_lb+(pow_count)*pow_interval
                speed_level = speed_lb+(speed_count)*speed_interval
                actual_width = float(input("Melt pool width (for " + str(power_level) + "W, " + str(speed_level*10**3) + "mm⁻ˢ in μm): "))* (10**-6)
                actual_depth = float(input("Melt pool depth (for " + str(power_level) + "W, " + str(speed_level*10**3) + "mm⁻ˢ in μm): "))* (10**-6) 
                experiment_data[str(power_level) + "," + str(speed_level)] = (actual_width,actual_depth)
        this_entry["experiment_data"] = experiment_data

    with open ("data.json",'r') as file:
        if file.read(2) !="[]" and file.read(2)!="{}" and file.read(2)!="":
            json_data = json.load(file)
        else:
            f = open("data.json","w",encoding="utf-8")
    json_data[metal] = this_entry
    json.dump(json_data,f)


def predict_width(power, speed, json_data, metal): # Please note that these functions I made will only accept standard units in order to get accurate answers
    data = json_data[metal]
    return data["const"] * math.sqrt(power/speed) * math.sqrt(1/(data["rho"]*data["cp"]*data["temp_change"]))

def predict_depth(power, speed, json_data, metal):
    data = json_data[metal]
    enthalpy = (4*data["a"]*power)/(math.pi*data["rho"]*(data["cp"]*(data["ts"]-data["t0"])+data["hf"])*math.sqrt(data["thermal_diffusivity"]*speed*(((data["sigma"]))**3)))# Enthalpy 
    fourier = data["thermal_diffusivity"]/(speed*((data["sigma"]))) # Fourier 
    return enthalpy * math.sqrt(fourier) * (data["melt_pool_depth_coefficient"]) # Melt pool depth calculation

def calculate_ellipsoid_volume(width, depth):
    return ((4/3) * math.pi * (width/2) * (width/2) * (depth/2))/2 # Please note it's a circular cross section that has been assumed by Grossman. See permanent_data.txt
