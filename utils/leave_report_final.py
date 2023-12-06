import mysql.connector
import pandas as pd
import datetime
import ast
import xlsxwriter
import os

name = ''
doj = ''
dept = ''
leaved = ''


def set_staff_data(cursor, id):
    query = "select doj, name, department, leaved_date from staff where id=%s" % (id)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.reset()
    global name, doj, dept, leaved
    name = data[0][1]
    doj = data[0][0]
    dept = data[0][2]
    leaved = data[0][3]


leave_buffer = []


def leave_availed(cursor, id, type, from_date, to_date):
    query = (
            "SELECT `from`, `to` FROM %s WHERE id = %s AND `from` >= '%s' AND `from` <= '%s';"
            % (type, id, from_date, to_date)
    )
    cursor.execute(query)
    leaves = [[start, end, type] for start, end in cursor.fetchall()]
    cursor.reset()
    if len(leave_buffer) > 0:
        if from_date.year == leave_buffer[0][0].year:
            leaves.insert(0, [from_date.date(), leave_buffer[0][0], leave_buffer[0][1]])
            leave_buffer.pop()
    for i in range(len(leaves)):
        if pd.Timestamp(leaves[i][1]) > pd.Timestamp(to_date):
            leave_buffer.append([leaves[i][1], type])
            leaves[i] = [leaves[i][0], to_date.date(), type]

    # query = (
    #         "SELECT `from`, `to` FROM %s WHERE id = %s AND `from` >= '%s' AND `to` <= '%s';"
    #         % (type, id, from_date, to_date + dateutil.relativedelta.relativedelta(years=1))
    # )
    return leaves


def g(df, leaves, i):
    result = []
    if leaves:
        if leaves[0][0].strftime("%d-%m") != "01-07":
            result.append(
                {
                    "from": pd.to_datetime(df.at[i, "from"]).date(),
                    "to": leaves[0][0] - datetime.timedelta(days=1),
                    "type": 0,
                }
            )
        for j in range(1, len(leaves) + 1):
            result.append(
                {
                    "from": leaves[j - 1][0],
                    "to": leaves[j - 1][1],
                    "type": leaves[j - 1][2],
                }
            )
            if j < len(leaves):
                if ((leaves[j][0] - datetime.timedelta(days=1)) - (
                        leaves[j - 1][1] + datetime.timedelta(days=1))).days < 0:
                    continue
                result.append(
                    {
                        "from": leaves[j - 1][1] + datetime.timedelta(days=1),
                        "to": leaves[j][0] - datetime.timedelta(days=1),
                        "type": 0,
                    }
                )
        if pd.to_datetime(df.at[i, "to"]).date() != leaves[-1][1]:
            result.append(
                {
                    "from": leaves[-1][1] + datetime.timedelta(days=1),
                    "to": pd.to_datetime(df.at[i, "to"]).date(),
                    "type": 0,
                }
            )
    else:
        result.append(
            {
                "from": pd.to_datetime(df.at[i, "from"]).date(),
                "to": pd.to_datetime(df.at[i, "to"]).date(),
                "type": 0,
            }
        )

    return result


def calc_vl_prevented_total(to_date, staff_id, cursor, dt):
    year = to_date
    vl_id = f'{str(year - 1)[2:]}-{str(year)[2:]}'
    total_vl = 0
    total_period = 0
    for i in ['s', 'w']:
        query = 'select prevented from vl where vac_id=\'%s\' and staff_id=%s' % (vl_id + i, staff_id)
        cursor.execute(query)
        prevented = cursor.fetchall()
        cursor.reset()
        cursor.execute(f"select total_days from general_vacation_details where v_id='{vl_id + i}'")
        total_period += cursor.fetchone()[0]
        cursor.reset()
        if len(prevented) > 0:
            prevented = ast.literal_eval(prevented[0][0].decode('utf-8')) if not isinstance(prevented[0][0],
                                                                                            str) else eval(
                prevented[0][0])
            for i in prevented:
                if i[0] and i[1]:
                    from_date = datetime.datetime.strptime(i[0], '%Y-%m-%d')
                    to_date = datetime.datetime.strptime(i[1], '%Y-%m-%d')
                    total_vl += (to_date - from_date).days + 1
    vl_prevention = 60 - (total_period - total_vl)
    return round(vl_prevention / 3) if vl_prevention >= 0 else 0


def calculate_leave(id, cursor):
    set_staff_data(cursor, id)
    date_of_join = pd.to_datetime(doj)
    from_end = f"{datetime.datetime.now().year - 1}-07-01"
    to_end = f"{datetime.datetime.now().year}-06-30"
    if leaved:
        from_end = f'{leaved.year - 1 if leaved.month < 7 else leaved.year}-07-01'
        to_end = leaved
    from_date_range = pd.date_range(
        start=date_of_join,
        end=from_end,
        freq="AS-JUL",
    ).tolist()
    from_date_range.insert(0, date_of_join)
    date_range = pd.date_range(
        start=f"{date_of_join.year}-06-30",
        end=to_end,
        freq="A-JUN",
    )

    # Filter the date range based on date_of_join
    to_date_range = date_range[date_range > date_of_join]

    if leaved:
        to_date_range = to_date_range.tolist()
        to_date_range.append(leaved)
    df = pd.DataFrame({"from": from_date_range, "to": to_date_range})
    result = []
    for i in range(len(df)):
        leaves = []
        for type in ["el", "ml", "mtl", "lop"]:
            leaves.extend(
                leave_availed(cursor, id, type, df.at[i, "from"], df.at[i, "to"])
            )

        leaves = sorted(leaves, key=lambda x: x[0])
        result.extend(g(df.copy(), leaves, i))
    calc = pd.DataFrame(result, columns=["from", "to", "type"])
    calc["from"] = pd.to_datetime(calc["from"])
    calc["to"] = pd.to_datetime(calc["to"])

    calc["days_between"] = (calc["to"] - calc["from"]).dt.days + 1
    calc.loc[calc["type"] == 0, "*/11"] = (
            calc.loc[calc["type"] == 0, "days_between"] / 11
    )
    calc.loc[calc["type"] == 0, "*/11"] = calc.loc[calc["type"] == 0, "*/11"].apply(
        lambda x: int(round(x))
    )
    calc.loc[calc["type"] == 0, "*/18"] = (
            calc.loc[calc["type"] == 0, "days_between"] / 18
    )
    calc.loc[calc["type"] == 0, "*/18"] = calc.loc[calc["type"] == 0, "*/18"].apply(
        lambda x: int(round(x))
    )
    calc["*/11-*/18"] = calc["*/11"] - calc["*/18"]
    if leaved:
        calc["vl_prevented"] = calc["to"].apply(
            lambda x: calc_vl_prevented_total(x.year, id, cursor, x) if x == datetime.datetime(x.year, 6,
                                                                                               30) or x.strftime(
                "%d-%m-%Y") == (leaved.strftime("%d-%m-%Y") if leaved else False) else '-')
    else:
        calc["vl_prevented"] = calc["to"].apply(
            lambda x: calc_vl_prevented_total(x.year, id, cursor, x) if x == datetime.datetime(x.year, 6,
                                                                                               30) else '-')

    total = 0
    total_list = []
    for i in range(len(calc)):
        if calc.at[i, 'type'] == 0:
            total += calc.at[i, '*/11-*/18']

        else:
            if calc.at[i, 'type'] in ['el', 'lop']:
                total -= calc.at[i, 'days_between']
        calc.at[i, 'total'] = total
        total_list.append(total)
        if calc.at[i, 'vl_prevented'] != '-':
            total += calc.at[i, 'vl_prevented']
            total_list.append(total)

    calc = calc.fillna('')
    return calc, total_list


def gen_excel(data, id, workbook=None):
    worksheet = workbook.add_worksheet(name="Leave Calculation")
    cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
                                       'border_color': 'black'})
    date_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
                                       'border_color': 'black', 'num_format': 'dd-mm-yyyy'})
    bold_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
                                       'border_color': 'black'})
    el_format = workbook.add_format(
        {'bold': True, 'bg_color': '#FFFF00', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black'})
    ml_format = workbook.add_format(
        {'bold': True, 'bg_color': '#00FF00', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black'})
    mtl_format = workbook.add_format(
        {'bold': True, 'bg_color': '#009eff', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black'})
    lop_format = workbook.add_format(
        {'bold': True, 'bg_color': '#ff00fe', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black'})
    el_date_format = workbook.add_format(
        {'bold': True, 'bg_color': '#FFFF00', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black', 'num_format': 'dd-mm-yyyy'})
    ml_date_format = workbook.add_format(
        {'bold': True, 'bg_color': '#00FF00', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black', 'num_format': 'dd-mm-yyyy'})
    mtl_date_format = workbook.add_format(
        {'bold': True, 'bg_color': '#009eff', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black', 'num_format': 'dd-mm-yyyy'})
    lop_date_format = workbook.add_format(
        {'bold': True, 'bg_color': '#ff00fe', 'align': 'center', 'valign': 'vcenter', 'border': 1,  # 1-pt border
         'border_color': 'black', 'num_format': 'dd-mm-yyyy'})

    leave_date_format = {
        "el": el_date_format,
        "ml": ml_date_format,
        "mtl": mtl_date_format,
        "lop": lop_date_format
    }
    leave_format = {
        "el": el_format,
        "ml": ml_format,
        "mtl": mtl_format,
        "lop": lop_format
    }
    details_rows = 3
    worksheet.write(0, 0, "Name", cell_format)
    worksheet.merge_range("B1:E1", name, cell_format)
    worksheet.write(1, 0, "Date of Joining", cell_format)
    worksheet.merge_range("B2:E2", doj.strftime("%d-%m-%Y"), cell_format)
    worksheet.write(2, 0, "Campus", cell_format)
    worksheet.merge_range("B3:E3", "Anna University Regional Campus - Tirunelveli", cell_format)
    headers = ["Type of Leave", '', '', '', '*/11', '*/18', '*/11-*/18', 'Total']

    worksheet.write_row(details_rows, 0, headers, bold_format)
    cell_format.set_bold(False)
    worksheet.set_default_row(25)
    worksheet.set_column(0, 0, 15)
    worksheet.set_column(0, 1, 15)
    worksheet.set_column(0, 2, 15)
    data["*/11"] = data["*/11"].apply(lambda x: int(x) if x != '' else x)
    data["*/18"] = data["*/18"].apply(lambda x: int(x) if x != '' else x)
    data["*/11-*/18"] = data["*/11-*/18"].apply(lambda x: int(x) if x != '' else x)
    data["total"] = data["total"].apply(lambda x: int(x) if x != '' else x)
    rows = []
    for i in range(len(data)):
        row_values = data.iloc[i].copy().tolist()
        rows.append(row_values)
        if data.at[i, 'to'].strftime("%d-%m") == '30-06' or i == len(data) - 1:
            rows.append(["Add Vacation", f'{data["to"].iloc[i].year - 1}-{data["to"].iloc[i].year}', '',
                         data.at[i, 'vl_prevented'],
                         '', '', '', '', data.at[i, 'vl_prevented'] + data.at[i, 'total']])
    data = pd.DataFrame(rows, columns=["from", "to", "type", "days", "/11", "/18", "/11-/18", "vl", "total"])
    data = data.drop('vl', axis=1)
    for i in range(len(data)):
        row = data.iloc[i].tolist()
        if row[2] == 0:
            worksheet.write_row(i + 4, 0, [row[0], row[1]], date_format)
            worksheet.write_row(i + 4, 2,
                                ['',
                                 f'=B{i + 5}-A{i + 5}+1',
                                 f'=ROUND(D{i + 5}/11,0)',
                                 f'=ROUND(D{i + 5}/18,0)',
                                 f'=E{i + 5}-F{i + 5}'] + [
                                    '=G5' if i == 0 else f'=H{i + 4}+G{i + 5}'],

                                cell_format)
        elif row[2] in ['el', 'ml', 'mtl', 'lop']:
            worksheet.write(i + 4, 0, row[2].upper(), leave_format[row[2]])
            worksheet.write_row(i+4, 1, [row[0], row[1]], leave_date_format[row[2]])
            worksheet.write_row(i + 4, 3,
                                [
                                    f'=C{i + 5}-B{i + 5}+1'] + row[4:-1] + [
                                    '=D5' if i == 0 else (f'=H{i + 4}-D{i + 5}' if row[2] == 'el' else f'=H{i + 4}')],
                                leave_format[row[2]])
        else:
            worksheet.write_row(i + 4, 0, row[:-1] + [f'=H{i + 4}+D{i + 5}'], bold_format)


def generate_consolidated_report(id, cursor, workbook):
    data, total = calculate_leave(id, cursor)
    gen_excel(data, id, workbook)


if __name__ == "__main__":
    db = mysql.connector.connect(
        host="localhost", port="3306", user="root", database="facultyleavedb"
    )
    cursor = db.cursor()
    # ids = [12222, 12223, 12224, 25001, 25005, 25007, 25009, 25010, 25012, 25013, 25019, 25030, 13331, 13332, 13333,
    #        27002]
    # ids = [30002, 20003, 30003, 45000, 45001]
    # ids = [24001, 24003]
    # ids = [26001, 55555]
    # ids = [13333] + [12222, 12223, 12224, 25001, 25005, 25007, 25009, 25010, 25012, 25013, 25019, 25030, 13331, 13332,
    #                  13333, 27002] + [30002, 20003, 30003, 45000, 45001] + [26001, 55555] + [10001, 21002, 21003, 21010,
    #                                                                                         66661] + [24001, 24003]
    # ids = [21002, 21003, 21010] #Civil
    # ids = [20003, 29007, 30002, 30003, 45000] # SNH
    # ids = [22003, 22222, 22007, 22223, 22015, 22019]  # CSE
    # ids = [24001, 24003] #ECE
    # ids = [26001, 55555, 55551] # MBA
    # ids = [13331, 13332, 27002]  # MCA
    # ids = [25030, 25012, 25009, 12223, 25010, 25005, 12222, 25019, 25007, 25001]  # MECH
    # ids = [32546, 22021]
    ids = [22003]
    for i in ids:
        workbook = xlsxwriter.Workbook(f'./new/{i}.xlsx')
        generate_consolidated_report(i, cursor, workbook)
        workbook.close()
