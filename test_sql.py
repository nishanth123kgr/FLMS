import mysql.connector
import pandas as pd

db = mysql.connector.connect(
    host="localhost", port="3306", user="root", database="facultyleavedb"
)
cursor = db.cursor()

cursor.execute("select v_id, total_days from general_vacation_details")
details = pd.DataFrame(cursor.fetchall(), columns=['Year', 'Total'])

details["Year"] = details["Year"].apply(lambda x: x[:-1])

details_grp = details.groupby("Year")
print(details_grp["Total"].sum())


cursor.close()
