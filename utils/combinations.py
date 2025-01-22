import csv

# Define the ranges
camera_ids = range(1, 7)  # 1 to 6
gimbal_speeds = range(1, 9)  # 1 to 8
pan_values = list(range(-55, 56, 10)) + list(range(55, -56, -10))  # -55 to 55 and 55 to -55 in steps of 10

# Open a CSV file for writing
with open('camera_combinations.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Write the header row
    writer.writerow(['camera_id', 'gimbal_speed', 'Pan'])
    
    # Generate and write all combinations
    for camera_id in camera_ids:
        for gimbal_speed in gimbal_speeds:
            for pan in pan_values:
                writer.writerow([camera_id, gimbal_speed, pan])

print("CSV file 'camera_combinations.csv' created successfully!")
