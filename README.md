[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/AHFn7Vbn)
# Superjoin Hiring Assignment

### Welcome to Superjoin's hiring assignment! 🚀

### Objective
Build a solution that enables real-time synchronization of data between a Google Sheet and a specified database (e.g., MySQL, PostgreSQL). The solution should detect changes in the Google Sheet and update the database accordingly, and vice versa.

### Problem Statement
Many businesses use Google Sheets for collaborative data management and databases for more robust and scalable data storage. However, keeping the data synchronised between Google Sheets and databases is often a manual and error-prone process. Your task is to develop a solution that automates this synchronisation, ensuring that changes in one are reflected in the other in real-time.

### Requirements:
1. Real-time Synchronisation
  - Implement a system that detects changes in Google Sheets and updates the database accordingly.
   - Similarly, detect changes in the database and update the Google Sheet.
  2.	CRUD Operations
   - Ensure the system supports Create, Read, Update, and Delete operations for both Google Sheets and the database.
   - Maintain data consistency across both platforms.
   
### Optional Challenges (This is not mandatory):
1. Conflict Handling
- Develop a strategy to handle conflicts that may arise when changes are made simultaneously in both Google Sheets and the database.
- Provide options for conflict resolution (e.g., last write wins, user-defined rules).
    
2. Scalability: 	
- Ensure the solution can handle large datasets and high-frequency updates without performance degradation.
- Optimize for scalability and efficiency.

## Submission ⏰
The timeline for this submission is: **Next 2 days**

Some things you might want to take care of:
- Make use of git and commit your steps!
- Use good coding practices.
- Write beautiful and readable code. Well-written code is nothing less than a work of art.
- Use semantic variable naming.
- Your code should be organized well in files and folders which is easy to figure out.
- If there is something happening in your code that is not very intuitive, add some comments.
- Add to this README at the bottom explaining your approach (brownie points 😋)
- Use ChatGPT4o/o1/Github Co-pilot, anything that accelerates how you work 💪🏽. 

Make sure you finish the assignment a little earlier than this so you have time to make any final changes.

Once you're done, make sure you **record a video** showing your project working. The video should **NOT** be longer than 120 seconds. While you record the video, tell us about your biggest blocker, and how you overcame it! Don't be shy, talk us through, we'd love that.

We have a checklist at the bottom of this README file, which you should update as your progress with your assignment. It will help us evaluate your project.

- [x] My code's working just fine! 🥳
- [x] I have recorded a video showing it working and embedded it in the README ▶️
- [x] I have tested all the normal working cases 😎
- [x] I have even solved some edge cases (brownie points) 💪
- [x] I added my very planned-out approach to the problem at the end of this README 📜

## Got Questions❓
Feel free to check the discussions tab, you might get some help there. Check out that tab before reaching out to us. Also, did you know, the internet is a great place to explore? 😛

We're available at techhiring@superjoin.ai for all queries. 

All the best ✨.

## Developer's Section
### Video Explanation
https://drive.google.com/file/d/1PUwdEF8OLCnXv4LEWuPBcHiyXAM3Q2DE/view?usp=sharing
_or_
[![Watch the video](https://img.youtube.com/vi/1Q3JZ4w1l1I/maxresdefault.jpg)](https://drive.google.com/file/d/1PUwdEF8OLCnXv4LEWuPBcHiyXAM3Q2DE/view?usp=sharing)

### Setup Requirements
Google Sheets API and Drive API Setup:

Create a Project: In the Google Cloud Console, create a project and enable the Google Sheets API and Google Drive API.
OAuth Credentials: Download OAuth 2.0 credentials (client secret) and save them as credentials.json.
Token Management: The script uses token.json to store access tokens.
MySQL Setup:

Database Connection: Ensure that you have a MySQL database running and accessible. Create tables as needed.
Database Credentials: Store MySQL connection details in secrets.json.

### Components

1. The mysql_db.py file in your project contains several functions that interact with a MySQL database. Here's a brief overview of each function:  
2. get_mysql_connection(): This function reads the MySQL connection details from a secrets.json file and establishes a connection to the MySQL server. It returns the connection object.  
3. create_table(cursor, table_name, num_columns): This function creates a new table in the MySQL database. It takes a cursor object, a table name, and the number of columns as arguments. It first drops the table if it already exists, then creates a new table with the specified number of columns.  
4. upsert_data(cursor, table_name, data): This function inserts or updates data in the specified table. It takes a cursor object, a table name, and the data to be inserted or updated as arguments. It determines the number of columns based on the longest row in the data, then constructs and executes an SQL query to insert or update the data.  
5. sync_google_sheet_to_db(spreadsheet_id, range_name): This function synchronizes data from a Google Sheet to the MySQL database. It reads data from the specified Google Sheet, establishes a connection to the MySQL server, creates a table in the database if it doesn't already exist, then inserts or updates the data in the table.  
6. These functions are imported and used in the main.py file to synchronize data between a Google Sheet and a MySQL database.

## Approach

### Overview
This project involves synchronizing data between Google Sheets and a MySQL database. The synchronization process ensures that changes in either source are reflected in the other, with Google Sheets having priority in case of conflicts.

## Synchronization Workflow
### Polling Interval:

The system polls for updates every 10 seconds.
### Data Comparison:

* Google Sheets Data: Extracted from the specified range.
* Database Data: Extracted from the corresponding table.
* Normalization: Data from both sources is normalized to handle empty cells and mismatched lengths.
* Comparison: Each cell in the rows (excluding extra columns in the database) is compared. None and empty strings ('') are considered equivalent.
### Syncing Data:

* Google Sheets to Database: If Google Sheets data is more recent, it updates the database.
* Database to Google Sheets: If database data is more recent, it updates the Google Sheets.
* Conflict Resolution: In case of conflicting changes, the data from Google Sheets will overwrite the database.
## Detailed Sync Algorithm
### Fetch Update Timestamps:

Retrieve the last update timestamps from both Google Sheets and the database.
### Compare Timestamps:

Convert timestamps to Unix format for comparison.
Decide which source has more recent data.
### Perform Synchronization:

Update the database with Google Sheets data if it's newer.
Update Google Sheets with database data if it's newer.
Handle Empty Cells:

Normalize data by treating None and '' as equivalent during comparison.