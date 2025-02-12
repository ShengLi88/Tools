import pandas as pd
import matplotlib.pyplot as plt
import math
import os

# Load the CSV file
csv_filename = 'query_results.csv'

if not os.path.exists(csv_filename):
    raise FileNotFoundError(f"{csv_filename} not found. Make sure it's in the same directory.")

# Read CSV into a DataFrame
df = pd.read_csv(csv_filename)

# Verify the expected columns exist
expected_columns = {'timestamp', 'seq', 'dut_sn', 'dut_pn', 'id', 'value'}
if not expected_columns.issubset(df.columns):
    raise ValueError(f"CSV file is missing one or more expected columns: {expected_columns}")

# Exclude specific dut_sn values
excluded_dut_sn = ['SN-', 'SN-']  # Add the DUT_SN values you want to exclude
df = df[~df['dut_sn'].isin(excluded_dut_sn)]  # Exclude the specified DUT_SN values

# Group by 'dut_pn' and 'id' for subplots
grouped = df.groupby(['dut_pn', 'id'])

# Determine the grid size for subplots
num_plots = len(grouped)
cols = 2  # Number of columns
rows = math.ceil(num_plots / cols)  # Number of rows

# Create a figure with subplots
fig, axes = plt.subplots(rows, cols, figsize=(24, 6 * rows))
axes = axes.flatten()  # Flatten for easy iteration

# Plotting
for ax, ((dut_pn, id), group_data) in zip(axes, grouped):
    # Further group by 'dut_sn' and 'timestamp' for separate lines
    sub_groups = group_data.groupby(['dut_sn', 'timestamp'])
    
    for (dut_sn, timestamp), sub_data in sub_groups:
        sub_data = sub_data.sort_values(by='seq')  # Sort by 'seq'
        
        # Filter out lines where the value at seq=20 is < 500
        seq_20_value = sub_data.loc[sub_data['seq'] == 20, 'value']
        if seq_20_value.empty or seq_20_value.values[0] < 200:
            continue  # Skip this line if the condition is not met

        # Plotting the valid lines
        label = f'{dut_sn} - {timestamp}'  # Label for the line
        ax.plot(sub_data['seq'], sub_data['value'], marker='o', label=label)

    # Plot formatting
    ax.set_title(f'DUT_PN: {dut_pn}, ID: {id}', fontsize=10)
    ax.set_xlabel('Sequence')
    ax.set_ylabel('Value')
    ax.grid(True)
    ax.legend(fontsize=5)  # Add legend to differentiate lines

# Hide any unused subplots
for i in range(len(grouped), len(axes)):
    fig.delaxes(axes[i])

plt.tight_layout()  # Adjust layout to prevent overlapping
plt.show()
