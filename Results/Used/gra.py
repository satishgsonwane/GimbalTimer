# Data provided in text format
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import numpy as np

# Data extracted from the table (assumed from the image)
pan_values = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]
columns = ['1', '2', '3', '4', '5', '6', '7', '8']
data = [
    [3.6950, 3.7972, 4.6449, 4.7960, 4.9970, 6.2972, 6.7458, 8.0949],
    [3.8967, 4.5962, 4.8450, 5.8955, 6.5466, 6.5471, 8.0959, 7.9934],
    [3.2970, 3.1451, 3.6477, 4.1957, 5.6951, 5.9448, 6.8468, 7.9455],
    [3.6443, 3.6954, 3.8944, 5.2439, 4.9962, 5.8458, 6.7462, 7.4455],
    [3.7470, 3.9983, 4.1956, 4.2956, 4.8450, 5.5459, 6.3971, 6.8462],
    [2.5447, 2.8968, 4.1969, 4.9446, 5.6964, 6.0976, 6.2464, 7.2956],
    [2.1451, 3.1468, 3.0964, 3.7956, 4.3971, 6.3937, 6.5455, 7.2964],
    [1.3964, 1.5974, 2.1465, 2.6455, 3.0937, 3.6459, 4.2446, 4.8449],
    [1.1969, 1.5457, 1.9981, 2.5978, 2.9963, 3.5467, 4.0969, 4.6931],
    [0.9450, 1.2471, 1.6969, 2.2446, 2.5461, 3.2459, 3.5495, 4.1442]
]

# Create a DataFrame for easier handling
df = pd.DataFrame(data, index=pan_values, columns=columns)

# Plot line graphs for each column across the pan values
plt.figure(figsize=(12, 6))
for col in columns:
    plt.plot(pan_values, df[col], marker='o', label=f'Gimbal Speed {col}')

plt.gca().invert_xaxis()  # Match the decreasing pan values from the table
plt.title("Execution Time vs Delta Pan for Each Gimbal Speed")
plt.xlabel("Delta Pan")
plt.ylabel("Gimbal Speed")
plt.legend(title="Gimbal Speed", loc="upper right")
plt.grid(True)
plt.show()

# Plot heatmap of the values
# plt.figure(figsize=(10, 6))
# plt.imshow(df, cmap='viridis', aspect='auto', interpolation='nearest')
# plt.colorbar(label="Value Intensity")
# plt.title("Heatmap of Values")
# plt.xlabel("Gimbal Speed")
# plt.xticks(np.arange(len(columns)), columns)
# plt.ylabel("Delta Pan")
# plt.yticks(np.arange(len(pan_values)), pan_values)
# plt.gca().invert_yaxis()  # Match the pan values decreasing from top to bottom
# plt.show()

# Recreating the DataFrame
data_new = {
    "pan": [100, 30, 20, 10],
    "1": [3.70, 1.40, 1.20, 0.95],
    "2": [3.80, 1.60, 1.55, 1.25],
    "3": [4.64, 2.15, 2.00, 1.70],
    "4": [4.80, 2.65, 2.60, 2.24],
    "5": [5.00, 3.09, 3.00, 2.55],
    "6": [6.30, 3.65, 3.55, 3.25],
    "7": [6.75, 4.24, 4.10, 3.55],
    "8": [8.09, 4.84, 4.69, 4.14],
}
df_new = pd.DataFrame(data_new).set_index("pan")

# Plotting the data
# plt.figure(figsize=(12, 6))
# for col in df_new.columns:
#     plt.plot(df_new.index, df_new[col], marker='o', label=f'Column {col}')

# plt.gca().invert_xaxis()  # Match the decreasing pan values
# plt.title("Values vs Pan Settings for Each Column (New Data)")
# plt.xlabel("Pan")
# plt.ylabel("Values")
# plt.legend(title="Gimbal_Speed", loc="upper left")
# plt.grid(True)
# plt.show()

# Original data
original_pan = [100, 30, 20, 10]
new_pan = list(range(100, 30, -5)) + [30, 20, 10]  # Interpolating between 50 and 15, keeping original between 15 to 5

# Interpolating values for columns
df_interpolated = pd.DataFrame(index=new_pan, columns=df_new.columns)

# Interpolating for each column
for col in df_new.columns:
    interp_func = interp1d(original_pan, df_new[col], kind='linear', fill_value="extrapolate")
    df_interpolated[col] = interp_func(new_pan)

# Plot the interpolated data
plt.figure(figsize=(12, 6))
for col in df_interpolated.columns:
    plt.plot(df_interpolated.index, df_interpolated[col], marker='o', label=f'Gimbal Speed {col}')

plt.gca().invert_xaxis()  # Match the decreasing pan values
plt.title("Interpolated Values of Time taken vs Delta Pan for each Gimbal Speed")
plt.xlabel("Delta Pan")
plt.ylabel("Gimbal Speed")
plt.legend(title="Gimbal Speed", loc="upper right")
plt.grid(True)
plt.show()

