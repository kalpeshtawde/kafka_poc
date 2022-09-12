from psycopg2 import connect

table_name = "payment"

# declare connection instance
conn = connect(
    dbnam="postgres",
    user="postgres",
    host="192.168.1.6",
    port="5435",
    password="postgres"
)

# declare a cursor object from the connection
cursor = conn.cursor()

# execute an SQL statement using the psycopg2 cursor object
cursor.execute(f"SELECT * FROM {table_name};")

# enumerate() over the PostgreSQL records
for i, record in enumerate(cursor):
    print ("\n", type(record))
    print ( record )

# close the cursor object to avoid memory leaks
cursor.close()

# close the connection as well
conn.close()
