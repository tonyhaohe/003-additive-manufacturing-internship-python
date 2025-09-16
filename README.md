# Grossman Melt Pool Modeller
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
![Last commit](https://img.shields.io/github/last-commit/tonyhaohe/grossman-melt-pool-modeller)
![Repo size](https://img.shields.io/github/repo-size/tonyhaohe/grossman-melt-pool-modeller)

## Table of Contents: 
- [About](#about)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Data for AlSi10Mg](#data-for-alsi10mg)
- [Support and Contributing](#support)
- [References](#references)

## About 
This project implements the Grossman et al. model and, when given experimental data, compares its predictions to the data. Researchers can assess their own models' performance against Grossman’s to improve laser powder bed fusion processes.
- `grossman_comparator.py` - Compares the Grossman model's predictions with actual experimental values.
- `grossman_heatmap.py` - Visualizes prediction errors as heatmaps for intuitive analysis.

### Independent Variables:
- Power (W)
- Speed (mm·s⁻¹)
- Laser beam diameter (µm)

### The Models Used: 
- Melt pool width: Grossman et al. [1], Eq. 7 (Not 11 since their calculated constant is used in these programs)
- Melt pool depth: Grossman et al. [2], Eq. 6 (also uses a constant they calculated)

## Installation 
```
# 1. Open a terminal (Command Prompt or PowerShell for Windows, Terminal for macOS or Linux)

# 2. Ensure Python and Git are installed
# Visit https://www.python.org to download and install Python (version 3.10 or higher)
# Visit https://git-scm.com to download and install console Git 

# 3. Clone the repository
git clone https://github.com/tonyhaohe/grossman-melt-pool-modeller.git

# 4. Navigate to the project directory
cd grossman-melt-pool-modeller

# 5. Create virtual environment and activate it 
python3 -m venv grossman-env
source grossman-env/bin/activate

# 6. Upgrade pip and install packages from requirements.txt
python -m pip install -U pip
pip install -r requirements.txt
```

## Quick Start 
### Compare Grossman predictions to experimental data
Run `python compare_pools.py`
To populate with dummy data, you can do: 
```bash
cat example_entry_dummymetal.txt - | python3 compare_pools.py
```
The `-` is vital, since it tells the shell to take user input after the text file is inputted. You will be able to use this inputted data with the heatmap. 

### Visualize error heatmaps
Run `python error_heatmap.py`
Please note that it will not be able to calculate anything and thus display nothing unless you input experimental data. 

### Data Storage
Data is stored in `data.json` using standard SI units (m, J, etc.).
- Structure:
    - Top-level keys: Metal names.
    - Values: Dictionaries containing variables for width and depth calculations.
    - Note: Current experiment data is dummy data, not actual experimental results.

### Key notes
- *Melt pool width* refers to maximum melt pool width, assuming a circular cross-section ([1], Fig. 3, p.4). Hence it refers to the width at the top of the melt pool.
- Laser diameter effect not deeply explored but can still be varied.

## Data for AlSi10Mg below: 
### Machine Power and Speed 
| Variable | Value Range | Interval |
|:-|:-|:-|
| Power (W) | 100–400 | 100 |
| Speed (mm·s⁻¹) | 750–2250 | 750 |

### Width Equation Variables
| Variable | Value | Source / Notes |
|:-|:-|:-|
| Proportionality constant (no units) | 0.49 | [1] Table 3 |
| Density (kgm⁻³) | 2670 | [1] Table 2 |
| Effective specific heat capacity (Jkg⁻¹K⁻¹) | 910 | [1] Table 2 (effective specific heat capacity doesn't account for temperature changes as opposed to specific heat capacity) |
| Initial temperature (K) | 298 | Assumed |
| Melting temperature (K) | 870 | [1] Table 2 |

### Depth Equation Variables
| Variable | Value | Source / Notes |
|:-|:-|:-|
| Conductivity (Wm⁻¹K⁻¹) | 140 | [2] Table 1 |
| Solidus temperature (K) | 830.15 | [2] Table 1 |
| Plate temperature (K) | 298 | Assumed |
| Heat of fusion (Jkg⁻¹) | 476500 | [2] Table 1 |
| Absorptivity | 0.32 | [2] Table 1 |
| Thermal diffusivity | k/(ρ×cp) | Standard formula |
| Laser beam diameter (μm) | 50–100 | Typical |
| Melt pool depth coefficient (μm) | 5.9 | [2] Table 4 |

## Support and Contributing 
If you find this project useful, consider starring ⭐ the repo! Contributions are welcome, if you'd like to improve this project:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit changes and push.
4. Open a pull request.

## References: 
1. Grossman et al. Melt pool controlled laser powder bed fusion for customised low-density lattice structures
   [DOI: 10.1016/j.matdes.2019.108054](https://doi.org/10.1016/j.matdes.2019.108054)
2. Grossman et al. Material and process invariant scaling laws to predict porosity of dense and lattice structures in laser powder bed fusion
   [DOI: 10.1016/j.matdes.2024.112684](https://doi.org/10.1016/j.matdes.2024.112684)