import pandas as pd


def get_ml_mtl_lop(file):
    # Load Excel data into a DataFrame
    df = pd.read_excel(file, sheet_name=-1)  # -1 selects the last sheet

    df.columns = df.iloc[6].fillna("_").tolist()
    df = df.iloc[7:, 5:12]
    df = df.reset_index(drop=True)

    # Extract rows
    ml, mtl, lop = [], [], []
    for index, row in df.iterrows():
        row = row.fillna("NULL").tolist()
        leave_type = str(row[-1]).lower()
        row = row[:-1]
        if leave_type not in ["el", "-"]:
            if leave_type == "ml":
                ml.append(row)
            elif leave_type == "mtl":
                mtl.append(row)
            elif leave_type == "lop":
                lop.append(row)

    return ml, mtl, lop


if __name__ == "__main__":
    ml_data, mtl_data, lop_data = get_ml_mtl_lop("../faculty.xlsx")
    print(ml_data)
