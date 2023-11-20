import pandas as pd
import mysql.connector
import datetime

df = pd.read_excel('Teaching - Probation.xlsx', sheet_name='Sheet1')

df.drop(df.columns[0], axis=1, inplace=True)
df.drop(axis=0, index=range(4), inplace=True)
df.reset_index(drop=True, inplace=True)
df.iloc[:, -1] = df.iloc[:, -1].apply(lambda x: datetime.datetime.strptime(str(x).split()[0].strip(), '%d.%m.%Y').strftime("%Y-%m-%d") if str(x) != 'nan' else None)

db = mysql.connector.connect(host="localhost", port="3306", user="root", database="facultyleavedb")
cursor = db.cursor()
print(df.iloc[:, -1])
try:
    for i in df.values.tolist():
        # print(i[0])
        query = "update staff set probation = '%s', designation = '%s' where name like '%s%%'" % (i[4] if i[4] else 'NULL', i[1].strip(), i[0].strip())
        print(query)
        cursor.execute(query)
        # name = cursor.fetchall()
        cursor.reset()
        # print(name)

        # cursor.execute("update staff set probation=1 where id=%s" % name[0][1])
except Exception as e:
    print(e)
    db.rollback()
db.commit()
