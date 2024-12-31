import mysql.connector
import time

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'redit'
TABLE_NAME = 'reditposts'


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
            INSERT INTO reditposts (site_url, name, post, title_date)
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
