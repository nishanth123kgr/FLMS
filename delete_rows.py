import mysql.connector

db = mysql.connector.connect(
    host="localhost", port="3306", user="root", database="facultyleavedb"
)
cursor = db.cursor()

# ids = [13333] + [12222, 12223, 12224, 25001, 25005, 25007, 25009, 25010, 25012, 25013, 25019, 25030, 13331, 13332,
#                     13333, 27002] + [30002, 20003, 30003, 45000, 45001] + [26001, 55555] + [10001, 21002, 21003, 21010,
#                                                                                             66661] + [24001, 24003, 29007, 55551, 21006]
ids = [24003]
for i in ids:
    for j in ['el', 'ml', 'mtl', 'lop']:
        query = f"delete from {j} where id={i}"
        cursor.execute(query)
        db.commit()
    # query = f"delete from vl where staff_id={i}"
    # cursor.execute(query)
    # db.commit()

# for j in ['el', 'ml', 'mtl', 'lop']:
#     query = f"delete from {j} where dept='CSE'"
#     cursor.execute(query)
#     db.commit()

# query = "DELETE FROM vl WHERE staff_id IN (SELECT id FROM staff WHERE department = 'CSE');"
# cursor.execute(query)
# db.commit()
