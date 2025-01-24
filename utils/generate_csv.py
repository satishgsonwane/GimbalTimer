import csv
import random

# Define parameters
cam_ids = [2, 3, 4]
gimbal_speeds = range(1, 9)  # 1-8
combinations_per_speed = 20
pan_range = (-50, 50)
tilt_range = (-5, 5)

# Create CSV file
with open('camera_combinations.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['cam_id', 'gimbal_speed', 'pan_setpoint', 'tilt_setpoint'])
    
    for camera_id in cam_ids:
        for speed in gimbal_speeds:
            for _ in range(combinations_per_speed):
                pan = random.randint(*pan_range)
                tilt = random.randint(*tilt_range)
                writer.writerow([camera_id, speed, pan, tilt])