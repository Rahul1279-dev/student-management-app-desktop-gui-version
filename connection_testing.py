from dotenv import load_dotenv
import pymysql,os

load_dotenv()
my_password = os.getenv("MYSQLPASSWORD")
print(my_password)

# Connect to the database
connection = pymysql.connect(
    host="localhost",
    user="root",
    password=my_password,
    database="school"
)

print("Connected!")

# Example query to test
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE();")
        result = cursor.fetchall()
        print("You're connected to database:", result)
finally:
    connection.close()
    print("Connection closed.")
