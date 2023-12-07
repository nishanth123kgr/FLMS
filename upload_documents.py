import mysql.connector

from from_csv.el_from_csv import get_el
from from_csv.ml_mtl_lop_from_csv import get_ml_mtl_lop
from from_csv.utils import get_total_days, convert_to_date_text
from from_csv.vl_from_csv import get_vl
from utils.vl_report import get_staff_details

import os


def upload_leave_details(cursor, file, db):
    staff_id = file.split('/')[1][:5]
    name, dept, doj = get_staff_details(staff_id, cursor)
    info = []
    el = get_el(file, 'EL')
    ml, mtl, lop, sl, eol = get_ml_mtl_lop(file, 'EL')
    # Update the EL table
    for i in range(len(el)):
        row = el[i]
        query = ''
        try:
            total = get_total_days(row[0], row[1])
            query = 'INSERT INTO el (id, dept, `from`, `to`, from_prefix, to_prefix, from_suffix, to_suffix, date_of_rejoin, total) VALUES (%s, "%s", "%s", "%s", %s, %s, %s, %s, %s, %s)' % (
                staff_id,
                dept,
                row[0],
                row[1],
                row[2][0] if row[2][0] == "NULL" else '"' + row[2][0] + '"',
                row[2][1] if row[2][1] == "NULL" else '"' + row[2][1] + '"',
                row[2][2] if row[2][2] == "NULL" else '"' + row[2][2] + '"',
                row[2][3] if row[2][3] == "NULL" else '"' + row[2][3] + '"',
                row[3] if row[3] == "NULL" else '"' + row[3] + '"',
                total,
            )
            # print(query)
            cursor.execute(
                query
            )
            db.commit()
            cursor.reset()
        except Exception as e:
            if "Duplicate entry" not in str(e):
                # print(query)
                # print(row)
                # print(e)
                pass
    # Update the ML, MTL, LOP table
    for name, table in [("ml", ml), ("mtl", mtl), ("lop", lop), ("sl", sl), ("eol", eol)]:
        if table:
            for i in range(len(table)):
                row = table[i]
                print(row, row[1])
                try:
                    total = get_total_days(row[0], row[1])
                    query = 'INSERT INTO %s (id, dept, `from`, `to`, medical_fittness_on, from_prefix, to_prefix, from_suffix, to_suffix, doj,total) VALUES (%s, "%s", "%s", "%s",%s, %s, %s, %s, %s, "%s", %s)' % (
                        name,
                        staff_id,
                        dept,
                        row[0],
                        row[1],
                        "NULL" if (row[3] == "NULL" or row[3] == '-') else f'"{row[3]}"',
                        row[4][0]
                        if row[4][0] == "NULL"
                        else '"' + row[4][0] + '"',
                        row[4][1]
                        if row[4][1] == "NULL"
                        else '"' + row[4][1] + '"',
                        row[4][2]
                        if row[4][2] == "NULL"
                        else '"' + row[4][2] + '"',
                        row[4][3]
                        if row[4][3] == "NULL"
                        else '"' + row[4][3] + '"',
                        row[5],
                        total,
                    )
                    print(query)
                    cursor.execute(
                        query
                    )
                    db.commit()
                    cursor.reset()
                except Exception as e:
                    if "Duplicate entry" not in str(e):
                        print(query)
                        print(row)
                        print(e)


def vl_upload(file, cursor, db):
    staff_id = file.split('/')[1][:5]
    data = get_vl(staff_id, file, "VL", cursor)
    for key, value in data.items():
        data[key] = {
            inner_key: convert_to_date_text(inner_value)
            for inner_key, inner_value in value.items()
        }
    try:
        for i in data:
            data[i]["Availed_from"] = list(filter(lambda x: x not in [None, "NULL"], data[i]["Availed_from"]))
            data[i]["Availed_to"] = list(filter(lambda x: x not in [None, "NULL"], data[i]["Availed_to"]))
            query = (
                    f'INSERT into vl (vac_id, staff_id, availed_from, availed_to, prevented, other_leave) values ("%s", %s, %s, %s, %s, %s)'
                    % (
                        i,
                        staff_id,
                        "NULL"
                        if (
                            not data[i]["Availed_from"]
                        )
                        else '"' + str(data[i]["Availed_from"]) + '"',
                        "NULL"
                        if (
                            not data[i]["Availed_to"]
                        )
                        else '"' + str(data[i]["Availed_to"]) + '"',
                        "NULL"
                        if (
                                data[i]["Prevented"] is None
                                or data[i]["Prevented"] == "NULL"
                        )
                        else '"' + str(data[i]["Prevented"]) + '"',
                        "NULL"
                        if (
                                data[i]["others"] is None
                                or data[i]["others"] == "NULL"
                        )
                        else '"' + str(data[i]["others"]) + '"'
                    )
            )
            cursor.execute(query)

            db.commit()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    db = mysql.connector.connect(
        host="localhost", port="3306", user="root", database="facultyleavedb"
    )
    cursor = db.cursor()
    directory_path = './LeaveData/'

    # List all files in the directory
    files_in_directory = os.listdir(directory_path)

    # Iterate through each file in the directory
    for file_name in files_in_directory:

        if not file_name.startswith(('~', '.')):
            print(file_name)
            upload_leave_details(cursor, f"LeaveData/{file_name}", db)
            vl_upload(f"LeaveData/{file_name}", cursor, db)

cursor.close()
db.close()
