import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
TABLE_NAME = os.getenv('TABLE_NAME')

# create_reditposts()
def create_reditposts(site_url, name, post, title_date):
    # Establish the database connection
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = connection.cursor()
 
    try:
        # Insert a new record into the `reditposts` table
        insert_query = """
            INSERT INTO test (site_url, name, post, title_date)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (site_url, name, post, title_date))
        redit_post_id = cursor.lastrowid  # Get the ID of the inserted row
        
        connection.commit()  # Commit the transaction
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        redit_post_id = None
    finally:
        cursor.close()
        connection.close()

    return redit_post_id


def get_last_row():
    # Establish the database connection
    connection = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True to get results as a dictionary
    
    try:
        # Query to fetch the last row based on the primary key or an auto-increment column
        fetch_query = "SELECT * FROM test ORDER BY id DESC LIMIT 1"
        cursor.execute(fetch_query)
        last_row = cursor.fetchone()  # Fetch the last row
        
        if last_row is None:
            # If the database is empty, handle accordingly
            print("The database is empty.")
            return None
        else:
            title_date = last_row.get('title_date')
            return title_date

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        connection.close()