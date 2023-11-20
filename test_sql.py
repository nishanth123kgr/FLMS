import pandas as pd

# Sample DataFrame
data = {'Column1': [1, 2, 3, 4, 5],
        'Column2': ['A', 'B', 'C', 'D', 'E']}
df = pd.DataFrame(data)
print(df)

# Index from which you want to shift the rows down
index_to_shift_down = 2

# Number of positions to shift the rows
shift_distance = 1
df.loc[len(df)] = ''
# Shift the rows down from the specified index
df.iloc[index_to_shift_down+1:] = df.iloc[index_to_shift_down+1:].shift(periods=shift_distance)

# Fill NaN values in the first row after shifting
df.iloc[index_to_shift_down] = df.iloc[index_to_shift_down].fillna('')

# Insert an empty row at the end


# Reset the index if needed
df = df.reset_index(drop=True)

print(df)