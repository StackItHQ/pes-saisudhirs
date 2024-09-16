import json
import time
from datetime import datetime

import mysql

from db_utils import get_db_last_update, fetch_all_data
from google_sheet import read_sheet_data, get_sheet_last_update, update_google_sheet
from mysql_db import get_mysql_connection, create_table, upsert_data

with open('secrets.json') as f:
    secrets = json.load(f)

SPREADSHEET_ID = secrets['google']['spreadsheet_id']
RANGE_NAME = secrets['google']['range_name']
POLLING_INTERVAL = 10  # seconds


def clean_values(values):
    return [[cell if cell is not None else '' for cell in row] for row in values]


def sync_db_to_sheet(spreadsheet_id, range_name):
    cnx = get_mysql_connection()
    cursor = cnx.cursor()
    try:
        rows = fetch_all_data(cursor, range_name)
        if rows:
            # Convert rows from database to sheet format
            sheet_data = [list(row[2:]) for row in rows]  # Exclude the id column
            update_google_sheet(spreadsheet_id, range_name, clean_values(sheet_data))
    except mysql.connector.Error as err:
        print(f"DB to Sheet Sync Error: {err}")
    finally:
        cursor.close()
        cnx.close()


def sync_google_sheet_to_db(spreadsheet_id, range_name):
    sheet_data = read_sheet_data(spreadsheet_id, range_name)
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


def count_non_empty_rows(data):
    """Count rows in data that are not entirely None or empty."""
    non_empty_row_count = 0
    for row in data:
        # Check if any value in the row is non-empty
        if any(cell for cell in row if cell not in (None, '')):
            non_empty_row_count += 1
    return non_empty_row_count


def count_non_empty_cells(data):
    """Count non-empty cells in the given data."""
    print(data)
    non_empty_cell_count = 0
    for row in data:
        for cell in row:
            if cell not in (None, ''):
                non_empty_cell_count += 1
    return non_empty_cell_count


def normalize_value(value):
    """Normalize values to treat None and '' as equivalent."""
    return value if value is not None else ''


def compare_data(sheet_data, db_data):
    """Compare the data from Google Sheets and the database, treating None and '' as equivalent."""

    # Exclude extra columns at the start of db_data
    extra_columns_count = 2

    # Normalize the length of rows in both datasets
    max_rows = max(len(sheet_data), len(db_data))
    sheet_data.extend([[]] * (max_rows - len(sheet_data)))  # Pad with empty rows
    db_data.extend([[]] * (max_rows - len(db_data)))  # Pad with empty rows

    for index, (sheet_row, db_row) in enumerate(zip(sheet_data, db_data)):
        # Compare rows, excluding the extra columns at the start of db_row
        db_comparable_row = db_row[extra_columns_count:]

        # Normalize values in rows to treat None and '' as the same
        normalized_sheet_row = [normalize_value(cell) for cell in sheet_row]
        normalized_db_row = [normalize_value(cell) for cell in db_comparable_row]

        # Trim trailing empty values for a cleaner comparison
        while normalized_db_row and normalized_db_row[-1] == '':
            normalized_db_row.pop()

        # Compare rows
        if normalized_sheet_row != normalized_db_row:
            print(f"Row mismatch at index {index}:")
            print(f"Google Sheets row (normalized): {normalized_sheet_row}")
            print(f"Database row (normalized, with extra columns excluded): {normalized_db_row}")
            return False

    return True


def sync_loop():
    last_sync_sheet = 0
    last_sync_db = 0

    while True:
        try:
            # Check for the last update times
            print("Checking last update times...")
            sheet_last_update = get_sheet_last_update(SPREADSHEET_ID) if not None else 0

            cnx = get_mysql_connection()
            cursor = cnx.cursor()
            db_last_update_iso = get_db_last_update(cursor, RANGE_NAME)
            db_last_update = int((datetime.strptime(str(db_last_update_iso), "%Y-%m-%d %H:%M:%S")).timestamp())

            # Fetch data from Google Sheets and database for comparison
            sheet_data = read_sheet_data(SPREADSHEET_ID, RANGE_NAME)
            db_data = fetch_all_data(cursor, RANGE_NAME)  # Implement fetching data from DB

            # Count non-empty rows for comparison
            sheet_non_empty_count = count_non_empty_cells(sheet_data)
            db_non_empty_count = count_non_empty_cells(db_data) - (
                        2 * count_non_empty_rows(db_data))  # Exclude the header row
            cursor.close()
            cnx.close()
            print(f"Sheet rows: {sheet_non_empty_count}, DB rows: {db_non_empty_count}")

            # Sync based on row counts
            if sheet_non_empty_count > db_non_empty_count:
                print("Google Sheets has more data, syncing to DB...")
                sync_google_sheet_to_db(SPREADSHEET_ID, RANGE_NAME)
                last_sync_sheet = sheet_last_update
            elif db_non_empty_count > sheet_non_empty_count:
                print("Database has more data, syncing to Google Sheets...")
                sync_db_to_sheet(SPREADSHEET_ID, RANGE_NAME)
                last_sync_db = db_last_update
            else:
                if compare_data(sheet_data, db_data):
                    print("Data is in sync.")
                else:
                    print("Data mismatch, forcing Google Sheet data to DB...")
                    sync_google_sheet_to_db(SPREADSHEET_ID, RANGE_NAME)
                    last_sync_sheet = sheet_last_update

            print(f"Next sync in {POLLING_INTERVAL} seconds...")
            time.sleep(POLLING_INTERVAL)
        except Exception as e:
            print(f"Sync Error: {e}")
            time.sleep(POLLING_INTERVAL)


if __name__ == "__main__":
    sync_loop()
