import os
import pickle
import psycopg2
import pandas as pd

pickle_file_path = 'D:/Building_Modeling_Code/Results/Processed_BuildingSim_Data/ASHRAE_2013_Albuquerque_ApartmentHighRise/Sim_ProcessedData/IDF_OutputVariables_DictDF.pickle'

data = pd.read_pickle(pickle_file_path)

# Connect to the PostgreSQL database
conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")
cursor = conn.cursor()

# zonename only applies for zone-based variables
# surfacename only applies for surface-based variables
# systemnodename only applies for node related varables. 
        
create_table_query = f"""
        CREATE TABLE eiotabledata (
            eiotabledataid SERIAL PRIMARY KEY,
            buildingid INTEGER REFERENCES buildingids(buildingid),
            tablename TEXT,
            zonename TEXT,
            variablename TEXT,
            stringvalue TEXT,
            floatvalue REAL
        );
        """

cursor.execute(create_table_query)
conn.commit()  # Commit all operations at once

# Close the connection
cursor.close()
conn.close()
