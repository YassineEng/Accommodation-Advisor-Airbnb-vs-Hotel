# services/database_service.py
# This file provides functionalities for interacting with the database.
# It handles establishing a connection and executing SQL queries.

import os
import pyodbc
from config.config import settings

# Function to establish a connection to the database.
# It uses the connection string defined in the application settings.
def get_db_connection():
    # pyodbc.connect establishes a connection to an ODBC data source.
    return pyodbc.connect(settings.db_connection_string)

# Function to execute a SQL query against the database.
# It can handle queries with optional parameters to prevent SQL injection.
def execute_query(query, params=None):
    # Use a 'with' statement to ensure the database connection is properly closed after use.
    with get_db_connection() as conn:
        cursor = conn.cursor() # Create a cursor object to execute SQL commands.
        if params:
            cursor.execute(query, params) # Execute query with parameters.
        else:
            cursor.execute(query) # Execute query without parameters.
        
        # Fetch column names from the cursor description.
        columns = [column[0] for column in cursor.description]
        results = []
        # Fetch all rows and convert them into a list of dictionaries,
        # where each dictionary represents a row with column names as keys.
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results
