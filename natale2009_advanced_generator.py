# -*- coding: utf-8 -*-
"""
natale2009_advanced_generator.py

This script generates synthetic sleep diary data, *partially* based on group-level statistics
from Natale et al. (2009), separately for control and insomnia participants.

- - - - - - - - - -

It extends the original 'natale2009_based_synthetic_data_generator':
In addition to core sleep variables, supplementary sleep-related and habit-related features 
(SQ, Rested, Caffeine, Physical Activity, Medication) are included. 
These added features are *not* derived from Natale et al. (2009), but are simulated using 
plausible distributions to enrich the dataset.

Each mock participant is assigned a generic email address based on their identifier.

The original dataset (obtained by running natale2009_based_synthetic_data_generator.py) 
simulates 21 consecutive days per participant and includes variables such as:
    SOL, WASO, TST, SE, Lights Off, Sleep End, Out of Bed, TIB, and Sleep Midpoint.

*** This augmented version also introduces:
- A simulated date sequence starting in March 2024
- Additional subjective and behavioral diary variables (based on plausible distributions instead of real data, as described above)

These enhancements are designed for integration into the 'prepostpleep_studypipeline' project (under development).

The output is saved as Excel (.xlsx).

Author: Iris Vantieghem  
Created: July 2025  
License: MIT
"""


import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
from pathlib import Path
import json

base_path = Path(__file__).resolve().parent


def generate_time_series_sleepdata(parameter_path, output_path, days=21, n_participants=300, seed=42):
    
    """
    Generates synthetic time series sleep diary data based on Natale et al. (2009), with additional habit-related variables.
    
    Each mock participant is assigned a unique ID and email, and 21 consecutive days of diary entries are simulated.
    Core sleep variables (e.g., SOL, WASO, TST, SE) are based on group-level statistics from Natale et al. (2009).
    Supplementary variables (e.g., Caffeine, Rested, Medication) are added using plausible distributions.
    
    Gamma distributions model positively skewed variables (e.g., SOL, WASO), while clock-time 
    variables are drawn from normal distributions centered around realistic values.
    
    In addition to the main numeric dataset, the function also creates an alternate version containing
    a JSON-formatted sleep block per entry.
    
    Parameters:
    - parameter_path (str or Path): Excel file containing group-level sleep parameters.
    - output_path (str or Path): Path to save the primary .xlsx file with numeric and clock-format variables.
    - days (int, default=21): Number of simulated days per participant.
    - n_participants (int, default=300): Number of mock participants to generate.
    - seed (int, default=42): Seed value for reproducibility.
    
    Returns:
    - df (pd.DataFrame): The main DataFrame with numeric and clock-format variables.
      An additional Excel file is saved alongside the main output, including an extra column ('Sleep_JSON')
      with sleep details in JSON-like format.
    """

    np.random.seed(seed)

    df_params = pd.read_excel(parameter_path).set_index("Variable")

        
    # Convert various time formats to minutes past midnight. Allows negative values for evening times if specified.
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
    
    # LIGHTS OFF is treated as a potential evening value --> may become negative
    df_params.loc["Light Off", "Mean"] = convert_time_to_minutes(df_params.loc["Light Off", "Mean"], allow_negative=True)
    # SLEEP END must remain positive (e.g., 07:30 AM)
    df_params.loc["Sleep End", "Mean"] = convert_time_to_minutes(df_params.loc["Sleep End", "Mean"])
    
    # Convert SD's from Light Off and Sleep End from hours to minutes
    df_params.loc["Light Off", "SD"] *= 60
    df_params.loc["Sleep End", "SD"] *= 60

    # Retrieve mean and SD for a given variable from the parameter table
    def get_params(var):
        return float(df_params.loc[var, "Mean"]), float(df_params.loc[var, "SD"])

    records = []
    
    # Startdate for simulation (added for advanced generator)
    start_date = pd.to_datetime("2024-03-01")


    for pid in range(1, n_participants + 1):
        for day in range(1, days + 1):
            #record = {"Code": f"Mock_{pid:03d}", "Day": day}
            record = {
                "Participant": f"Mock_{pid:03d}",
                "Email": f"mock_{pid:03d}@example.test", # added for advanced generator
                "Day": (start_date + pd.Timedelta(days=day - 1)).strftime("%d/%m/%Y")
            }

            
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
            tib = out_of_bed_min - lights_off_min # Out of bed includes time between waking up & getting up
            record["TIB"] = tib
            
            # TWT
            twt = sol + waso
            record["TWT"] = twt
            
            # Total Sleep Time
            tst = tib - (sol + waso)
            record["TST"] = tst
                     
            # Sleep efficiency
            se = (tst / tib) * 100 if tib > 0 else np.nan
            record["SE"] = se
            
            # Midpoint of sleep based on lights_off and time of getting out of bed
            midpoint = (lights_off_min + out_of_bed_min) / 2 # Alternatively, (lights_off_min + sol) + out_of_bed_min
            record["Midpoint"] = midpoint
            
            # Simulated subjective and habit-related diary variables

            # Subjective Sleep Quality (1–10 scale)
            record["SQ"] = int(np.clip(np.round(np.random.normal(7, 1.5)), 1, 10))
            
            # Feeling Rested (1–10 scale)
            record["Rested"] = int(np.clip(np.round(np.random.normal(6.5, 1.8)), 1, 10))
            
            # Physical Activity (minutes/day)
            record["Physical_Activity_Minutes"] = int(np.clip(np.random.normal(50, 20), 0, 180))
            
            # Caffeine intake (cups per day)
            record["Caffeine"] = int(np.clip(np.random.poisson(1.2), 0, 6))
            
            # Medication (set to None)
            record["Medication"] = None
            
            # Time to calm down and relax before bed (in minutes)
            record["time to calm down and relax"] = int(np.clip(np.random.normal(45, 15), 0, 120))

            #######
            
            records.append(record)

    df = pd.DataFrame(records)

    # Add clock-format columns 
    for col in ["Lights_Off", "Sleep_End", "Midpoint"]:
        df[f"{col}_Clock"] = df[col].apply(lambda x: pd.to_datetime(x % (24 * 60), unit='m').strftime("%H:%M"))
    

    # Build JSON-like column to include sleep variables to create a more realistic excel output (e.g. export from a website) 
    def build_sleep_json(row):
        start_time = pd.to_datetime(row["Lights_Off"] % (24*60), unit='m').strftime("%H:%M")
        end_time = pd.to_datetime(row["Sleep_End"] % (24*60), unit='m').strftime("%H:%M")
        # sleep_in = int(round(row["SOL"]))
    
        json_data = {
            "start": start_time,
            "end": end_time,
            #"values": [],  # optional: include other time series into values
            "totals": {
                "sl": int(round(row["SOL"])),
                "wans": int(round(row["WASO"])),
                "twt": int(round(row["SOL"] + row["WASO"])),
                "tib": int(round(row["TIB"])),
                "tst": int(round(row["TST"])),
                "se": round(row["SE"], 1)
            }
        }
        return json.dumps(json_data)
    
    # Add JSON-like column to the dataframe
    df_with_json = df.copy()
    df_with_json["Sleep_JSON"] = df_with_json.apply(build_sleep_json, axis=1)
    
    # File 1: original data without JSON-like column
    df.to_excel(output_path, index=False)
    
    # # Prepare second file with JSON sleep block + non-sleep diary variables only
    sleep_vars = ["Out_of_Bed",	"Midpoint", "Lights_Off_Clock",	"Sleep_End_Clock", "Midpoint_Clock",
                  "Lights_Off", "Sleep_End", "SOL", "WASO", "TWT", "TIB", "TST", "SE"]
    df_json_only = df_with_json.drop(columns=sleep_vars)
    cols_order = [col for col in df_json_only.columns if col != "Sleep_JSON"] + ["Sleep_JSON"]
    df_json_only = df_json_only[cols_order]
    
    jsonblock_path = output_path.parent / f"{output_path.stem}_jsonblock_only{output_path.suffix}"
    df_json_only.to_excel(jsonblock_path, index=False)

    return df

# For standalone execution:
def main():
    parameter_path = base_path /"input/natale2009_control_group_sleep_main_parameters.xlsx"
    # parameter_path = base_path /"input/natale2009_insomnia_group_sleep_main_parameters.xlsx"

    output_path = base_path /"output/synthetic_sleepdata_timeseries_control_augmented.xlsx"
    # output_path = base_path /"output/synthetic_sleepdata_timeseries_insomnia_augmented.xlsx"
    generate_time_series_sleepdata(parameter_path, output_path)
    
    

if __name__ == "__main__":
    main()


