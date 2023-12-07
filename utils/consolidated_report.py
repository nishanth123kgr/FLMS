import mysql.connector
import xlsxwriter
from leave_report_final import generate_consolidated_report
from vl_report import generate_vl, get_staff_details
from report_generation import generate_report
import os


def consolidated_report(id, cursor):
    name, dept, doj = get_staff_details(id, cursor)
    print(name, dept, doj, f"Consolidated_Reports/{dept}")
    if not os.path.exists(f"Consolidated_Reports/{dept}"):
        os.makedirs(f"Consolidated_Reports/{dept}")
    workbook = xlsxwriter.Workbook(f"Consolidated_Reports/{dept}/{id}-{name.strip().replace(' ', '')}.xlsx")
    generate_consolidated_report(id, cursor, workbook)
    generate_vl(id, cursor, workbook)
    generate_report(cursor,id, workbook)
    workbook.close()


if __name__ == '__main__':
    id = '22003'
    db = mysql.connector.connect(
        host="localhost", port="3306", user="root", database="facultyleavedb"
    )
    cursor = db.cursor()
    civil_ids = [21002, 21003, 21010, 21006]
    snh_ids = [20003, 29007, 30002, 30003, 45000]
    cse_ids = [22003, 22222, 22007, 22223, 22015, 22019, 22009, 22010, 22006]
    ece_ids = [24001, 24003]
    mba_ids = [26001, 55555, 55551]
    mca_ids = [13331, 13332, 27002, 13333]
    mech_ids = [25012, 25009, 12223, 25010, 25005, 25019, 25007, 25001]
    other_ids = [32546, 22021]

    combined_array = civil_ids + snh_ids + cse_ids + ece_ids + mba_ids + mca_ids + mech_ids + other_ids

    print(combined_array)
    for id in combined_array:
        print(id)
        consolidated_report(str(id), cursor)
    cursor.close()
    db.close()
