# synthetic_sleepdata_generator
This repository contains a Python script to generate synthetic sleep diary data ((SOL, WASO, TST, SE, etc.) based on the published summary statistics reported by Natale et al. (2009).
The original summary statistics have been derived from actigraphy data. Still, the current source was chosen because of the sample size being larger than usual and the clear information on which participants where included in the dataset. 
Although a bias may exist because actigraphy, for instance, usually underestimates the time it takes to fall asleep in comparison to subjective sleep diary entries, this source contains rich and reliable sleep data.

The generator simulates 21 days of sleep variables for a sample of mock participants, separately for insomnia and control groups. 
Distributions are defined using the published means and standard deviations, and synthetic time series are generated accordingly.

## Key features

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

- `natale2009_based_synthetic_data_generator.py`  
  Main Python script for generating the synthetic data

## How to use

1. Place the correct Excel parameter file in the `input/` folder.
2. Run the Python script. It will generate 21 days of synthetic sleep data for 100 mock participants.
3. The output will be saved in the `output/` folder.

You can adapt the number of participants or days by modifying the arguments in `generate_time_series_sleepdata()` inside the script.

Run with:
python natale2009_based_synthetic_data_generator.py

Note: Make sure to use Python 3 and have `pandas` and `openpyxl` installed.

## Reference

Natale V, Plazzi G, Martoni M. Actigraphy in the assessment of insomnia: a quantitative approach. Sleep. 2009 Jun;32(6):767-71. doi: 10.1093/sleep/32.6.767. PMID: 19544753; PMCID: PMC2690564.

## Author

Created by Iris Vantieghem – Contact: via GitHub profile

## License

This project is licensed under the MIT License – see LICENSE for details.

