# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 19:04:59 2022

This file will be an area for data preperation and any necessary cleaning.
After the methods of this file are ran, then the analysis can begin.

@author: Francisco Vazquez
"""
import pandas as pd
import os

def categorizeJUCO(filepath):
    career_data = pd.read_csv(filepath)
    
    juco_year = career_data.query("Lvl == 'NJCAA'")['Year'].values[0]
    try:
        ncaa_year = career_data.query("Lvl == 'NCAA-1'")['Year'].values[0]
    except IndexError:
        return pd.DataFrame(), "NA"
    
    if "AVG" in career_data.columns:
        juco_data = career_data.query("Lvl == 'NJCAA'").iloc[-1:,-33:]
        ncaa_data = career_data.query("Lvl == 'NCAA-1'").iloc[-1:,-33:]
        
        if juco_year > ncaa_year:
            print("Went to JUCO after D1")
            return pd.DataFrame(), "NA"
        
        juco_data = juco_data.add_prefix("juco_")
        ncaa_data = ncaa_data.add_prefix("ncaa_")
        
        combined_data = ncaa_data.join(juco_data,how="outer")
        combined_data.reset_index(inplace=True,drop=True)
        # print(combined_data)
        combined_data = pd.DataFrame(combined_data.loc[0].combine_first(combined_data.loc[1]))
        combined_data = combined_data.transpose()
        
        return combined_data, "Bat"
        
    if "ERA" in career_data.columns:
        juco_data = career_data.query("Lvl == 'NJCAA'").iloc[-1:,-28:]
        ncaa_data = career_data.query("Lvl == 'NCAA-1'").iloc[-1:,-28:]
        
        
        
        if juco_year > ncaa_year:
            print("Went to JUCO after D1")
            return pd.DataFrame(), "NA"
        
        juco_data = juco_data.add_prefix("juco_")
        ncaa_data = ncaa_data.add_prefix("ncaa_")
        
        combined_data = ncaa_data.join(juco_data,how="outer")
        combined_data.reset_index(inplace=True,drop=True)
        # print(combined_data)
        combined_data = pd.DataFrame(combined_data.loc[0].combine_first(combined_data.loc[1]))
        combined_data = combined_data.transpose()
        
        return combined_data, "Pit"

def parse_JUCO(folder_path):
    full_data_hit = pd.DataFrame()
    full_data_pitch = pd.DataFrame()
    for filename in os.listdir(folder_path):
        if filename == "desktop.ini":
            continue
        player_file_path = folder_path + "/" + filename
        print(player_file_path)
        
        player_data, cat = categorizeJUCO(player_file_path)
        if cat == "Bat":
            full_data_hit = full_data_hit.append(player_data)
        if cat == "Pit":
            full_data_pitch = full_data_pitch.append(player_data)
            
    return full_data_hit,full_data_pitch
        
   
    