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
    print(workbook)
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
    consolidated_report(id, cursor)
    cursor.close()
    db.close()
