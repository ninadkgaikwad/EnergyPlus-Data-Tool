# -*- coding: utf-8 -*-
"""
Created on Mon 20240617

@author: Kasey Dettlaff

"""

#This version has csv generation commented out, and was created to work on automation.
#Issue with generatiion of eio pickle file was resolved. 
#This version of the code adds code to delete EIO_Dict_Full and the csv files after generation is complete. 

# =============================================================================
# Import Required Modules
# =============================================================================

# External Modules
import os
import numpy as np
import pandas as pd
import scipy.io
import opyplus as op
import re
import shutil
import datetime
import pickle

# Custom Modules
    
# =============================================================================
# Get Location from Climate Zone
# =============================================================================
def climateZone_to_location(climateZone):
    
    location = 'Unknown'
    
    if climateZone == "CZ1AWH":
        location = "Miami"
    elif climateZone == "CZ1AWHT":
        location = "Honolulu"
    elif climateZone == "CZ1AWHTS":
        location = "Honolulu"
    elif climateZone == "CZ2AWH":
        location = "Tampa"
    elif climateZone == "CZ2B":
        location = "Tucson"
    elif climateZone == "CZ3A":
        location = "Atlanta"
    elif climateZone == "CZ3AWH":
        location = "Montgomery"
    elif climateZone == "CZ3B":
        location = "ElPaso"
    elif climateZone == "CZ3C":
        location = "SanDiego"
    elif climateZone == "CZ4A":
        location = "NewYork"
    elif climateZone == "CZ4B":
        location = "Albuquerque"
    elif climateZone == "CZ4C":
        location = "Seattle"
    elif climateZone == "CZ5A":
        location = "Buffalo"
    elif climateZone == "CZ5B":
        location = "Denver"
    elif climateZone == "CZ5C":
        location = "PortAngeles"
    elif climateZone == "CZ6A":
        location = "Rochester"
    elif climateZone == "CZ6B":
        location = "GreatFalls"
    elif climateZone == "CZ7":
        location = "InternationalFalls"
    elif climateZone == "CZ8":
        location = "Fairbanks"
        
    return location


# =============================================================================
# Get Simulation Name
# =============================================================================
def get_simulation_name(IDF_FileName):
    
    IDF_FileName = IDF_FileName.replace(".idf", "")
    
    # EnergyPlus Prototype Commercial
    # Naming Convention: Standard_Year_Location_BuildingType
    if IDF_FileName.startswith("ASHRAE"): 
        FileName_Split = IDF_FileName.split('_')
        Simulation_Name = "ASHRAE" + '_' + FileName_Split[2][3:] + '_' + FileName_Split[3] + '_' + FileName_Split[1]
    elif IDF_FileName.startswith("IECC"): 
        FileName_Split = IDF_FileName.split('_')
        Simulation_Name = "IECC" + '_' + FileName_Split[2][3:] + '_' + FileName_Split[3] + '_' + FileName_Split[1]
        
    # EnergyPlus Prototype Residential 
    # Naming Convention: Prototype_ClimateZone_Location_HeatingType_FoundationType_Standard_Year
    elif IDF_FileName.startswith("US"): 
        FileName_Split = IDF_FileName.split('+') 
        Simulation_Name = FileName_Split[1] + '_' + FileName_Split[2] + '_' + climateZone_to_location(FileName_Split[2]) + '_' + FileName_Split[3] + '_' + FileName_Split[4] + '_' + FileName_Split[5]

    # EnergyPlus Prototypes Manufactured
    # Naming Convention: Configuration_Location_ClimateZone_EnergyCode_HeatingType
    elif IDF_FileName.startswith("MS") or IDF_FileName.startswith("SS"):
        Simulation_Name = IDF_FileName
    
    else: Simulation_Name = IDF_FileName
    
    return Simulation_Name

# =============================================================================
# Create Text Files
# =============================================================================

generated_textfiles_folderpath = r"D:\Building_Modeling_Code\Code\EPW_DataGeneration\generated_textfiles"
IDF_filepathlist_textfile_path = os.path.join(generated_textfiles_folderpath, "IDF_filepathlist.txt")
weather_filepathlist_textfile_path = os.path.join(generated_textfiles_folderpath, "weather_filepathlist.txt")
simulationName_list_texfile_path = os.path.join(generated_textfiles_folderpath, "simulationName_filepathlist.txt")

IDF_filepathlist_textfile = open(IDF_filepathlist_textfile_path, 'w')
weather_filepathlist_textfile = open(weather_filepathlist_textfile_path, 'w')
simulationName_list_textfile = open(simulationName_list_texfile_path, 'w')

# =============================================================================
# Get List of Weather Files
# =============================================================================

data_folderpath = r"D:\Building_Modeling_Code\Data"

commercial_weatherfolderpath = os.path.join(data_folderpath, "TMY3_WeatherFiles_Commercial")
manufactured_weatherfolderpath = os.path.join(data_folderpath, "TMY3_WeatherFiles_Manufactured")
residential_weatherfolderpath = os.path.join(data_folderpath, "TMY3_WeatherFiles_Residential")

commercial_weatherfile_list = []
for filename in os.listdir(commercial_weatherfolderpath):
    filename = filename.replace('San.Diego', 'SanDiego')
    filename = filename.replace('International.Falls', 'InternationalFalls')
    filename = filename.replace('Great.Falls', 'GreatFalls')
    filename = filename.replace('New.York', 'NewYork')
    filename = filename.replace('El.Paso', 'ElPaso')
    filename = filename.replace('Port.Angeles', 'PortAngeles')
    commercial_weatherfile_list.append(os.path.basename(filename))
    
manufactured_weatherfile_list = []
for filename in os.listdir(manufactured_weatherfolderpath):
    filename = filename.replace('San.Francisco', 'SanFrancisco')
    filename = filename.replace('El.Paso', 'ElPaso')
    manufactured_weatherfile_list.append(os.path.basename(filename))
    
residential_weatherfile_list = []
for filename in os.listdir(residential_weatherfolderpath):
    filename = filename.replace('San.Diego', 'SanDiego')
    filename = filename.replace('International.Falls', 'InternationalFalls')
    filename = filename.replace('Great.Falls', 'GreatFalls')
    filename = filename.replace('New.York', 'NewYork')
    filename = filename.replace('El.Paso', 'ElPaso')
    filename = filename.replace('Port.Angeles', 'PortAngeles')
    residential_weatherfile_list.append(os.path.basename(filename))

# =============================================================================
# Write IDF and Weather Filepath List
# =============================================================================

commercial_idf_folderpath = os.path.join(data_folderpath, "Commercial_Prototypes")
manufactured_idf_folderpath = os.path.join(data_folderpath, "Manufactured_Prototypes")
residential_idf_folderpath = os.path.join(data_folderpath, "Residential_Prototypes")

# Commercial IDF Files
for standard_subfolder in os.listdir(commercial_idf_folderpath):
    standard_subfolder_path = os.path.join(commercial_idf_folderpath, standard_subfolder)
    for year_subfolder in os.listdir(standard_subfolder_path):
        year_subfolder_path = os.path.join(standard_subfolder_path, year_subfolder)
        for file in os.listdir(year_subfolder_path):
            if file.endswith(".idf"):
                simulation_name = get_simulation_name(os.path.basename(file))
                # Write corresponding simulation name
                simulation_location = simulation_name.split('_')[2]
                # Write corresponding weather filename
                found_weatherfile = 0
                for weatherfilename in commercial_weatherfile_list:
                    if simulation_location in weatherfilename: 
                        weather_filepathlist_textfile.write(weatherfilename + '\n')
                        found_weatherfile = 1    
                if found_weatherfile == 1:
                    IDF_filepathlist_textfile.write(os.path.basename(file) + '\n')
                    simulationName_list_textfile.write(simulation_name + '\n')
                else: print("Could not find weather file for location: " + simulation_location + '\n')
                
                        

# Manufactured IDF Files
for standard_subfolder in os.listdir(manufactured_idf_folderpath):
    standard_subfolder_path = os.path.join(manufactured_idf_folderpath, standard_subfolder)
    for location_subfolder in os.listdir(standard_subfolder_path):
        location_subfolder_path = os.path.join(standard_subfolder_path, location_subfolder)
        for file in os.listdir(location_subfolder_path):
            if file.endswith(".idf"):
                simulation_name = get_simulation_name(os.path.basename(file))
                # Write corresponding simulation name
                simulation_location = simulation_name.split('_')[1]
                # Write corresponding weather filename
                found_weatherfile = 0
                for weatherfilename in manufactured_weatherfile_list:
                    if simulation_location in weatherfilename: 
                        weather_filepathlist_textfile.write(weatherfilename + '\n')
                        found_weatherfile = 1    
                if found_weatherfile == 1:
                    IDF_filepathlist_textfile.write(os.path.basename(file) + '\n')
                    simulationName_list_textfile.write(simulation_name + '\n')
                else: print("Could not find weather file for location: " + simulation_location + '\n')
                
# Residential IDF Files
for standard_subfolder in os.listdir(residential_idf_folderpath):
    standard_subfolder_path = os.path.join(residential_idf_folderpath, standard_subfolder)
    for climateZone_subfolder in os.listdir(standard_subfolder_path):
        climateZone_subfolder_path = os.path.join(standard_subfolder_path, climateZone_subfolder)
        for file in os.listdir(climateZone_subfolder_path):
            if file.endswith(".idf"):
                simulation_name = get_simulation_name(os.path.basename(file))
                # Write corresponding simulation name
                simulation_location = simulation_name.split('_')[2]
                # Write corresponding weather filename
                found_weatherfile = 0
                for weatherfilename in residential_weatherfile_list:
                    if simulation_location in weatherfilename: 
                        weather_filepathlist_textfile.write(weatherfilename + '\n')
                        found_weatherfile = 1    
                if found_weatherfile == 1:
                    IDF_filepathlist_textfile.write(os.path.basename(file) + '\n')
                    simulationName_list_textfile.write(simulation_name + '\n')
                else: print("Could not find weather file for location: " + simulation_location + '\n')


# =============================================================================
# Close Text Files
# =============================================================================

IDF_filepathlist_textfile.close()
weather_filepathlist_textfile.close()
simulationName_list_textfile.close()

# Problem Location Names: 
# Commerical: SanDiego, 
# Manufactured: ElPaso, San.Francisco, 