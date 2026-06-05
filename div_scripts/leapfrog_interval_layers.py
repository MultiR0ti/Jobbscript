import pandas as pd
import openpyxl

# Read in data
filepath = r"C:\Users\jdr\Downloads\interval-03.02.26.csv"

df = pd.read_csv(filepath, sep=',', decimal='.')


# Initialize a dictionary to keep track of geology counts for each Borepoint
geology_counts = {}

# Function to update Geology column
def update_geology(row):
    borepoint = row['Borepoint']
    geology = row['Geology']
    count = geology_counts.get((borepoint, geology), 0) + 1
    geology_counts[(borepoint, geology)] = count
    return f'{geology} {count}'

# Apply the update_geology function to the DataFrame
df['Geology'] = df.apply(update_geology, axis=1)

# Save the updated DataFrame to a new CSV file
df.to_csv(r"C:\Users\jdr\Downloads\interval-03.02.26_lagnummer.csv", index=False)