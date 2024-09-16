import mysql.connector
from mysql.connector import Error
import json

from google_sheet import read_sheet_data


def get_mysql_connection():
    with open('secrets.json') as f:
        secrets = json.load(f)

    connection = mysql.connector.connect(
        host=secrets['mysql']['host'],
        database=secrets['mysql']['database'],
        user=secrets['mysql']['user'],
        password=secrets['mysql']['password']
    )
    return connection


def create_table(cursor, table_name, num_columns):
    columns_def = ', '.join([f"col{i + 1} VARCHAR(255)" for i in range(num_columns)])
    drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
    cursor.execute(drop_table_query)
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT NOT NULL AUTO_INCREMENT UNIQUE,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        {columns_def},
        PRIMARY KEY (id)
    );
    """
    cursor.execute(create_table_query)


def upsert_data(cursor, table_name, data):
    # Determine the number of columns based on the longest row
    num_columns = max(len(row) for row in data) if data else 0

    if num_columns == 0:
        print("No data to insert/update.")
        return

    placeholders = ', '.join(['%s'] * num_columns)
    update_placeholders = ', '.join([f"col{i + 1} = VALUES(col{i + 1})" for i in range(num_columns)])

    for row in data:
        if len(row) < num_columns:
            row += [None] * (num_columns - len(row))  # Pad with None if fewer columns

        row_tuple = tuple(row)

        query = f"""
        INSERT INTO {table_name} ({', '.join([f'col{i + 1}' for i in range(num_columns)])})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_placeholders}, timestamp = CURRENT_TIMESTAMP;
        """

        print("Upsert Query:", query)
        print("Upsert Parameters:", row_tuple)

        try:
            cursor.execute(query, row_tuple)
        except mysql.connector.Error as err:
            print(f"Upsert Error: {err}")


def sync_google_sheet_to_db(spreadsheet_id, range_name):
    sheet_data = read_sheet_data(spreadsheet_id, range_name)
    print(sheet_data)

    cnx = get_mysql_connection()
    cursor = cnx.cursor()

    try:
        num_columns = max(len(row) for row in sheet_data if row) if sheet_data else 0

        create_table(cursor, range_name, num_columns)

        processed_data = [[None if cell == '' else cell for cell in row] for row in sheet_data]
        upsert_data(cursor, range_name, processed_data)

        cnx.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        cnx.close()
