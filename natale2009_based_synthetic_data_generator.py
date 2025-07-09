# -*- coding: utf-8 -*-
"""
natale2009_based_synthetic_data_generator.py

This script generates synthetic sleep diary time series data based on group-level statistics
from Natale et al. (2009), separately for control and insomnia participants.

The generated data simulate 21 consecutive days for each mock participant and include key
sleep variables such as SOL, WASO, TST, SE, Lights Off, Sleep End, Out of Bed, TIB, and Midpoint.
Gamma distributions are used for positively skewed variables (e.g., SOL, WASO), while clock-time
variables follow normal distributions centered around realistic means.

Outputs are saved as Excel (.xlsx) files in both numeric and human-readable clock formats.

Author: Iris Vantieghem
Created: July 2025
License: MIT
"""


import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
from pathlib import Path

base_path = Path(__file__).resolve().parent


def generate_time_series_sleepdata(parameter_path, output_path, days=21, n_participants=100, seed=42):
    
    """
    Generate synthetic time series sleep diary data based on summary statistics 
    (means and standard deviations) from Natale et al. (2009).

    This function simulates multiple sleep variables (e.g., SOL, WASO, TST, SE) for a given number 
    of mock participants over a specified number of days. Key variables like 'Lights Off' and 
    'Sleep End' are treated as clock times and include logic for handling values that cross midnight.

    Parameters:
    - parameter_path (str or Path): Path to the Excel file containing the summary statistics.
    - output_path (str or Path): Path where the generated .xlsx file will be saved.
    - days (int, default=21): Number of days to simulate for each participant.
    - n_participants (int, default=100): Number of mock participants to generate.
    - seed (int, default=42): Random seed for reproducibility.

    Returns:
    - df (pd.DataFrame): DataFrame containing the synthetic sleep data in numeric and clock format.
    """
    np.random.seed(seed)

    df_params = pd.read_excel(parameter_path).set_index("Variable")

        
        # Updated time conversion function
    def convert_time_to_minutes(val, allow_negative=False):
        if isinstance(val, (pd.Timestamp, datetime)):
            mins = val.hour * 60 + val.minute

        elif isinstance(val, time):
            mins = val.hour * 60 + val.minute

        elif isinstance(val, timedelta):
            return val.total_seconds() / 60

        elif isinstance(val, str):
            t = pd.to_datetime(val).time()
            mins = t.hour * 60 + t.minute

        elif isinstance(val, (int, float)):
            return val
        
        else:
            raise TypeError(f"Unexpected type: {type(val)}")
        
        if allow_negative and mins >= 1080: # 18*60 meaning after 6 pm! --> if after 6 pm: interpret this as 'the evening before'
            print("conversion going on: ", mins - 1440)
            return mins - 1440  # interpretes 23:30 as -30
        return mins
    
    # LIGHTS OFF is treated as a potential evening value → may become negative
    df_params.loc["Light Off", "Mean"] = convert_time_to_minutes(df_params.loc["Light Off", "Mean"], allow_negative=True)
    # SLEEP END must remain positive (e.g., 07:30 AM)
    df_params.loc["Sleep End", "Mean"] = convert_time_to_minutes(df_params.loc["Sleep End", "Mean"])
    
    # Convert SD's from Light Off and Sleep End from hours to minutes
    df_params.loc["Light Off", "SD"] *= 60
    df_params.loc["Sleep End", "SD"] *= 60


    def get_params(var):
        return float(df_params.loc[var, "Mean"]), float(df_params.loc[var, "SD"])

    records = []

    for pid in range(1, n_participants + 1):
        for day in range(1, days + 1):
            record = {"Code": f"Mock_{pid:03d}", "Day": day}
            
            # Generated sleep parameters:
            
            
            # Lights off (based on mean, SD from Natale et al., 2009)    
            mu_loff, sd_loff = get_params("Light Off")
            lights_off_min = np.random.normal(mu_loff, sd_loff)
            record["Lights_Off"] = lights_off_min
            
            # Sleep End (based on mean, SD from Natale et al., 2009) 
            mu_send, sd_send = get_params("Sleep End")
            sleep_end_min = np.random.normal(mu_send, sd_send)
            record["Sleep_End"] = sleep_end_min
            
            # Sleep Onset Latency (based on mean, SD from Natale et al., 2009) 
            mu_sol, sd_sol = get_params("SOL")
            shape_sol = (mu_sol / sd_sol) ** 2
            scale_sol = sd_sol ** 2 / mu_sol
            sol = np.random.gamma(shape_sol, scale_sol)
            record["SOL"] = sol
            
            # Wake After Sleep Onset (based on mean, SD from Natale et al., 2009)
            mu_waso, sd_waso = get_params("WASO")
            shape_waso = (mu_waso / sd_waso) ** 2
            scale_waso = sd_waso ** 2 / mu_waso
            waso = np.random.gamma(shape_waso, scale_waso)
            record["WASO"] = waso
            
            # Derived sleep parameters:
            
            # Time between waking up and getting out of bed
            wait_time = np.clip(np.random.normal(15, 10), 5, 30)
            out_of_bed_min = sleep_end_min + wait_time
            record["Out_of_Bed"] = out_of_bed_min
            # Time in bed
            tib = out_of_bed_min - lights_off_min
            record["TIB"] = tib
            # Total Sleep Time
            tst = tib - (sol + waso)
            record["TST"] = tst
            # Sleep efficiency
            se = (tst / tib) * 100 if tib > 0 else np.nan
            record["SE"] = se
            # Midpoint of sleep based on lights_off
            midpoint = (lights_off_min + sleep_end_min) / 2 # Alternatively, (lights_off_min + sol) + sleep_end_min
            record["Midpoint"] = midpoint

            records.append(record)

    df = pd.DataFrame(records)

    # Add clock-format columns for readability
    for col in ["Lights_Off", "Sleep_End", "Midpoint"]:
        df[f"{col}_Clock"] = df[col].apply(lambda x: pd.to_datetime(x % (24 * 60), unit='m').strftime("%H:%M"))

    df.to_excel(output_path, index=False)
    return df

# For standalone execution:
def main():
    parameter_path = base_path /"input/natale2009_control_group_sleep_main_parameters.xlsx"
    # parameter_path = base_path /"input/natale2009_insomnia_group_sleep_main_parameters.xlsx"

    output_path = base_path /"output/synthetic_sleepdata_timeseries_control_gamma_clock.xlsx"
    # output_path = base_path /"output/synthetic_sleepdata_timeseries_insomnia_gamma_clock.xlsx"
    generate_time_series_sleepdata(parameter_path, output_path)

if __name__ == "__main__":
    main()


