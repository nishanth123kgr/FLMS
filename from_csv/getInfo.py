import pandas as pd


def get_info(file):
    df = pd.read_excel(file, sheet_name="all leave details", header=None)
    info = df.iloc[6, 1:6].tolist()
    info = dict(zip(["name", "id", "designation", "department", "doj"], info))
    return info


if __name__ == "__main__":
    print(get_info("../faculty.xlsx"))
