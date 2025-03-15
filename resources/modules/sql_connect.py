import mysql.connector
from mysql.connector import Error

"""
Currently unused, will apply as an option to connect to a SQL database in the future.
"""
def create_connection(host_name='localhost', user_name='root', user_password='', db_name=''):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except Error as e:
        print(f"The error '{e}' occurred")
    return result

connect = create_connection("localhost", "root", "")
select_users = "SELECT * FROM users"
users = execute_read_query(connect, select_users)
for user in users:
    print(user)