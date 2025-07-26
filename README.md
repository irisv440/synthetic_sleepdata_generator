# synthetic_sleepdata_generator

This repository provides Python scripts to generate synthetic sleep diary data (partially) based on group-level statistics from Natale et al. (2009).  
The generated datasets include core sleep variables such as SOL, WASO, TST, SE, and more.

The original parameters are derived from actigraphy data. Although actigraphy tends to underestimate sleep onset latency (SOL) compared to subjective sleep diaries, this source was chosen for its unusually large sample size and clear inclusion criteria.

Two generator scripts are available:
- A **basic** generator (`natale2009_based_synthetic_data_generator.py`) that simulates the core sleep variables.
- An **advanced** generator (`natale2009_advanced_generator.py`) that also adds mock email addresses, dates, and habit-related diary variables.
Note that the supplementary variables included in the advanced generator are not based on Natale et al. (2009). 
Unlike the core sleep variables, no distinction between control and insomnia groups is currently implemented for these additional features, though this may be added in a future version.

Both scripts simulate 21 days of data for each mock participant, separately for control and insomnia groups.

## Features

- Generated variables include SOL, WASO, TST, SE, Lights Off, Sleep End, Out of Bed, Midpoint, and TIB
- Gamma distributions for usually positively skewed variables (e.g. SOL, WASO)
- Normally distributed clock times for variables like Lights Off and Sleep End
- Output is saved as `.xlsx` files with both numeric and clock-time formats
- No sensitive data used – safe for demonstration or development

## Project structure

- `input/`  
  Contains the Excel parameter files for the control and insomnia groups:
  - `natale2009_control_group_sleep_main_parameters.xlsx`
  - `natale2009_insomnia_group_sleep_main_parameters.xlsx`

- `output/`  
  Output folder where the generated `.xlsx` files are saved:
  - `synthetic_sleepdata_timeseries_control_gamma_clock.xlsx`
  - `synthetic_sleepdata_timeseries_insomnia_gamma_clock.xlsx`
  Output of the 'advanced' generator:
  - `synthetic_sleepdata_timeseries_control_augmented_jsonblock_only.xlsx`
  - `synthetic_sleepdata_timeseries_control_augmented.xlsx`

- `natale2009_based_synthetic_data_generator.py`  
  Main Python script for generating the synthetic data ('basic' generator for main sleep variables)
- `natale2009_advanced_generator.py`  
  Python script for generating 'enriched' synthetic data (includes also mock emailadresses, a date column, behavioral data and habit data)

## How to use

1. Place the correct Excel parameter file in the `input/` folder or use the examples already present.
2. Run the Python script of your choice. Use `natale2009_based_synthetic_data_generator.py` if you want to generate main sleep variables only, use
  `natale2009_advanced_generator.py` if you want a dataset including behavioral and habit data, emailadresses and a date column. 
   Both of them will generate 21 days of synthetic data.
3. The output will be saved in the `output/` folder.

You can adapt the number of participants or days by modifying the arguments in `generate_time_series_sleepdata()` inside the script.

Run with:
python natale2009_based_synthetic_data_generator.py
or
natale2009_advanced_generator.py

Note: Make sure you're using Python 3, with the following packages available: pandas, openpyxl (external), and json (built-in).


## Reference

Natale V, Plazzi G, Martoni M. Actigraphy in the assessment of insomnia: a quantitative approach. Sleep. 2009 Jun;32(6):767-71. doi: 10.1093/sleep/32.6.767. PMID: 19544753; PMCID: PMC2690564.

## Author

Created by Iris Vantieghem – Contact: via GitHub profile

## License

This project is licensed under the MIT License – see LICENSE for details.

