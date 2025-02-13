import pandas as pd
import matplotlib.pyplot as plt
import math
from datetime import timedelta
import os

# Load the CSV file
csv_filename = 'query_results.csv'

if not os.path.exists(csv_filename):
    raise FileNotFoundError(f"{csv_filename} not found. Make sure it's in the same directory.")

# Read CSV into a DataFrame
df = pd.read_csv(csv_filename)

# Ensure 'timestamp' is in datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

# Exclude specific dut_pn values
excluded_dut_pn = ['1281-0277-2106', '1281-0277-2105', '3814-6535-1704']
df = df[~df['dut_pn'].isin(excluded_dut_pn)]

# Sort by dut_sn and timestamp for proper grouping
df = df.sort_values(by=['dut_sn', 'timestamp'])

# Function to group rows with the same dut_sn and timestamp within 1 second
def group_rows(df):
    groups = []
    current_group = [df.iloc[0]]
    
    for i in range(1, len(df)):
        prev_row = current_group[-1]
        current_row = df.iloc[i]
        
        # Check if the dut_sn is the same and timestamp difference is ≤ 1 second
        if current_row['dut_sn'] == prev_row['dut_sn'] and (current_row['timestamp'] - prev_row['timestamp']) <= timedelta(seconds=1):
            current_group.append(current_row)
        else:
            groups.append(pd.DataFrame(current_group))
            current_group = [current_row]
    
    # Add the last group
    if current_group:
        groups.append(pd.DataFrame(current_group))
    
    return groups

# Fix in the calculate_ratios function
def calculate_ratios(group):
    created_system = group[group['id'] == 'HeatingSeriesPowerCreatedTestSystem']
    consumed_system = group[group['id'] == 'HeatingSeriesPowerConsumedTestSystem']
    
    merged = pd.merge(created_system, consumed_system, on='seq', suffixes=('_created', '_consumed'))
    merged['cop'] = merged['value_created'] / merged['value_consumed']
    
    # Make an explicit copy to avoid SettingWithCopyWarning
    result = merged[['timestamp_created', 'seq', 'dut_sn_created', 'dut_pn_created', 'cop']].copy()
    result.rename(columns={
        'timestamp_created': 'timestamp',
        'dut_sn_created': 'dut_sn',
        'dut_pn_created': 'dut_pn'
    }, inplace=True)
    
    return result

# Group the data
grouped_data = group_rows(df)

# Process each group and calculate ratios
results = []
for group in grouped_data:
    ratio_df = calculate_ratios(group)
    if not ratio_df.empty:
        results.append(ratio_df)

# Combine all ratio results into a single DataFrame
final_result = pd.concat(results, ignore_index=True)

# Filter out lines where COP < 1 at seq = 100
# Identify DUT_SN values where COP >= 1 at seq = 100
valid_dut_sn = final_result.loc[(final_result['seq'] == 100) & (final_result['cop'] >= 1), 'dut_sn'].unique()

# Filter the final result to keep only valid DUT_SN values
final_result = final_result[final_result['dut_sn'].isin(valid_dut_sn)]

# Get unique dut_pn values
unique_dut_pns = sorted(final_result['dut_pn'].unique())

# Determine the grid size for subplots
num_plots = len(unique_dut_pns)
cols = 2  # Number of columns
rows = math.ceil(num_plots / cols)  # Number of rows

# Create subplots
fig, axes = plt.subplots(rows, cols, figsize=(14, 5 * rows))
axes = axes.flatten()  # Flatten for easy iteration

# Plotting
for ax, dut_pn in zip(axes, unique_dut_pns):
    group = final_result[final_result['dut_pn'] == dut_pn]
    for dut_sn, sn_group in group.groupby('dut_sn'):       
        # Skip lines where the seq is out of bounce
        if '1281-0277-21' in sn_group['dut_pn'].values:
            seq_top_limit = 400
        else:
            seq_top_limit = 350
        if sn_group['seq'].max() < 250 or sn_group['seq'].max() > seq_top_limit:
            continue
        
        # Remove  duplicates
        sn_group = sn_group.drop_duplicates(subset='seq')

        # Combine conditions and copy to avoid the warning
        sn_group = sn_group[
            (sn_group['cop'].between(0, 10)) &
            (sn_group['seq'].between(0, 300))
        ].copy()

        ax.plot(sn_group['seq'], sn_group['cop'], label=f'DUT_SN: {dut_sn}')
    
    ax.set_ylim(0, 11)
    ax.set_title(f'COP for DUT_PN: {dut_pn}', fontsize=10)
    ax.set_xlabel('Sequence')
    ax.set_ylabel('COP')
    ax.grid(True)
    # ax.legend(fontsize=5)

# Hide any unused subplots
for i in range(len(unique_dut_pns), len(axes)):
    fig.delaxes(axes[i])

plt.tight_layout()  # Adjust layout to prevent overlapping
plt.show()
