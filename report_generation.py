import json
import uuid
import datetime
import xlsxwriter


def generate_report(cursor, id):
    def with_permission_fun(from_prefix, to_prefix, from_suffix, to_suffix):
        prefix = []
        if from_prefix and to_prefix:
            prefix.append(f"{from_prefix.strftime('%d-%m-%Y')} to {to_prefix.strftime('%d-%m-%Y')}")
        elif not from_prefix and to_prefix:
            prefix.append(f"{to_prefix.strftime('%d-%m-%Y')}")
        elif from_prefix and not to_prefix:
            prefix.append(f"{from_prefix.strftime('%d-%m-%Y')}")

        suffix = []
        if from_suffix and to_suffix:
            suffix.append(f"{from_suffix.strftime('%d-%m-%Y')} to {to_suffix.strftime('%d-%m-%Y')}")
        elif not from_suffix and to_suffix:
            suffix.append(f"{to_suffix.strftime('%d-%m-%Y')}")
        elif from_suffix and not to_suffix:
            suffix.append(f"{from_suffix.strftime('%d-%m-%Y')}")

        on_permission = []
        if prefix and suffix:
            on_permission.append(f"{prefix[0]} & {suffix[0]}")
        elif not prefix and suffix:
            on_permission.append(suffix[0])
        elif prefix and not suffix:
            on_permission.append(prefix[0])

        return on_permission

    def getdata(type, id):
        if type == 'el':
            cursor.reset()
            query = "SELECT `from`, `to`, `from_prefix`, `to_prefix`, `from_suffix`, `to_suffix`, `date_of_rejoin`, `total` FROM " + type + " WHERE id=" + id + "; "
            cursor.execute(query)
            data = cursor.fetchall()
            data_final = [sublist + (type,) for sublist in data]
            on_permission = []
            for i in data_final:
                on_permission.append(with_permission_fun(i[2], i[3], i[4], i[5]))
            data_final_updated = []
            for i, sublist in enumerate(data_final):
                columns_to_keep = sublist[:2] + (on_permission[i],) + sublist[6:]
                data_final_updated.append(columns_to_keep)
            return data_final_updated
        else:
            cursor.reset()
            query = "SELECT `from`,`to`,`total`, `medical_fittness_on`, `from_prefix`, `to_prefix`, `from_suffix`, `to_suffix`, `doj` FROM " + type + " WHERE id=" + id + ";; "
            cursor.execute(query)
            data5 = cursor.fetchall()
            data_final = [sublist + (type,) for sublist in data5]
            on_permission = []
            for i in data_final:
                on_permission.append(with_permission_fun(i[4], i[5], i[6], i[7]))

            data_final_updated = []
            for i, sublist in enumerate(data_final):
                columns_to_keep = sublist[:4] + (on_permission[i],) + sublist[8:]
                data_final_updated.append(columns_to_keep)
            return data_final_updated

    def generate_random_name():
        random_uuid = str(uuid.uuid4())

        random_name = random_uuid[:8]
        return random_name

    query = "SELECT * FROM `staff` WHERE id=" + id + ";"
    cursor.execute(query)
    data = cursor.fetchall()
    data_el = getdata('el', '22015')
    data_ml = getdata('ml', '22015')
    data_lop = getdata('lop', '22015')
    data_mtl = getdata('mtl', '22015')
    sorted_data = sorted(data_lop + data_el + data_ml + data_mtl, key=lambda x: x[0])
    xlname = generate_random_name()
    workbook = xlsxwriter.Workbook("static/reports/" + xlname + '.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.set_column('A:M', 12)

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

    })
    cell_format_left = workbook.add_format({
        'align': 'center',  # Center alignment
        'text_wrap': True,  # Wrap text

    })

    # Perform the defined merges
    worksheet.merge_range(*(0, 0, 0, 12), 'Annexure -II', cell_format_center)
    worksheet.merge_range(*(1, 0, 1, 12), 'Anna univeristy chennai', cell_format_center)
    worksheet.merge_range(*merge_ranges[0], 'Name', cell_format_center)
    worksheet.merge_range(*merge_ranges[1], data[0][1], cell_format_left)
    worksheet.merge_range(*merge_ranges[2], 'Designation', cell_format_left)
    worksheet.merge_range(*merge_ranges[3], '', cell_format_left)
    worksheet.merge_range(*merge_ranges[4], 'Department', cell_format_left)
    worksheet.merge_range(*merge_ranges[5], data[0][2], cell_format_left)
    worksheet.merge_range(*merge_ranges[6], 'Date of joining in service', cell_format_left)
    worksheet.merge_range(*merge_ranges[7], data[0][3].strftime('%d-%m-%Y'), cell_format_left)
    worksheet.merge_range(*merge_ranges[8], 'Campus', cell_format_left)
    worksheet.merge_range(*merge_ranges[9], 'ANNA UNIVERSITY REGIONAL CAMPUS   -   TIRUNELVELI', cell_format_center)
    worksheet.merge_range(*merge_ranges[10], 'DETAILS OF LEAVE', cell_format_left)
    worksheet.merge_range(*merge_ranges[11], 'Earned Leave  (EL)', cell_format_left)
    worksheet.merge_range(*merge_ranges[12], 'Medical Leave  (ML)  /  Maternity Leave  (MTL) / Loss of pay (LOP)',
                          cell_format_left)
    worksheet.write('L9', 'Type of Leave', cell_format_left)
    worksheet.write('M10', 'Remarks', cell_format_left)

    head_list = [['From', 'To', 'with permission on', 'Date of Joining on Duty after EL', 'Total No. of Days',
                  'From', 'To', 'Total No. of Days', 'Medical Fitness on', 'with permission on',
                  'Date of Joining on Duty after leave', '(ML/ EL/LOP/MTL)']
                 ]

    # Define the starting row
    start_row = 9

    # Iterate through each sublist and its values
    for sublist in head_list:
        column_index = 0  # Start writing from the first column
        for value in sublist:
            worksheet.write(start_row, column_index, value, cell_format_left)
            column_index += 1  # Move to the next column for the next value
        start_row += 1

    start_row = 10
    for sublist in sorted_data:
        # Start writing from the first column
        if sublist[-1] == 'el':
            column_index = 0
            for value in sublist:
                if value == 'el':
                    worksheet.write(start_row, 11, value, cell_format_left)
                elif isinstance(value, datetime.date):

                    worksheet.write(start_row, column_index, value.strftime('%d-%m-%Y'), cell_format_left)
                    column_index += 1
                elif isinstance(value, list):
                    if value:
                        worksheet.write(start_row, column_index, value[0], cell_format_left)
                    else:

                        worksheet.write(start_row, column_index, "Nil", cell_format_left)

                    column_index += 1

                elif isinstance(value, bytes):
                    byte_data = value
                    byte_data_str = byte_data.decode('utf-8')
                    str_data = json.loads(byte_data_str)
                    worksheet.write(start_row, column_index, str_data[0], cell_format_left)
                    column_index += 1
                else:
                    worksheet.write(start_row, column_index, value, cell_format_left)
                    column_index += 1  # Move to the next column for the next value
            for i in range(column_index, 11):
                worksheet.write(start_row, i, "-", cell_format_center)

            start_row += 1
        else:
            column_index = 5
            for value in sublist:
                if value == 'lop' or value == 'mtl' or value == 'ml':
                    print(value)
                    worksheet.write(start_row, 11, value, cell_format_left)
                elif isinstance(value, datetime.date):
                    worksheet.write(start_row, column_index, value.strftime('%d-%m-%Y'), cell_format_left)
                    column_index += 1

                elif isinstance(value, bytes):
                    byte_data = value
                    byte_data_str = byte_data.decode('utf-8')
                    str_data = json.loads(byte_data_str)
                    formatted_date = datetime.datetime.strptime(str_data[0], "%Y-%m-%d")
                    worksheet.write(start_row, column_index, formatted_date.strftime('%d-%m-%Y'), cell_format_left)
                    column_index += 1

                elif isinstance(value, list):
                    if value:
                        worksheet.write(start_row, column_index, value[0], cell_format_left)
                    else:
                        worksheet.write(start_row, column_index, "Nil", cell_format_left)
                    column_index += 1


                else:
                    worksheet.write(start_row, column_index, value, cell_format_left)
                    column_index += 1  # Move to the next column for the next value
            for i in range(0, 5):
                worksheet.write(start_row, i, "-", cell_format_center)

            start_row += 1

    workbook.close()
    return xlname
