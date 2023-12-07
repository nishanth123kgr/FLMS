import pandas as pd
from from_csv.el_from_csv import convert_to_desired_format, remove_extra
from from_csv.el_from_csv import separate_prefix_suffix


def get_ml_mtl_lop(file, sheet_name):
    # Load Excel data into a DataFrame
    df = pd.read_excel(file, sheet_name=sheet_name)  # -1 selects the last sheet

    df = df.iloc[8:, 5:12]
    df = df.reset_index(drop=True)

    # Extract rows
    ml, mtl, lop, sl, eol = [], [], [], [], []
    for index, row in df.iterrows():
        row = list(map(str, row.fillna("NULL").tolist()))
        row = list(map(str.strip, row))
        leave_type = str(row[-1]).lower()
        row = row[:-1]
        row[0] = remove_extra(row[0])
        row[1] = remove_extra(row[1])
        row[5] = remove_extra(row[5])
        row = [convert_to_desired_format(str(date_str)) for date_str in row]
        row[4] = separate_prefix_suffix(row[0], row[1], row[4])
        if leave_type not in ["el", "-"]:
            if leave_type == "ml":
                ml.append(row)
            elif leave_type == "mtl":
                mtl.append(row)
            elif leave_type == "lop":
                lop.append(row)
            elif leave_type == "sl":
                sl.append(row)
            elif leave_type == "eol":
                eol.append(row)

    return ml, mtl, lop, sl, eol


if __name__ == "__main__":
    ml_data, mtl_data, lop_data, sl_data, eol_data = get_ml_mtl_lop("../Mrs. C . Jayalakshmi -29.11.2023.xlsx", 'EL')
    print(eol_data)
