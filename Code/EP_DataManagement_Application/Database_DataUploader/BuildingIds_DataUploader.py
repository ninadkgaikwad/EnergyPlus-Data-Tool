import os
import pickle
from re import S
import psycopg2

def find_heating_type(file_path): # Use only for Commercial Buildings
    
    search_strings = [
        'ALL OBJECTS IN CLASS: COIL:HEATING:WATER',
        'ALL OBJECTS IN CLASS: COIL:HEATING:ELECTRIC',
        'ALL OBJECTS IN CLASS: COIL:HEATING:STEAM',
        'ALL OBJECTS IN CLASS: COIL:HEATING:GAS'
    ]
    
    found_string = ""
    found_strings = []
    
    # Open and read the file
    with open(file_path, 'r') as file:
        file_contents = file.read()
        
        # Check each string in search_strings to see if it is in the file
        for search_string in search_strings:
            if search_string in file_contents and search_string not in found_strings:
                
                if search_string == 'ALL OBJECTS IN CLASS: COIL:HEATING:WATER':
                    found_strings.append('Water')
                elif search_string == 'ALL OBJECTS IN CLASS: COIL:HEATING:ELECTRIC':
                    found_strings.append('Electric')
                elif search_string == 'ALL OBJECTS IN CLASS: COIL:HEATING:STEAM':
                    found_strings.append('Steam')
                else:
                    found_strings.append('Gas')
                    
                
    combined_string = ' & '.join(found_strings)
  
    return combined_string

def commercial_climate_zone(commercial_building_location):
    
    climate_zone = 'Unknown'
    
    if (commercial_building_location == 'HoChiMinh'):
        climate_zone = '0A'
    elif (commercial_building_location == 'Dubai'): 
        climate_zone = '0B'
    elif (commercial_building_location == 'Miami'):  
        climate_zone = '1A' 
    elif (commercial_building_location == 'Honolulu'):
        climate_zone = '1A'
    elif (commercial_building_location == 'NewDehli'):  
        climate_zone = '1B'
    elif (commercial_building_location == 'Tampa'):  
        climate_zone = '2A'
    elif (commercial_building_location == 'Tucson'):  
        climate_zone = '2B'
    elif (commercial_building_location == 'Atlanta'):  
        climate_zone = '3A'   
    elif (commercial_building_location == 'ElPaso'):  
        climate_zone = '3B'
    elif (commercial_building_location == 'SanDiego'):  
        climate_zone = '3C'
    elif (commercial_building_location == 'NewYork'):  
        climate_zone = '4A'
    elif (commercial_building_location == 'Albuquerque'):  
        climate_zone = '4B'
    elif (commercial_building_location == 'Seattle'):  
        climate_zone = '4C'      
    elif (commercial_building_location == 'Buffalo'):  
        climate_zone = '5A'
    elif (commercial_building_location == 'Denver'):  
        climate_zone = '5B'
    elif (commercial_building_location == 'PortAngeles'):  
        climate_zone = '5C'
    elif (commercial_building_location == 'Rochester'):  
        climate_zone = '6A'
    elif (commercial_building_location == 'GreatFalls'):  
        climate_zone = '6B'
    elif (commercial_building_location == 'InternationalFalls'):  
        climate_zone = '7'
    elif (commercial_building_location == 'Fairbanks'):  
        climate_zone = '8'

    return climate_zone

def parse_name_commercial(model_name): # Naming Convention: Standard_Year_Location_BuildingType
   
    split_string = model_name.split('_')
    model_information = dict(Standard = split_string[0], StandardYear = split_string[1], Climate_Zone = commercial_climate_zone(split_string[2]), Location = split_string[2], BuildingType = split_string[3])
    
    return model_information

def parse_name_residential(model_name): # Naming Convention: Prototype_ClimateZone_Location_HeatingType_FoundationType_Standard_Year 
    
    split_string = model_name.split('_')
    model_information = dict(Prototype = split_string[0], ClimateZone = split_string[1], Location = split_string[2], HeatingType = split_string[3], FoundationType = split_string[4], Standard = split_string[5], Year = split_string[6]);
    
    return model_information

def parse_name_manufactures(model_name): # Naming Convention: Configuration_Location_ClimateZone_EnergyCode_HeatingType
    
    split_string = model_name.split('_')
    model_information = dict(Configuration = split_string[0], Location = split_string[1], ClimateZone = split_string[2], EnergyCode = split_string[3], HeatingType = split_string[4]);
    
    return model_information

def upload_to_buildingsids(model_information, building_category, conn): 
    
    # SQL query template for inserting data
        insert_query = """
        INSERT INTO buildingids (
            buildingcategory, buildingtype, buildingprototype, buildingconfiguration, buildingstandard, 
            buildingstandardyear, buildinglocation, buildingclimatezone, 
            buildingheatingtype, buildingfoundationtype
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Prepare data for insertion, replacing missing fields with 'NA'
        data = (
            building_category,
            model_information.get('BuildingType', 'NA'),
            model_information.get('Prototype', 'NA'),
            model_information.get('Configuration', 'NA'),
            model_information.get('Standard', 'NA'),
            model_information.get('StandardYear', 'NA'),
            model_information.get('Location', 'NA'),
            model_information.get('Climate_Zone', 'NA'),
            model_information.get('HeatingType', 'NA'),
            model_information.get('FoundationType', 'NA')
        )
        
        cursor = conn.cursor()
        cursor.execute(insert_query, data)
        cursor.close()
        
        print("Data uploaded successfully.")
        

########## MAIN ##########

conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")

current_folderpath = os.path.dirname(__file__)

commercial_models_folderpath = os.path.join(current_folderpath, '..', 'Results', 'Processed_BuildingSim_Data')

completed_simulations_textfile = open(r"D:\Building_Modeling_Code\Code\EPW_DataGeneration\generated_textfiles\completed_simulations.txt", 'r')
completed_simulations = completed_simulations_textfile.readlines()

for folderpath in completed_simulations:
    
    if folderpath.startswith('ASHRAE') or folderpath.startswith('IECC'):
        model_information = parse_name_commercial(os.path.basename(folderpath))
        upload_to_buildingsids(model_information, 'Commercial', conn)
    elif folderpath.startswith('MF') or folderpath.startswith('SF'):
        model_information = parse_name_residential(os.path.basename(folderpath))
        upload_to_buildingsids(model_information, 'Residential', conn)
    else:
        model_infomration = parse_name_manufactures(os.path.basename(folderpath))
        upload_to_buildingsids(model_information, 'Manufactured', conn)
    
conn.commit()
conn.close()

#Postgres SQL Database
#buildingids columns:
#buildingcategory
#buildingtype
#buildingstandard
#buildingstandardyear
#buildinglocation
#buildingclimatezone
#buildingheatingtype
#buildingfoundationtype
#buildingclimatezone

