# Grossman melt pool width and depth evaluator
The purpose of this project is to have an objective and intuitive evaluation of Grossman et al. model's accuracy in predicting melt pool width and depth and then comparing our own model to see if it does better. grossman_comparator.py helps us see how far off their model was with actual experiment values you can see. grossman_heatmap.py helps us see how far off their model was more intuitively with a glance. 

Power & speed are the independent variables. The programs use the melt pool width model proposed in paper [1] equation 7 (and not 11 since we're using their calculated constant) and the melt pool depth in paper [2] equation 6 (which also uses a constant they calculated): 
- [1] Grossman et al. Melt pool controlled laser powder bed fusion for customised low-density lattice structures
- [2] Grossman et al. Material and process invariant scaling laws to predict porosity of dense and lattice structures in laser powder bed fusion

## How is the data stored? 
Data is stored in data.json in standard units (m, J etc.) even if the prompt is in non-standard units for user convenience. It is stored as a dictionary. The top level has metal names with corresponding dictionaries to contain variables required for calculating expected melt pool width and melt pool depth. Experiment data is also stored. To see the sources of the values of the variables, see below:

## Personal references and choice of variable values explained:
Not the actual final source for the values, just for personal reference for what paper/place I encountered them in. We're focussing on AlSi10Mg, not Ti6Al14V or 1.2709. I placed the values we are using for the Eager Tsai model after the Grossman values because I thought we'd be using them to fairly evaluate Grossman's model compared to ours. But this I realised this was a flawed approach since their model purposefully didn't account for the effect of temperature change at many points in time on their values for simplicity's sake (so some of our values wouldn't work anyway) and because we're using their proportionality constant for the melt-pool width and their melt pool depth coefficient. I'd need to use the values they've used to maintain fair comparison. So there was some wasted effort, but a lesson learned. Anyways, see the following key:
- [1] Grossman et al. Melt pool controlled laser powder bed fusion for customised low-density lattice structures
- [2] Grossman et al. Material and process invariant scaling laws to predict porosity of dense and lattice structures in laser powder bed fusion
- [3] properties AlSi10Mg.xlsx (by Sam)

Please note that melt pool width is "maximum melt pool width" (with an assumption of a "circular cross section") from [1] p.4 figure 3. Hence, it refers to the width at the top of the melt pool.
Also please note that the json data DOES NOT CURRENTLY CONTAIN ACTUAL EXPERIMENTAL DATA. It is merely dummy data. 

## Data for AlSi10Mg below: 
### Machine power and speed variables - clean
- Lower bound of power range = 100W from our decision 
- Upper bound of power range = 400W from our decision
- Size of intervals of power = 100W from our decision
- Lower bound of speed range = 750 from our decision
- Upper bound of speed range = 2250 from our decision
- Size of intervals of speed = 750 from our decision 

### Width equation variables - clean, however the choice for initial temperature might need to be looked at. 
- Proportionality constant = 0.49 from [1] p.7 table 3 (determined by Grossman et al. by regression analysis). 
- Material density = 2670 from [1] p.4 table 2 | 2690-0.19\*(current_temp-293.15) from [3] - I have chosen 2670 
- Specific heat capacity = 910 from [1] p.4 table 2 |  536.1+0.035\*current_temp from [3] - I have chosen 910. Please note this value (belonging to Grossman) did account for changes in temperature to some extent by using an effective specific heat capacity value, not a specific heat capacity value. 
- Initial temperature = 298K from assuming that the metal powder is initially is at room temperature 
- Melting temperature = 870K from [1] p.4 table 2.  | 867K from [3] - I have chosen 870K

### Depth equation variables - clean, however the choice for plate temperature and thermal diffusivity might need to be looked at. 
- Conductivity = 140 from [2] p.3 table 1 | 113+1.06\*(10^-5)\*current_temp from [3] - I chosen 140
- Solidus temperature (this is the temperature below which an alloy is completely solid, no liquid at all) = 830.15K from [2] p.3 table 1 - I have chosen 830.15K
- Plate temperature = 298K from assuming it's standard room temperature
- Heat of fusion (energy for converting 1kg solid to liquid) = 476500 from [2] p.3 table 1 | 5.03\*10^5 from [3] - I have chosen 476500
- Absorptivity of the metal = 0.32 from [2] p.3 table 1 | No Absorptivity yet from us, is minimum sbsorptivity the same? - I have chosen 0.32
- Thermal diffusivity = conductivity/(rho\*cp) (which is a standard equation) | 4.5\*10^-5 from [3] - I have decided to use the standard equation because while it is more proper to use an experimental value which is the theoretical naturally adjusted by unaccounted factors, there was no indication that a thermal diffusivity experimental value was used. I could be wrong and we could check.  
- Laser beam diameter = varies. It's typically 100 micrometres, 75 micrometres, 50 micrometres etc. on these machines 
- Melt pool depth coefficient = 5.9 from [2] p.4 table 4. (determined by Grossman et al. by experiments)

Probably irrelevant, but when I compare the current data to the old data it seems that the differences in values are in cp (major difference), conductivity (major), thermal diffusivity, sigma. 