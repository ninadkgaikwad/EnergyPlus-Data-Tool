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
    
    pickle_filepaths = {} # Access a filepath by building ID
    
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
            
        pickle_filepaths[building_id] = os.path.join(correct_filepath, "Sim_ProcessedData", "Eio_OutputFile.pickle")
    
    cursor.close()        
    return pickle_filepaths

# =============================================================================
# Get Eio Table Data for One Building 
# =============================================================================

def upload_eiotable_data(buildingid, pickle_filepath): 
    
    # Table Columns = ['buildingid', 'tablename', 'zonename', 'variablename', 'value']
    print("Processing " + pickle_filepath + '\n')
    
    insert_query = sql.SQL("""
                    INSERT INTO eiotabledata (buildingid, tablename, zonename, variablename, stringvalue, floatvalue)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """)
    
    check_query = sql.SQL("""
                    SELECT EXISTS(
                        SELECT 1 FROM eiotabledata 
                        WHERE buildingid = %s AND tablename = %s AND zonename = %s AND variablename = %s AND stringvalue = %s AND floatvalue = %s
                    )
                    """)
    
    # Load Pickle File
    with open(pickle_filepath, 'rb') as file: data = pd.read_pickle(pickle_filepath)
    
    for key, value in data.items():
        
        tablename = key
        
        columns = value.columns.tolist()
        columns.remove('Zone Name')
        
        for column in columns:
            
            variablename = column.strip()
            
            for index, row in value.iterrows():
                
                zonename = row['Zone Name'].strip()
                
                table_value = row[column]
                
                try:
                    floatvalue = float(table_value)
                    stringvalue = 'NA'
                except:
                    stringvalue = table_value
                    floatvalue = float('NaN')
                
                conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")    
                cur = conn.cursor() 
                
                # Check if the row already exists
                cur.execute(check_query, (buildingid, tablename, zonename, variablename, stringvalue, floatvalue))
                exists = cur.fetchone()[0]
                
                if not exists:
                    # Insert the row if it does not exist
                    cur.execute(insert_query, (buildingid, tablename, zonename, variablename, stringvalue, floatvalue))
                    conn.commit()
                    
                cur.close()
                conn.close()
            
            
# =============================================================================
# Main
# =============================================================================

uploaded_filepathlist = r"D:\Building_Modeling_Code\Code\EPW_DataGeneration\generated_textfiles\eiotabledata_uploaded_filepathlist.txt"

with open(uploaded_filepathlist, 'r') as file:
    uploaded_filepaths = file.readlines()

# Link Building ID to Pickle Filepath for all Building IDS
conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")    
completed_simulations_txt_filepath = r"D:\Building_Modeling_Code\Code\EPW_DataGeneration\generated_textfiles\completed_simulations.txt"
pickle_filepaths = get_pickle_filepaths(completed_simulations_txt_filepath, conn) # Access Filepath using the Building ID as the index
conn.close()

# Accessing Each Building One at a Time
for i in range(len(pickle_filepaths)):
    buildingid = i + 1
    if not pickle_filepaths[buildingid] in uploaded_filepaths:
        upload_eiotable_data(buildingid, pickle_filepaths[buildingid])
        with open(uploaded_filepathlist, 'a') as file:
            file.write(pickle_filepaths[buildingid] + '\n')
    else: print(pickle_filepaths[buildingid] + " Already Uploaded\n")

# =============================================================================
# Testing
# =============================================================================


