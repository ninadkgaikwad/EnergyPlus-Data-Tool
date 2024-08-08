import os
import pickle
import psycopg2
from psycopg2 import sql
import pandas as pd
import dateutil
from dateutil.parser import isoparse

# =============================================================================
# Link Building ID to Pickle Filepath
# =============================================================================
# Tested - Works

def get_pickle_filepaths(completed_simulations_txt_filepath, conn):
    
    cursor = conn.cursor()

    # Get list of filepath to results for each completed simulation
    completed_simulations_txt = open(completed_simulations_txt_filepath, 'r')
    completed_simulation_filepaths = completed_simulations_txt.readlines()
    
    # Iterate through each row in the buildingids table
    cursor.execute("SELECT * FROM buildingids")
    print("Fetching From Building IDS Table\n")
    building_rows = cursor.fetchall()
    print("Fetching Complete\n")
    
    pickle_filepaths = {}  # Use a dictionary to store file paths by building ID
    
    for building_info in building_rows:

        print("Finding Pickle Filepath for Building ID: " + str(building_info[0]))
        
        building_id = building_info[0]
        
        buildingcategory = building_info[1]
        buildingtype = building_info[2]
        buildingstandard = building_info[3]
        buildingstandardyear = building_info[4]
        buildinglocation = building_info[5]
        buildingheatingtype = building_info[6]
        buildingfoundationtype = building_info[7]
        buildingclimatezone = building_info[8]
        buildingprototype = building_info[9]
        buildingconfiguration = building_info[10]
        
        correct_filepath = "Pickle Filepath Not Found"
        
        for filepath in completed_simulation_filepaths:
            if buildingcategory == 'Commercial':
                if (buildingtype in filepath and 
                    buildingstandard in filepath and 
                    buildingstandardyear in filepath and 
                    buildinglocation in filepath):
                    correct_filepath = filepath.rstrip()
            elif buildingcategory == 'Residential': 
                if (buildingprototype in filepath and 
                    buildingclimatezone in filepath and 
                    buildingheatingtype in filepath and 
                    buildingfoundationtype in filepath and 
                    buildingstandard in filepath and 
                    buildingstandardyear in filepath):
                    correct_filepath = filepath.rstrip()
            else:
                if (buildingconfiguration in filepath and 
                    buildinglocation in filepath and 
                    buildingclimatezone in filepath and 
                    buildingstandard in filepath and 
                    buildingheatingtype in filepath):
                    correct_filepath = filepath.rstrip()
        
        # Initialize the list for this building_id
        pickle_filepaths[building_id] = []
        
        # Add the processed data file path
        pickle_filepaths[building_id].append(os.path.join(correct_filepath, "Sim_ProcessedData", "IDF_OutputVariables_DictDF.pickle"))
        
        # Add aggregated data file paths
        aggregated_dir = os.path.join(correct_filepath, "Sim_AggregatedData")
        for filepath in os.listdir(aggregated_dir):
            pickle_filepaths[building_id].append(os.path.join(aggregated_dir, filepath))
    
    cursor.close()
    return pickle_filepaths

# =============================================================================
# Format Datetime Correctly
# =============================================================================
# Use the ISO 8601 format, YYYY-MM-DD HH:MM:SS
# This way SQL can find the max and min Datetime

def format_datetime(simulation_year, datetime):
    
    month = datetime.split('/')[0]
    day = (datetime.split('/')[1]).split('  ')[0]
    time = (datetime.split('  ')[1]).strip()

    hour = time.split(':')[0]
    minute = time.split(':')[1]
    second = time.split(':')[2]
    
    formatted_datetime = str(simulation_year) + '-' + month + '-' + day + ' ' + time
    
    return formatted_datetime

# =============================================================================
# Check if Pickle File has already been Uploaded
# =============================================================================
# Tested - Works

def check_pickle_already_uploaded(pickle_filepath, uploaded_filelist_filepath):
    
    already_uploaded = 0
    
    with open(uploaded_filelist_filepath, 'r') as file:
        for filepath in file.readlines():
            if pickle_filepath == filepath: already_uploaded = 1
    
    return already_uploaded

# =============================================================================
# Check if Variable has already been Upload
# =============================================================================

def get_last_datetime(buildingid, variablename, name_value=None):
    
    # last_datetime is the last datetime uploaded for the variable in question

    conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")    
    cur = conn.cursor()
    
    if name_value:
            # Define the query to get the last datetime for the specified buildingid, variablename, and name_value
            query = sql.SQL("""
                SELECT MAX(datetime) 
                FROM timeseriesdata 
                WHERE buildingid = %s AND variablename = %s AND 
                (schedulename = %s OR zonename = %s OR surfacename = %s OR systemnodename = %s)
            """)
            # Execute the query
            cur.execute(query, (buildingid, variablename, name_value, name_value, name_value, name_value))
    else:
        # Define the query to get the last datetime for the specified buildingid and variablename
        query = sql.SQL("""
            SELECT MAX(datetime) 
            FROM timeseriesdata 
            WHERE buildingid = %s AND variablename = %s
        """)
        # Execute the query
        cur.execute(query, (buildingid, variablename))
    
    last_datetime = cur.fetchone()[0]
    
    cur.close()
    conn.close
    
    return last_datetime  

def datetime_already_uploaded(datetime, buildingid, variablename, name_value=None):
    
    datetime_already_uploaded = 0
    
    if name_value: last_datetime = get_last_datetime(buildingid, variablename, name_value)
    else: last_datetime = get_last_datetime(buildingid, variablename)
    
    if last_datetime is not None:
        datetime_obj = isoparse(datetime)
        last_datetime_obj = isoparse(last_datetime)
        
        if datetime_obj <= last_datetime_obj: datetime_already_uploaded = 1
     
    return datetime_already_uploaded        

def variable_already_uploaded(buildingid, variablename, name_value=None):
    
    if name_value: datetime = get_last_datetime(buildingid, variablename, name_value)
    else: datetime = get_last_datetime(buildingid, variablename)
    
    variable_already_uploaded = 0
    
    if datetime is not None:
       
        time = (datetime.split(' ')[1]).strip()
        hour = time.split(':')[0]
        
        if hour == '24': variable_already_uploaded = 1
        
    return variable_already_uploaded
                
# =============================================================================
# Get Time Series Data for One Building
# =============================================================================
# Works so Far

def upload_time_series_data(pickle_filepath, building_id, timeresolution):
     
   
    # table_df columns = ['buildingid', 'datetime', 'timeresolution', 'variablename', 'zonename', 'surfacename', 'systemnodename', 'value']
    
    insert_query = sql.SQL("""
                    INSERT INTO timeseriesdata (buildingid, datetime, timeresolution, variablename, schedulename, zonename, surfacename, systemnodename, value)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """)
    
    # Load Pickle File
    with open(pickle_filepath, 'rb') as file:
         data = pd.read_pickle(pickle_filepath)
        
    # Key = Variable Name
    # Value = Time Series Data for Variable
    
    caught_up = 0
    
    simulation_year = (data['DateTime_List'])[0].year
    
    for key, value in data.items():
        
        variablename = key.replace('.csv', '') # This May need to be modified
        
        print("Building ID: " + str(building_id) + '\n' + "Pickle Filepath: " + pickle_filepath + '\n')
        print("Processing Variable: " + variablename + '\n')
        
        if variablename == 'Schedule_Value':
            variablename_value = 'Schedule Value'
            zonename_value = 'NA'
            surfacename_value = 'NA'
            systemnodename_value = 'NA'
            schedulenames = value.columns.tolist() # Get Schedule Names - These are Columns in the Schedule_Value table in the eio file pickle. 
            schedulenames.remove('Date/Time')
            for schedulename in schedulenames:
                schedulename_value = (schedulename.split(':')[0]).strip()
                if not variable_already_uploaded(building_id, variablename_value, schedulename_value):  # Check if data has aleady been uploaded for this Schedule Value
                    for index, row in value.iterrows(): # For Each Row in Data, create and add row to table_df
                        datetime_value = row['Date/Time'].strip()
                        datetime_value = format_datetime(simulation_year, datetime_value)
                        if caught_up or not datetime_already_uploaded(datetime_value, building_id, variablename_value, schedulename_value): # only upload data that has not yet been uploaded
                            caught_up = 1
                            table_tilevalue = row[schedulename] # Get Value for this Schedule Value for this Time
                            conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")    
                            cur = conn.cursor() 
                            cur.execute(insert_query, (building_id, datetime_value, timeresolution, variablename_value, schedulename_value, zonename_value, surfacename_value, systemnodename_value, table_tilevalue))
                            conn.commit()
                            cur.close()
                            conn.close()     
            
        elif variablename.startswith('Facility') or variablename.startswith('Site'):  
            # One-Column Variable 
            variablename_value = (variablename.replace('_', ' ')).strip()
            schedulename_value = 'NA'
            zonename_value = 'NA'
            surfacename_value = 'NA'
            systemnodename_value = 'NA'
            if caught_up or not variable_already_uploaded(building_id, variablename_value): # check if data has already been uploaded for this variable
                for index, row in value.iterrows(): # For Each Row in Data, create and add row to table_df
                    datetime_value = row['Date/Time'].strip() 
                    datetime_value = format_datetime(simulation_year, datetime_value)
                    if caught_up or not datetime_already_uploaded(datetime_value, building_id, variablename_value): # only upload data that has not yet been uploaded
                        caught_up = 1
                        columnname = value.columns[1]   # Get ColumnName for Single-Column Variable
                        table_tilevalue = row[columnname]         # Get Value of Single Column
                        conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")    
                        cur = conn.cursor()
                        cur.execute(insert_query, (building_id, datetime_value, timeresolution, variablename_value, schedulename_value, zonename_value, surfacename_value, systemnodename_value, table_tilevalue))
                        conn.commit()
                        cur.close()
                        conn.close()
                
        elif variablename.startswith('Zone'): 
            # Zone-Based Variable
            variablename_value = (variablename.replace('_', ' ')).strip()
            schedulename_value = 'NA'
            surfacename_value = 'NA'
            systemnodename_value = 'NA'
            for index, row in value.iterrows(): # For Each Row in Data, create and add row to table_df
                datetime_value = row['Date/Time'].strip()   
                datetime_value = format_datetime(simulation_year, datetime_value)
                if caught_up or not datetime_already_uploaded(datetime_value, building_id, variablename_value, zonename_value): # only upload data that has not yet been uploaded
                    for columnname in value.columns:    # For each Date/Time, there will be multiple rows - one row for each zone. 
                        if not columnname == 'Date/Time': 
                            zonename_value = (columnname.split(':')[0]).strip()
                            if caught_up or not variable_already_uploaded(building_id, variablename_value, zonename_value): # Check if Zone has laready been uploaded for this variable
                                caught_up = 1
                                table_tilevalue = row[columnname]
                                conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")    
                                cur = conn.cursor()
                                cur.execute(insert_query, (building_id, datetime_value, timeresolution, variablename_value, schedulename_value, zonename_value, surfacename_value, systemnodename_value, table_tilevalue))
                                conn.commit()
                                cur.close()
                                conn.close()
        
        elif variablename.startswith('Surface'):
            # Surface-Based Variable
            variablename_value = (variablename.replace('_', ' ')).strip()
            schedulename_value = 'NA'
            zonename_value = 'NA'
            systemnodename_value = 'NA'
            for index, row in value.iterrows(): # For Each Row in Data, create and add row to table_df
                datetime_value = row['Date/Time'].strip() 
                datetime_value = format_datetime(simulation_year, datetime_value)
                if caught_up or not datetime_already_uploaded(datetime_value, building_id, variablename_value, surfacename_value): # only upload data that has not yet been uploaded
                    for columnname in value.columns:    # For each Date/Time, there will be multiple rows - one row for each surface. 
                        if not columnname == 'Date/Time': 
                            surfacename_value = (columnname.split(':')[0]).strip()
                            if caught_up or not variable_already_uploaded(building_id, variablename_value, surfacename_value): # Check if surface has already been uploaded for this variable
                                caught_up = 1
                                table_tilevalue = row[columnname]
                                conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")    
                                cur = conn.cursor()
                                cur.execute(insert_query, (building_id, datetime_value, timeresolution, variablename_value, zonename_value, schedulename_value, surfacename_value, systemnodename_value, table_tilevalue))
                                conn.commit()
                                cur.close()
                                conn.close()
            
            
        elif variablename.startswith('System_Node'):
            # System Node Based
            variablename_value = (variablename.replace('_', ' ')).strip()
            schedulename_value = 'NA'
            zonename_value = 'NA'
            surfacename_value = 'NA'
            for index, row in value.iterrows(): # For Each Row in Data, create and add row to table_df
                datetime_value = row['Date/Time'].strip() 
                datetime_value = format_datetime(simulation_year, datetime_value)
                if caught_up or not datetime_already_uploaded(datetime_value, building_id, variablename_value, systemnodename_value): # only upload data that has not yet been uploaded
                    for columnname in value.columns:    # For each Date/Time, there will be multiple rows - one row for each systemnode. 
                        if not columnname == 'Date/Time': 
                            systemnodename_value = (columnname.split(':')[0]).strip()
                            if caught_up or not variable_already_uploaded(building_id, variablename_value, systemnodename_value): # check if systemnode has already been uploaded for this variable
                                caught_up = 1
                                table_tilevalue = row[columnname]
                                conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")    
                                cur = conn.cursor()
                                cur.execute(insert_query, (building_id, datetime_value, timeresolution, variablename_value, schedulename_value, zonename_value, surfacename_value, systemnodename_value, table_tilevalue))
                                conn.commit()
                                cur.close()
                                conn.close()
            
        print('\n\n')
        
# =============================================================================
# Main
# =============================================================================

def buildingtimeseriesdata_uploader():
    
    uploaded_filepathlist_filepath = r"D:\Building_Modeling_Code\Code\EPW_DataGeneration\generated_textfiles\timeseriesdata_uploaded_filepathlist.txt"   

    with open(uploaded_filepathlist_filepath, 'r') as file:
        uploaded_filepaths = file.readlines()

    # Link Building ID to Pickle Filepath for all Building IDS
    conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")    
    completed_simulations_txt_filepath = r"D:\Building_Modeling_Code\Code\EPW_DataGeneration\generated_textfiles\completed_simulations.txt"
    pickle_filepaths = get_pickle_filepaths(completed_simulations_txt_filepath, conn) # Access Filepath using the Building ID as the index
    conn.close
    print('\n\n\n\n\n')

    # Time Resolution
    timeresolution = 5

    # Accessing Each Building One at a Time
    # For Each Building, Accessing each pickle file
    for buildingid, building_filepaths in pickle_filepaths:
        for filepath in building_filepaths:
            upload_time_series_data(filepath, buildingid, timeresolution)
    

    # Close the connection
    conn.close()
    
# =============================================================================
# Testing and Running code
# =============================================================================

buildingtimeseriesdata_uploader()   

# This Code is Modified to also upload pickle files for the aggregated data. This version of the code has not been tested yet. 