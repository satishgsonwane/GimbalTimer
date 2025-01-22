import asyncio
import json
import csv
import pandas as pd
from nats.aio.client import Client as NATS
from timer import Timer

BOLD = "\033[1m"
RESET = "\033[0m"

async def process_combination(nc, cam_id, gimbal_speed, pan_setpoint):
    timer = Timer()
    target_reached = asyncio.Event()
    initial_position_reached = asyncio.Event()
    
    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
            
            if 'panposition' in data:
                current_pan = float(data['panposition'])
                if not initial_position_reached.is_set():
                    # Check if we've reached initial position (0)
                    difference = abs(current_pan - 0)
                    if difference <= 0.1:
                        print(f"\nReached initial position 0: {current_pan:.3f}")
                        initial_position_reached.set()
                    else:
                        print(f"Moving to initial position 0. Current: {current_pan:.3f}", end='\r')
                else:
                    # Check for final target position
                    difference = abs(current_pan - pan_setpoint)
                    if difference <= 0.1:
                        print(f"\nFinal position: {current_pan:.3f}, Final position Difference: {difference:.3f}")
                        print("Target position reached!")
                        target_reached.set()
                    else:
                        print(f"Current position: {current_pan:.3f}, Difference: {difference:.3f}", end='\r')
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing message: {e}")
    
    subscription = await nc.subscribe(f"ptzinfo.camera{cam_id}", cb=message_handler)
    print("="*80)
    print(f"Testing: Camera {cam_id}, Speed {gimbal_speed}, Pan {pan_setpoint}")
    print(f"Subscribed to ptzinfo.camera{cam_id}")
    
    # First move to position 0
    initial_control_msg = {
        "pansetpoint": 0,
        "gimbal_speed": gimbal_speed
    }
    print("Moving to initial position 0...")
    await nc.publish(f"ptzcontrol.camera{cam_id}", json.dumps(initial_control_msg).encode())
    
    try:
        # Wait for initial position to be reached
        await asyncio.wait_for(initial_position_reached.wait(), timeout=120.0)
        print("Initial position 0 reached. Starting test to target position...")
        
        # Now move to actual target position
        control_msg = {
            "pansetpoint": pan_setpoint,
            "gimbal_speed": gimbal_speed
        }
        print("Sending control message and starting timer...")
        await nc.publish(f"ptzcontrol.camera{cam_id}", json.dumps(control_msg).encode())
        timer.start()

        await asyncio.wait_for(target_reached.wait(), timeout=120.0)
        elapsed_time = timer.get_lapsed() / 1000  # Convert to seconds
        print(f"Target reached in {BOLD}{elapsed_time:.2f} Seconds{RESET}")
        return elapsed_time
    except asyncio.TimeoutError:
        print("\nTimeout: Target position not reached within 120 seconds")
        return None
    finally:
        timer.stop()
        await subscription.unsubscribe()

async def main():
    # Read the CSV file
    df = pd.read_csv('camera_combinations.csv')
    
    # Add execution_time column if it doesn't exist
    if 'execution_time' not in df.columns:
        df['execution_time'] = None
    
    # Connect to NATS server
    nc = NATS()
    await nc.connect("nats://localhost:4222")
    
    try:
        # Process each combination
        for index, row in df.iterrows():
            if pd.isna(row['execution_time']):  # Only process combinations without execution time
                print(f"\nProcessing combination {index + 1} of {len(df)}")
                
                execution_time = await process_combination(
                    nc,
                    int(row['cam_id']),
                    int(row['gimbal_speed']),
                    float(row['pan_setpoint'])
                )
                
                # Update the DataFrame with the execution time
                df.at[index, 'execution_time'] = execution_time
                
                # Save after each combination in case of interruption
                df.to_csv('camera_combinations.csv', index=False)
                
                # Add a small delay between tests
                await asyncio.sleep(2)
        
        print("\nAll combinations tested successfully!")
        
    finally:
        await nc.drain()

if __name__ == "__main__":
    asyncio.run(main())