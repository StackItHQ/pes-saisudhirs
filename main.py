import mysql

from google_sheet import read_sheet_data
from mysql_db import get_mysql_connection, create_table, upsert_data

def sync_google_sheet_to_db(spreadsheet_id, range_name):
    sheet_data = read_sheet_data(spreadsheet_id, range_name)

    # Connect to the database
    cnx = get_mysql_connection()
    cursor = cnx.cursor()

    try:
        # Determine the number of columns from the first non-empty row
        num_columns = max(len(row) for row in sheet_data if row) if sheet_data else 0

        # Create or alter the table as needed
        create_table(cursor, range_name, num_columns)

        # Process and insert/update data
        processed_data = [[None if cell == '' else cell for cell in row] for row in sheet_data]
        upsert_data(cursor, range_name, processed_data)

        # Commit changes
        cnx.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        cnx.close()

if __name__ == "__main__":
    sync_google_sheet_to_db("speadsheet_id", "Sheet1")
