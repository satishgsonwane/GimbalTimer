import asyncio
import json
import csv
import pandas as pd
from nats.aio.client import Client as NATS
from timer import Timer

BOLD = "\033[1m"
RESET = "\033[0m"

async def process_combination(nc, cam_id, gimbal_speed, pan_setpoint, tilt_setpoint):
    POSITION_TOLERANCE = 0.1  # Easily adjustable tolerance
    timer = Timer()
    target_reached = asyncio.Event()
    pan_reached = False
    tilt_reached = False
    last_pan_difference = float('inf')
    last_tilt_difference = float('inf')
    
    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
            nonlocal pan_reached, tilt_reached, last_pan_difference, last_tilt_difference
            
            if 'panposition' in data and 'tiltposition' in data:
                try:
                    current_pan = float(data['panposition'])
                    current_tilt = float(data['tiltposition'])
                except ValueError:
                    print(f"Warning: Invalid position data received: {data}")
                    return
                
                # Invert current tilt position for comparison if setpoint is positive
                adjusted_current_tilt = -current_tilt if tilt_setpoint > 0 else current_tilt
                pan_difference = abs(current_pan - pan_setpoint)
                tilt_difference = abs(adjusted_current_tilt - tilt_setpoint)
                
                # Debug logging for significant changes
                if abs(pan_difference - last_pan_difference) > 0.05:
                    print(f"\nPan difference changed significantly: {pan_difference:.3f}")
                if abs(tilt_difference - last_tilt_difference) > 0.05:
                    print(f"\nTilt difference changed significantly: {tilt_difference:.3f}")
                
                last_pan_difference = pan_difference
                last_tilt_difference = tilt_difference
                
                # Update reached flags independently
                if pan_difference <= POSITION_TOLERANCE:
                    if not pan_reached:
                        print(f"\nPan target reached at {current_pan:.3f}")
                    pan_reached = True
                if tilt_difference <= POSITION_TOLERANCE:
                    if not tilt_reached:
                        print(f"\nTilt target reached at {adjusted_current_tilt:.3f}")
                    tilt_reached = True
                
                if pan_reached and tilt_reached and not target_reached.is_set():
                    print(f"\nFinal position: Pan={current_pan:.3f}, Tilt={current_tilt:.3f}")
                    print(f"Final position Difference: Pan={pan_difference:.3f}, Tilt={tilt_difference:.3f}")
                    print("Target position reached!")
                    target_reached.set()
                else:
                    print(f"Current position: Pan={current_pan:.3f}, Tilt={current_tilt:.3f}, " 
                          f"Difference: Pan={pan_difference:.3f}, Tilt={tilt_difference:.3f}", end='\r')
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing message: {e}")
    
    subscription = await nc.subscribe(f"ptzinfo.camera{cam_id}", cb=message_handler)
    print("="*80)
    print(f"Testing: Camera {cam_id}, Speed {gimbal_speed}, Pan {pan_setpoint}, Tilt {tilt_setpoint}")
    print(f"Subscribed to ptzinfo.camera{cam_id}")
    
    # Reset flags before starting new movement
    pan_reached = False
    tilt_reached = False
    last_pan_difference = float('inf')
    last_tilt_difference = float('inf')
    
    # Invert positive tilt values to negative
    adjusted_tilt = -tilt_setpoint if tilt_setpoint > 0 else tilt_setpoint
    control_msg = {
        "pansetpoint": pan_setpoint,
        "tiltsetpoint": adjusted_tilt,
        "gimbal_speed": gimbal_speed
    }
    print("Sending control message and starting timer...")
    await nc.publish(f"ptzcontrol.camera{cam_id}", json.dumps(control_msg).encode())
    timer.start()

    try:
        await asyncio.wait_for(target_reached.wait(), timeout=20.0)
        elapsed_time = timer.get_lapsed() / 1000  # Convert to seconds
        print(f"Target reached in {BOLD}{elapsed_time:.2f} Seconds{RESET}")
        return elapsed_time
    except asyncio.TimeoutError:
        print("\nTimeout: Target position not reached within 20 seconds")
        print(f"Last differences - Pan: {last_pan_difference:.3f}, Tilt: {last_tilt_difference:.3f}")
        return None
    finally:
        timer.stop()
        await subscription.unsubscribe()

async def main():
    # Read the CSV file
    df = pd.read_csv('camera_combinations_new.csv')
    
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
                    float(row['pan_setpoint']),
                    float(row['tilt_setpoint'])
                )
                
                # Update the DataFrame with the execution time
                df.at[index, 'execution_time'] = execution_time
                
                # Save after each combination in case of interruption
                df.to_csv('camera_combinations_new.csv', index=False)
                
                # Add a small delay between tests
                await asyncio.sleep(2)
        
        print("\nAll combinations tested successfully!")
        
    finally:
        await nc.drain()

if __name__ == "__main__":
    asyncio.run(main())