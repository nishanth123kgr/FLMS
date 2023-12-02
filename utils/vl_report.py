import ast
import os
from datetime import datetime

import mysql.connector
import pandas as pd
import xlsxwriter


def get_vl_details(id, cursor):
    cursor.execute(f"select `vac_id`,  `prevented` from vl where staff_id={id}")
    prevented_details = cursor.fetchall()
    cursor.reset()

    cursor.execute(f"select `vac_id`, `availed_from`, `availed_to` from vl where staff_id={id}")
    availed_details = cursor.fetchall()
    cursor.reset()

    return prevented_details, availed_details


def parse_json(data):
    for i in range(len(data)):
        data[i] = list(data[i])
        for j in range(1, len(data[i])):
            if data[i][j] is None:
                continue
            if data[i][j] == "NULL":
                data[i][j] = None
                continue
            data[i][j] = ast.literal_eval(data[i][j])

    return data


def generate_df(vl_data):
    result = []
    for i in vl_data:
        result.append({
            "year": i[0],

        })


def split_prevented_from_to(data):
    df_new = []
    for i in range(len(data)):
        for j in range(len(data.at[i, 'Prevented'])):
            df_new.append([data.at[i, 'Year'], data.at[i, 'Prevented'][j][0], data.at[i, 'Prevented'][j][1]])
    return pd.DataFrame(df_new, columns=['Year', 'Prevented From', 'Prevented To'])


def split_availed_from_to(data):
    df_new = []
    for i in range(len(data)):
        if data.at[i, 'Availed From'] is None and data.at[i, 'Availed To'] is None:
            continue
        for from_date, to_date in zip(data.at[i, 'Availed From'], data.at[i, 'Availed To']):
            df_new.append([data.at[i, 'Year'], from_date, to_date])
    return pd.DataFrame(df_new, columns=['Year', 'Availed From', 'Availed To'])


def group_to_dict(group):
    group_dict = {
        "year": group['Year'],
        'from': group['from'],
        'to': group['to'],
    }
    return group_dict


def get_general_details(id, cursor):
    cursor.execute(
        f"select v_id, `from`, `to` from general_vacation_details where v_id in (select vac_id from vl where staff_id={id})")
    df = pd.DataFrame(cursor.fetchall(), columns=['Year', 'from', 'to'])
    cursor.reset()
    return df


def generate_excel(data, id, name, dept, doj, workbook):
    worksheet = workbook.add_worksheet("VL")
    worksheet.set_column('A:L', 12)

    merge_ranges = [
        (2, 0, 2, 3),
        (2, 4, 2, 12),
        (3, 0, 3, 3),
        (3, 4, 3, 12),
        (4, 0, 4, 3),
        (4, 4, 4, 12),
        (5, 0, 5, 3),
        (5, 4, 5, 12),
        (6, 0, 6, 3),
        (6, 4, 6, 12),
        (7, 0, 7, 12),
        (8, 0, 8, 4),
        (8, 5, 8, 10)

    ]
    cell_format_center = workbook.add_format({
        'align': 'center',  # Center alignment
        'text_wrap': True,  # Wrap text
        'valign': 'vcenter',  # Center vertically
        'border': 1
    })
    cell_format_left = workbook.add_format({
        'align': 'left',  # Center alignment
        'text_wrap': True,  # Wrap text
        'valign': 'vcenter',  # Center vertically
        'border': 1
    })

    # Perform the defined merges
    worksheet.merge_range(*(0, 0, 0, 12), 'Annexure -II', cell_format_center)
    worksheet.merge_range(*(1, 0, 1, 12), 'Anna University chennai', cell_format_center)
    worksheet.merge_range(*merge_ranges[0], 'Name', cell_format_left)
    worksheet.merge_range(*merge_ranges[1], name, cell_format_left)
    worksheet.merge_range(*merge_ranges[2], 'Designation', cell_format_left)
    worksheet.merge_range(*merge_ranges[3], '', cell_format_left)
    worksheet.merge_range(*merge_ranges[4], 'Department', cell_format_left)
    worksheet.merge_range(*merge_ranges[5], dept, cell_format_left)
    worksheet.merge_range(*merge_ranges[6], 'Date of joining in service', cell_format_left)
    worksheet.merge_range(*merge_ranges[7], doj.strftime('%d-%m-%Y'), cell_format_left)
    worksheet.merge_range(*merge_ranges[8], 'Campus', cell_format_left)
    worksheet.merge_range(*merge_ranges[9], 'ANNA UNIVERSITY REGIONAL CAMPUS   -   TIRUNELVELI', cell_format_left)
    worksheet.merge_range(*merge_ranges[10], 'Details of Vacation', cell_format_center)

    worksheet.merge_range("B9:M9", "Vacation", cell_format_center)
    worksheet.merge_range("A9:A11", "Year", cell_format_center)
    worksheet.merge_range("B10:E10", "Period of Vacation", cell_format_center)
    worksheet.merge_range("F10:I10", "Vacation Availed", cell_format_center)
    worksheet.merge_range("J10:M10", "Vacation Prevention", cell_format_center)
    worksheet.write("B11", "Summer / Winter", cell_format_center)
    worksheet.write("C11", "From", cell_format_center)
    worksheet.write("D11", "To", cell_format_center)
    worksheet.write("E11", "Total", cell_format_center)
    worksheet.write("F11", "From", cell_format_center)
    worksheet.write("G11", "To", cell_format_center)
    worksheet.write("H11", "Total", cell_format_center)
    worksheet.write("I11", "Year Total", cell_format_center)
    worksheet.write("J11", "From", cell_format_center)
    worksheet.write("K11", "To", cell_format_center)
    worksheet.write("L11", "Total", cell_format_center)
    worksheet.write("M11", "Year Total", cell_format_center)

    row = 12
    sums = [0, 0, 0]
    for year, values in data.items():
        from_date = values[0]['from']
        to_date = values[0]['to']
        if year[-1] == 'W' or row == 12:
            sums[0] = row
        props = [row, 0, 0]
        for items in values:
            avail_sum = (datetime.strptime(items['Availed To'], "%Y-%m-%d") - datetime.strptime(items['Availed From'],
                                                                                                "%Y-%m-%d")).days + 1 if \
                items['Availed From'] not in ['', 'NULL'] and items['Availed To'] not in ['', 'NULL'] else 0
            preven_sum = (datetime.strptime(items['Prevented To'], "%Y-%m-%d") - datetime.strptime(
                items['Prevented From'],
                "%Y-%m-%d")).days + 1 if \
                items['Prevented From'] not in ['', 'NULL'] and items['Prevented To'] not in ['', 'NULL'] else 0
            props[1] += avail_sum
            props[2] += preven_sum
            worksheet.write(f"F{row}", items['Availed From'] if items['Availed From'] not in ['', 'NULL'] else '-',
                            cell_format_center)
            worksheet.write(f"G{row}", items['Availed To'] if items['Availed To'] not in ['', 'NULL'] else '-',
                            cell_format_center)
            worksheet.write(f"H{row}", avail_sum if avail_sum else '-', cell_format_center)
            worksheet.write(f"J{row}", items['Prevented From'] if items['Prevented From'] not in ['', 'NULL'] else '-',
                            cell_format_center)
            worksheet.write(f"K{row}", items['Prevented To'] if items['Prevented To'] not in ['', 'NULL'] else '-',
                            cell_format_center)
            worksheet.write(f"L{row}", preven_sum if preven_sum else '-', cell_format_center)

            row += 1
        sums[1] += props[1]
        sums[2] += props[2]
        if year[-1] == 'S' or list(data.items())[-1] == (year, values):
            if sums[0] == row - 1:
                worksheet.write(f"I{sums[0]}", sums[1], cell_format_center)
                worksheet.write(f"M{sums[0]}", sums[2], cell_format_center)
                worksheet.write(f'A{sums[0]}', f'20{year[:2]}-20{year[3:5]}', cell_format_center)
            else:
                worksheet.merge_range(f'I{sums[0]}:I{row - 1}', sums[1], cell_format_center)
                worksheet.merge_range(f'M{sums[0]}:M{row - 1}', sums[2], cell_format_center)
                worksheet.merge_range(f'A{sums[0]}:A{row - 1}', f'20{year[:2]}-20{year[3:5]}', cell_format_center)
            sums = [0, 0, 0]

        from_date = datetime.strptime(from_date, "%Y-%m-%d") if from_date else '-'
        to_date = datetime.strptime(to_date, "%Y-%m-%d") if to_date else '-'
        if props[0] == row - 1:
            worksheet.write(f"C{props[0]}", from_date.strftime("%d-%m-%Y") if from_date != '-' else '-',
                            cell_format_center)
            worksheet.write(f"D{props[0]}", to_date.strftime("%d-%m-%Y") if to_date != '-' else '-',
                            cell_format_center)
            if from_date != '-' and to_date != '-':
                worksheet.write(f"E{props[0]}", (to_date - from_date).days + 1, cell_format_center)
        else:
            worksheet.merge_range(f"C{props[0]}:C{row - 1}",
                                  from_date.strftime("%d-%m-%Y") if from_date != '-' else '-',
                                  cell_format_center)
            worksheet.merge_range(f"D{props[0]}:D{row - 1}", to_date.strftime("%d-%m-%Y") if to_date != '-' else '-',
                                  cell_format_center)
            if from_date != '-' and to_date != '-':
                worksheet.merge_range(f"E{props[0]}:E{row - 1}", (to_date - from_date).days + 1 if from_date else '-',
                                      cell_format_center)
        if year[-1] == 'W':
            if props[0] == row - 1:
                worksheet.write(f"B{props[0]}", 'Winter', cell_format_center)
            else:
                worksheet.merge_range(f"B{props[0]}:B{row - 1}", "Winter", cell_format_center)
        else:
            if props[0] == row - 1:
                worksheet.write(f"B{props[0]}", 'Summer', cell_format_center)
            else:
                worksheet.merge_range(f"B{props[0]}:B{row - 1}", "Summer", cell_format_center)


def convert_data(data):
    data = data.fillna("")
    data = data.T.to_dict()
    converted_data = {}
    for key, value in data.items():
        year_key = key[0]
        if year_key not in converted_data:
            converted_data[year_key] = []
        if value['from'] is not None and value['from']:
            value['from'] = value['from'].strftime("%Y-%m-%d")
        if value['from'] is not None and value['from']:
            value['to'] = value['to'].strftime("%Y-%m-%d")
        converted_data[year_key].append(value)
    return converted_data


def get_staff_details(id, cursor):
    cursor.execute(f"select `name`, `department`, `doj` from staff where id={id}")
    name, dept, doj = cursor.fetchone()
    return name, dept, doj


def generate_vl(id, cursor, workbook):
    name, dept, doj = get_staff_details(id, cursor)
    prevention, availed = get_vl_details(id, cursor)
    general_details = get_general_details(id, cursor)
    general_details["Year"] = general_details["Year"].apply(
        lambda x: x[:-1] + f"{'w' if x[-1] == 's' else 'a'}{x[-1].upper()}")
    prevention = pd.DataFrame(parse_json(prevention), columns=['Year', 'Prevented'])
    prevention["Year"] = prevention["Year"].apply(lambda x: x[:-1] + f"{'w' if x[-1] == 's' else 'a'}{x[-1].upper()}")
    availed = pd.DataFrame(parse_json(availed), columns=['Year', 'Availed From', 'Availed To'])
    availed["Year"] = availed["Year"].apply(lambda x: x[:-1] + f"{'w' if x[-1] == 's' else 'a'}{x[-1].upper()}")
    prevention = split_prevented_from_to(prevention).groupby('Year').apply(lambda x: x.reset_index(drop=True))
    prevention.drop(['Year'], axis=1, inplace=True)
    availed = split_availed_from_to(availed).groupby('Year').apply(lambda x: x.reset_index(drop=True))
    availed.drop(['Year'], axis=1, inplace=True)
    general_details = general_details.groupby('Year').apply(lambda x: x.reset_index(drop=True))
    general_details.drop(['Year'], axis=1, inplace=True)

    new1 = pd.concat([general_details, availed, prevention], axis=1, join='outer').sort_index()
    data = convert_data(new1)
    generate_excel(data, id, name, dept, doj, workbook)


if __name__ == "__main__":
    id = 22019
    db = mysql.connector.connect(
        host="localhost", port="3306", user="root", database="facultyleavedb"
    )
    cursor = db.cursor()
    workbook = xlsxwriter.Workbook(f'VL/{id}_VL.xlsx')
    generate_vl(id, cursor, workbook)
    workbook.close()
    cursor.close()
