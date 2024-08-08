# -*- coding: utf-8 -*-
"""
Created on Fri 20240614

@author: Kasey Dettlaff, Ninad Gaikwad

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
# Simulate Building
# =============================================================================

# Inputs:
# IDF Filepath
# Weather Filepath
# Results FolderPath - Path to 'Processed_BuildingSim_Data'

def simulate_building(IDF_FilePath, Weather_FilePath, Special_IDFFile_Path, Simulation_Name, IDF_FileYear, Simulation_VariableNames, Sim_Start_Day, Sim_Start_Month, Sim_End_Day, Sim_End_Month, Sim_OutputVariable_ReportingFrequency, Sim_TimeStep, Results_FolderPath):
    
    IDF_FileName = os.path.basename(IDF_FilePath)
    Weather_FileName = os.path.basename(Weather_FilePath)
    
    # =============================================================================
    # Copying IDF and Weather Files to Temporary Folder
    # =============================================================================

    # Getting Temporary Folder Path
    Temporary_FolderPath = r"D:\Building_Modeling_Code\Results\TemporaryFolder"
    
    # Getting Temporary IDF/Weather File Paths
    Temporary_IDF_FilePath = os.path.join(Temporary_FolderPath, IDF_FileName)
    Temporary_Weather_FilePath = os.path.join(Temporary_FolderPath, Weather_FileName)
    
    shutil.copy(IDF_FilePath, Temporary_IDF_FilePath)
    shutil.copy(Weather_FilePath, Temporary_Weather_FilePath)

    # =============================================================================
    # Editing Saving Current IDF File and Saving Weather File in Results Folder
    # =============================================================================

    # Loading Current IDF File
    Current_IDFFile = op.Epm.load(Temporary_IDF_FilePath)

    # Editing RunPeriod
    Current_IDF_RunPeriod = Current_IDFFile.RunPeriod.one()

    Current_IDF_RunPeriod['begin_day_of_month'] = Sim_Start_Day

    Current_IDF_RunPeriod['begin_month'] = Sim_Start_Month

    Current_IDF_RunPeriod['end_day_of_month'] = Sim_End_Day

    Current_IDF_RunPeriod['end_month' ]= Sim_End_Month

    # Editing TimeStep
    Current_IDF_TimeStep = Current_IDFFile.TimeStep.one()

    Current_IDF_TimeStep['number_of_timesteps_per_hour'] = int(60/Sim_TimeStep)

    # Getting Current Schedule
    Current_ScheduleCompact = Current_IDFFile.Schedule_Compact

    Current_ScheduleCompact_Records_Dict = Current_ScheduleCompact._records

    # Creating Edited IDF File
    Edited_IDFFile = Current_IDFFile

    # Making Additional Folders

    Sim_IDFWeatherFiles_FolderName = 'Sim_IDFWeatherFiles'

    Sim_OutputFiles_FolderName = 'Sim_OutputFiles'

    Sim_IDFProcessedData_FolderName = 'Sim_ProcessedData'

    # Checking if Folders Exist if not create Folders
    if (os.path.isdir(os.path.join(Results_FolderPath, Simulation_Name))):

        # Folders Exist    
        z = None
                    
    else:
                    
        os.mkdir(os.path.join(Results_FolderPath, Simulation_Name))
                    
        os.mkdir(os.path.join(Results_FolderPath, Simulation_Name, Sim_IDFWeatherFiles_FolderName))
                    
        os.mkdir(os.path.join(Results_FolderPath, Simulation_Name, Sim_OutputFiles_FolderName))
                    
        os.mkdir(os.path.join(Results_FolderPath, Simulation_Name, Sim_IDFProcessedData_FolderName))

    # Saving Edited IDF and Weather File in Results Folder
    Edited_IDFFile_FolderPath = os.path.join(Results_FolderPath, Simulation_Name,  Sim_IDFWeatherFiles_FolderName)

    Edited_IDFFile.save(os.path.join(Edited_IDFFile_FolderPath, "Edited_IDFFile.idf"))

    shutil.copy(Weather_FilePath, Edited_IDFFile_FolderPath)    
             
    # =============================================================================
    # Running Edited IDF File to get Output Variables and saving in Results Folder
    # =============================================================================

    # Getting Folder Paths
    Edited_IDFFile_Path = os.path.join(Edited_IDFFile_FolderPath, "Edited_IDFFile.idf")

    Edited_WeatherFile_Path = os.path.join(Edited_IDFFile_FolderPath, Weather_FileName)

    Sim_OutputFiles_FolderPath = os.path.join(Results_FolderPath, Simulation_Name, Sim_OutputFiles_FolderName)

    Sim_IDFProcessedData_FolderPath = os.path.join(Results_FolderPath, Simulation_Name, Sim_IDFProcessedData_FolderName)

    # Appending Special IDF File into Edited IDF File
    IDF_From = open(Special_IDFFile_Path, "r")
    IDF_To = open(Edited_IDFFile_Path, "a")

    Data = IDF_From.read()
    IDF_To.write("\n")
    IDF_To.write(Data)

    IDF_From.close()
    IDF_To.close()

    # Loading the Edited IDF File
    epm_Edited_IDFFile = op.Epm.load(Edited_IDFFile_Path)

    # Loading the Special IDF File
    epm_Special_IDFFile = op.Epm.load(Special_IDFFile_Path)

    # Getting Output Variable from Edited IDF File
    OutputVariable_QuerySet = epm_Edited_IDFFile.Output_Variable.one()

    for OutputVariable_Name in Simulation_VariableNames:


        New_OutputVariable_FileName = OutputVariable_Name.replace(' ','_') + '.csv'
        
        if New_OutputVariable_FileName in os.listdir(Sim_IDFProcessedData_FolderPath):
            
            print("Output Variable " + OutputVariable_Name + " Already Simulated\n")
        
        else:

            # Updating OutputVariable_QuerySet in the Special IDF File

            print("---------- Simulating Output Variable: ", OutputVariable_Name)
            print("\n")

            OutputVariable_QuerySet['key_value'] = '*'

            OutputVariable_QuerySet['reporting_frequency'] = Sim_OutputVariable_ReportingFrequency

            OutputVariable_QuerySet['variable_name'] = OutputVariable_Name

            # Saving Special IDF File
            epm_Edited_IDFFile.save(os.path.join(Edited_IDFFile_FolderPath, "Edited_IDFFile.idf"))

            # Running Building Simulation to obtain current output variable
            op.simulate(Edited_IDFFile_Path, Edited_WeatherFile_Path, base_dir_path = Sim_OutputFiles_FolderPath)

            # Moving Output Variable CSV file to Desired Folder
            try:

                Current_CSV_FilePath = os.path.join(Sim_OutputFiles_FolderPath, "eplusout.csv")            

                MoveTo_CSV_FilePath = os.path.join(Sim_IDFProcessedData_FolderPath, New_OutputVariable_FileName)

                shutil.move(Current_CSV_FilePath, MoveTo_CSV_FilePath)

            except:

                continue 
        
        # =============================================================================
        # Convert and Save Output Variables .csv to.mat in Results Folder
        # =============================================================================    

        # Getting all .csv Files paths from Sim_IDFProcessedData_FolderPath
        FileName_List = os.listdir(Sim_IDFProcessedData_FolderPath)

        # Initializing CSV_FileName_List
        CSV_FilePath_List = []

        # FOR LOOP: For each file in Sim_IDFProcessedData_FolderPath
        for file in FileName_List:
                    
            # Check only .csv files 
            if file.endswith('.csv'):
                        
                # Appending .csv file paths to CSV_FilePath_List
                CSV_FilePath_List.append(os.path.join(Sim_IDFProcessedData_FolderPath,file))

        # Initializing IDF_OutputVariable_Dict
        IDF_OutputVariable_Dict = {}

        IDF_OutputVariable_Full_Dict = {}

        IDF_OutputVariable_Full_DF = pd.DataFrame()

        IDF_OutputVariable_ColumnName_List = []

        Counter_OutputVariable = 0

        # FOR LOOP: For Each .csv File in CSV_FilePath_List
        for file_path in CSV_FilePath_List:
                    
            # Reading .csv file in dataframe
            Current_DF = pd.read_csv(file_path)

            # Getting CurrentDF_1
            if (Counter_OutputVariable == 0):
                        
                # Keeping DateTime Column
                Current_DF_1 = Current_DF
                        
            else:
                        
                # Dropping DateTime Column
                Current_DF_1=Current_DF.drop(Current_DF.columns[[0]],axis=1)
                            
            # Concatenating IDF_OutputVariable_Full_DF
            IDF_OutputVariable_Full_DF = pd.concat([IDF_OutputVariable_Full_DF,Current_DF_1], axis="columns")
                    
            # Appending Column Names to IDF_OutputVariable_ColumnName_List
            for ColumnName in Current_DF_1.columns:
                        
                IDF_OutputVariable_ColumnName_List.append(ColumnName)
                        
            # Getting File Name
            FileName = file_path.split('\\')[-1].split('_.')[0]
                    
            # Storing Current_DF in IDF_OutputVariable_Dict
            IDF_OutputVariable_Dict[FileName] = Current_DF
                    
            # Incrementing Counter_OutputVariable
            Counter_OutputVariable = Counter_OutputVariable + 1

        # Creating and saving DateTime to IDF_OutputVariable_Dict
        DateTime_List = []

        DateTime_Column = Current_DF['Date/Time']

        Datetime_counter = 0

        for DateTime in DateTime_Column:
                        
            Datetime_counter += 1

        print("Datetime Column: " + str(Datetime_counter))
        print("\n")
                        
        DateTime_Split = DateTime.split(' ')

        if(len(DateTime_Split) == 4): 

            Date_Split = DateTime_Split[1].split('/')
                            
            Time_Split = DateTime_Split[3].split(':')
                    
        elif(len(DateTime_Split) == 3):

            Date_Split = DateTime_Split[0].split('/')
                        
            Time_Split = DateTime_Split[2].split(':')

        elif(len(DateTime_Split) == 2):
                            
            Date_Split = DateTime_Split[0].split('/')
                        
            Time_Split = DateTime_Split[1].split(':')

        # Converting all 24th hour to 0th hour as hour must be in 0..23
        if int(Time_Split[0]) == 24:
            Time_Split[0] = 00
                        
        DateTime_List.append(datetime.datetime(IDF_FileYear,int(Date_Split[0]),int(Date_Split[1]),int(Time_Split[0]),int(Time_Split[1]),int(Time_Split[2])))

        IDF_OutputVariable_Dict['DateTime_List'] = DateTime_List

        IDF_OutputVariable_Full_Dict['IDF_OutputVariable_Full_DF'] = IDF_OutputVariable_Full_DF

        IDF_OutputVariable_Full_Dict['DateTime_List'] = DateTime_List

        pickle.dump(IDF_OutputVariable_Dict, open(os.path.join(Sim_IDFProcessedData_FolderPath,"IDF_OutputVariables_DictDF.pickle"), "wb"))

        # Writing and Saving Column Names to a Text Files
        textfile = open(os.path.join(Sim_IDFProcessedData_FolderPath,"IDF_OutputVariable_ColumnName_List.txt"), "w")

        for ColumnName in IDF_OutputVariable_ColumnName_List:    
                    
            textfile.write(ColumnName + "\n")
                    
        textfile.close()
        
    # =============================================================================
    # Process .eio Output File and save in Results Folder
    # =============================================================================    

    # Reading .eio Output File
    Eio_OutputFile_Path = os.path.join(Sim_OutputFiles_FolderPath,'eplusout.eio') 

    # Initializing Eio_OutputFile_Dict
    Eio_OutputFile_Dict = {}

    with open(Eio_OutputFile_Path) as f:
        Eio_OutputFile_Lines = f.readlines()

    # Removing Intro Lines
    Eio_OutputFile_Lines = Eio_OutputFile_Lines[1:]

    Category_Key = ""
    Category_Key_List = ["Zone Information", "Zone Internal Gains Nominal", "People Internal Gains Nominal", "Lights Internal Gains Nominal", "ElectricEquipment Internal Gains Nominal", "GasEquipment Internal Gains Nominal", "HotWaterEquipment Internal Gains Nominal", "SteamEquipment Internal Gains Nominal", "OtherEquipment Internal Gains Nominal" ]
    Is_Table_Header = 0

    # Counting number of EIO file tables
    eiotable_count = 0

    # FOR LOOP: For each category in .eio File
    for Line_1 in Eio_OutputFile_Lines:

        #Check if Line contains table Header
        for Item in Category_Key_List:
            Category_Key = Item
            if ((Line_1.find(Item) >= 0) and (Line_1.find('!') >= 0)):
                Is_Table_Header = 1
                break 
            else:
                Is_Table_Header = 0
                        
        # IF ELSE LOOP: To check category
        # Code inside this if/else did not change meaningfully.
        if (Is_Table_Header > 0):
                        
            print("EIO Table: ", Category_Key)
            print("\n")
            #print(Line_1 + '\n')

            eiotable_count += 1
            print("Eio Tables: ", eiotable_count, "/9")
            print("\n")

            # Get the Column Names for the .eio File category
            DF_ColumnName_List = Line_1.split(',')[1:]

            # Removing the '\n From the Last Name
            DF_ColumnName_List[-1] = DF_ColumnName_List[-1].split('\n')[0]

            # Removing Empty Element
            if DF_ColumnName_List[-1] == ' ':
                DF_ColumnName_List = DF_ColumnName_List[:-1]

            # Initializing DF_Index_List
            DF_Index_List = []

            # Initializing DF_Data_List
            DF_Data_List = []

            # FOR LOOP: For all elements of current .eio File category
            for Line_2 in Eio_OutputFile_Lines:

                # IF ELSE LOOP: To check data row belongs to current Category
                if ((Line_2.find('!') == -1) and (Line_2.find(Category_Key) >= 0)):

                    #print(Line_2 + '\n')

                    DF_ColumnName_List_Length = len(DF_ColumnName_List)

                    # Split Line_2
                    Line_2_Split = Line_2.split(',')

                    # Removing the '\n From the Last Data
                    Line_2_Split[-1] = Line_2_Split[-1].split('\n')[0]

                    # Removing Empty Element
                    if Line_2_Split[-1] == ' ':
                        Line_2_Split = Line_2_Split[:-1]

                    # Getting DF_Index_List element
                    DF_Index_List.append(Line_2_Split[0])

                    Length_Line2 = len(Line_2_Split[1:])

                    Line_2_Split_1 = Line_2_Split[1:]

                    # Filling up Empty Column
                    if Length_Line2 < DF_ColumnName_List_Length:
                        Len_Difference = DF_ColumnName_List_Length - Length_Line2

                        for ii in range(Len_Difference):
                            Line_2_Split_1.append('NA')

                        # Getting DF_Data_List element
                        DF_Data_List.append(Line_2_Split_1)

                    else:
                        # Getting DF_Data_List element
                        DF_Data_List.append(Line_2_Split[1:])

                else:

                    continue

            # Creating DF_Table
            DF_Table = pd.DataFrame(DF_Data_List, index=DF_Index_List, columns=DF_ColumnName_List)

            # Adding DF_Table to the Eio_OutputFile_Dict
            Eio_OutputFile_Dict[Category_Key] = DF_Table

        else:

            continue
                    
    # Saving Eio_OutputFile_Dict as a .pickle File in Results Folder
    pickle.dump(Eio_OutputFile_Dict, open(os.path.join(Sim_IDFProcessedData_FolderPath,"Eio_OutputFile.pickle"), "wb"))

    # =============================================================================
    # Deleting all files from Temporary Folder
    # =============================================================================    

    # Deleting all files and sub-folders in Temporary Folder
    for files in os.listdir(Temporary_FolderPath):
                    
        path = os.path.join(Temporary_FolderPath, files)
                    
        try:
                        
            shutil.rmtree(path)
                        
        except OSError:
                        
            os.remove(path)

    # =============================================================================
    # Deleting CSV's
    # =============================================================================   
                
    # FOR LOOP: For Each .csv File in CSV_FilePath_List
    for file_path in CSV_FilePath_List:
        os.remove(file_path)

# =============================================================================
# Test
# =============================================================================

IDF_FilePath = r"D:\Building_Modeling_Code\Data\Commercial_Prototypes\ASHRAE\90_1_2013\ASHRAE901_ApartmentHighRise_STD2013_Albuquerque.idf"
Weather_FilePath = r"D:\Building_Modeling_Code\Data\TMY3_WeatherFiles_Commercial\USA_NM_Albuquerque.Intl.Sunport.723650_TMY3.epw"

# =============================================================================
# Read Input Textfiles
# =============================================================================

IDF_textfile_path = r"D:\Building_Modeling_Code\Code\EPW_DataGeneration\generated_textfiles\IDF_filepathlist.txt"
weather_textfile_path = r"D:\Building_Modeling_Code\Code\EPW_DataGeneration\generated_textfiles\weather_filepathlist.txt"
simulationName_textfile_path = r"D:\Building_Modeling_Code\Code\EPW_DataGeneration\generated_textfiles\simulationName_filepathlist.txt"
skipsimulation_textfile_path = r"D:\Building_Modeling_Code\Code\EPW_DataGeneration\generated_textfiles\skip_simulations.txt"

IDF_textfile = open(IDF_textfile_path, 'r')
Weather_textfile = open(weather_textfile_path, 'r')
simulationName_textfile = open(simulationName_textfile_path, 'r')
skipsimulation_textfile = open(skipsimulation_textfile_path, 'r')

# Assume textfiles are ordered correctly so that the nth element in one textfile corresponds with the nth element in the other textfiles
IDF_filepath_list = IDF_textfile.readlines()
weather_filepath_list = Weather_textfile.readlines()
simulationName_list = simulationName_textfile.readlines() 
skipsimulation_list = skipsimulation_textfile.readlines()

# Check Input Textfiles all have the same number of elements. 
length = len(IDF_filepath_list)
if all(len(lst) == length for lst in [weather_filepath_list, simulationName_list]):
    input_textfiles_good = 1
else: input_textfiles_good = 0

# =============================================================================
# Write output Textfiles
# =============================================================================

completed_simulation_folderpaths_textfile_path = r"D:\Building_Modeling_Code\Code\EPW_DataGeneration\generated_textfiles\completed_simulations.txt" # User Input
completed_simulation_folderpaths_textfile = open(completed_simulation_folderpaths_textfile_path, "r+") # Appending to completed simulations list, not overwriting.

# =============================================================================
# Other User Inputs 
# =============================================================================

Special_IDFFile_Path = r"D:\Building_Modeling_Code\Data\Special.idf"
IDF_FileYear = 2013
Sim_Start_Day = 1
Sim_Start_Month = 1
Sim_End_Day = 31
Sim_End_Month = 12
Sim_OutputVariable_ReportingFrequency = 'timestep'
Sim_TimeStep = 5
Results_FolderPath = r"F:\Processed_BuildingSim_Data" # Storing New Generated Data in F Drive 
Simulation_VariableNames = ['Schedule Value',
                                  'Facility Total HVAC Electric Demand Power',
                                  'Site Diffuse Solar Radiation Rate per Area',
                                  'Site Direct Solar Radiation Rate per Area',
                                  'Site Outdoor Air Drybulb Temperature',
                                  'Site Solar Altitude Angle',
                                  'Surface Inside Face Internal Gains Radiation Heat Gain Rate',
                                  'Surface Inside Face Lights Radiation Heat Gain Rate',
                                  'Surface Inside Face Solar Radiation Heat Gain Rate',
                                  'Surface Inside Face Temperature',
                                  'Zone Windows Total Transmitted Solar Radiation Rate',
                                  'Zone Air Temperature',
                                  'Zone People Convective Heating Rate',
                                  'Zone Lights Convective Heating_Rate',
                                  'Zone Electric Equipment Convective Heating Rate',
                                  'Zone Gas Equipment Convective Heating Rate',
                                  'Zone Other Equipment Convective Heating Rate',
                                  'Zone Hot Water Equipment Convective Heating Rate',
                                  'Zone Steam Equipment Convective Heating Rate',
                                  'Zone People Radiant Heating Rate',
                                  'Zone Lights Radiant Heating Rate',
                                  'Zone Electric Equipment Radiant Heating Rate',
                                  'Zone Gas Equipment Radiant Heating Rate',
                                  'Zone Other Equipment Radiant Heating Rate',
                                  'Zone Hot Water Equipment Radiant Heating Rate',
                                  'Zone Steam Equipment Radiant Heating Rate',
                                  'Zone Lights Visible Radiation Heating Rate',
                                  'Zone Total Internal Convective Heating Rate',
                                  'Zone Total Internal Radiant Heating Rate',
                                  'Zone Total Internal Total Heating Rate',
                                  'Zone Total Internal Visible Radiation Heating Rate',
                                  'Zone Air System Sensible Cooling Rate',
                                  'Zone Air System Sensible Heating Rate',
                                  'System Node Temperature',
                                  'System Node Mass Flow Rate']

i = 0
completed_simulation_folderpaths = completed_simulation_folderpaths_textfile.readlines()
completed_simulation_folderpaths_textfile.close()

for IDF_filepath in IDF_filepath_list:
    
    weather_filepath = weather_filepath_list[i]
    Simulation_Name = (simulationName_list[i]).rstrip()
    i += 1
    
    # Check if Simulation has already been completed or is marked to be skipped
    simulation_result_folderpath = os.path.join(Results_FolderPath, Simulation_Name)
    run_simulation = 1
    
    for line in completed_simulation_folderpaths:
        if os.path.basename(simulation_result_folderpath) == os.path.basename(line.rstrip()):
            run_simulation = 0
            print("Simulation Already Completed: " + Simulation_Name + "\n")
    
    for line in skipsimulation_list:
        if Simulation_Name == line.rstrip():
            run_simulation = 0
            print("Skip Simulation: " + Simulation_Name + "\n")
            
    if run_simulation == 1: 
        print("Running Simulation: " + Simulation_Name + "\n")
        simulate_building(IDF_FilePath, Weather_FilePath, Special_IDFFile_Path, Simulation_Name, IDF_FileYear, Simulation_VariableNames, Sim_Start_Day, Sim_Start_Month, Sim_End_Day, Sim_End_Month, Sim_OutputVariable_ReportingFrequency, Sim_TimeStep, Results_FolderPath)
        # Write to Output Textfile
        with open(completed_simulation_folderpaths_textfile_path, 'a') as file:
            file.write('\n' + simulation_result_folderpath)
    
    
#IDF_FilePath, Weather_FilePath, Special_IDFFile_Path, Simulation_Name, IDF_FileYear, Simulation_VariableNames, Sim_Start_Day, Sim_Start_Month, Sim_End_Day, Sim_End_Month, Sim_OutputVariable_ReportingFrequency, Sim_TimeStep, Results_FolderPath
    
# =============================================================================
# To Do
# =============================================================================

# Add code to add completed simulations to a txt file. 

# Add textfile for durations of simulation YYYYMMDD - YYYYMMDD

# Add more checks for valid input files - never hurts    

# Add skip simulation textfile    

# We are missing Denver Apartment High Rise            