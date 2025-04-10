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

# Include specific dut_sn values
# only_dut_sn = ['SN-LY4P-R9JY', 'SN-JYV2-K5LY', 'SN-6YXP-RR8Y', 'SN-N70N-8K27', 'SN-LY3E-4PVY', 'SN-N70N-8K27', 'SN-N70N-0M27', 'SN-6YXP-RR8Y', 'SN-PYP5-5V37']
# df = df[df['dut_sn'].isin(only_dut_sn)]

# Exclude specific dut_pn values
# excluded_dut_pn = ['1281-0277-2106', '1281-0277-2105', '3814-6535-1704']
# df = df[~df['dut_pn'].isin(excluded_dut_pn)]

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
    
    print(len(sub_groups))
    
    for (dut_sn, timestamp), sub_data in sub_groups:
       
        # Adjust the plot range depending on the DUT PN
        if '1281-0277-21' in sub_data['dut_pn']:
            seq_top_limit = 400
        else:
            seq_top_limit = 350
        
        # Skip lines where the seq is out of bounce
        if sub_data['seq'].max() < 250 or sub_data['seq'].max() > seq_top_limit:
            continue

        # Plot up to 300 sequences
        sub_data = sub_data[(sub_data['seq'] >= 0) & (sub_data['seq'] <= 300)]

        # Plotting the valid lines
        label = f'{dut_sn} - {timestamp}'  # Label for the line
        ax.plot(sub_data['seq'], sub_data['value'], label=label)
        
        # Extend plot range depending on content
        if sub_data['id'].max() == 'HeatingSeriesPowerConsumedTestSystem':
            plot_range = 4000
        else:
            plot_range = 13000

    # Plot formatting
    ax.set_ylim(0, plot_range)
    ax.set_title(f'DUT_PN: {dut_pn}, ID: {id}', fontsize=10)
    ax.set_xlabel('Sequence')
    ax.set_ylabel('Watts')
    ax.grid(True)
    ax.legend(fontsize=5)

plt.tight_layout()  # Adjust layout to prevent overlapping
plt.show()
