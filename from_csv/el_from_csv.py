import pandas as pd
from datetime import datetime


def convert_to_desired_format(date_str):
    input_date_format = "%d.%m.%Y"

    try:
        parsed_date = datetime.strptime(date_str, input_date_format)
        converted_date_str = parsed_date.strftime("%Y-%m-%d")
        return converted_date_str
    except ValueError:
        return date_str


def get_el(file):
    # Load Excel data into a DataFrame
    df = pd.read_excel(file, sheet_name=-1)  # -1 selects the last sheet

    df.columns = df.iloc[6].fillna("_").tolist()
    df = df.iloc[7:, :5]
    df = df.reset_index(drop=True)

    # Extract rows starting from the 8th row
    data = []
    for i, row in df.iterrows():
        row = row.fillna("NULL").tolist()
        if not set(row).issubset({"NULL", "-"}):
            row[-1] = str(row[-1]).removesuffix("*") if row[-1] != "NULL" else row[-1]
            row = [convert_to_desired_format(date_str) for date_str in row]

            data.append(row)

    return data


if __name__ == "__main__":
    print(get_el("../faculty.xlsx"))
