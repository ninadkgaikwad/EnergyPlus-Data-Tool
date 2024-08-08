import os
import pickle
from re import S
import psycopg2

# Connect to the PostgreSQL database
conn = psycopg2.connect("dbname=Building_Models user=kasey password=OfficeLarge")
cursor = conn.cursor()

create_table_query = """
    CREATE TABLE buildingids (
        buildingid SERIAL PRIMARY KEY,
        buildingcategory TEXT,
        buildingtype TEXT,
        buildingstandard TEXT,
        buildingstandardyear TEXT,
        buildinglocation TEXT,
        buildingheatingtype TEXT,
        buildingfoundationtype TEXT,
        buildingclimatezone TEXT,
        buildingprototype TEXT,
        buildingconfiguration TEXT
    );
    """
cursor.execute(create_table_query)
conn.commit()  # Commit all operations at once

# Close the connection
cursor.close()
conn.close()