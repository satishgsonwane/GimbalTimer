import asyncio
import json
from nats.aio.client import Client as NATS
from timer import Timer

BOLD = "\033[1m"
RESET = "\033[0m"

async def main():
    nc = NATS()
    timer = Timer()
    
    # Get user inputs
    while True:
        try:
            cam_id = int(input(f"Enter Camera id (1 to 6) :"))
        except ValueError:
            print(f"{cam_id} is not a number, please enter a number")
        else:
            if 1 <= cam_id <= 6:  
                break
            else:
                print(f"{cam_id} is not within range, please enter a valid number")

    pan_setpoint = float(input("Enter pan setpoint value: "))

    while True:
        try:
            gimbal_speed = int(input(f"Enter gimbal_speed (0 to 255) :"))
        except ValueError:
            print(f"{gimbal_speed} is not a number, please enter a number")
        else:
            if 0 <= gimbal_speed <= 255:  
                break
            else:
                print(f"{gimbal_speed} is not within range, please enter a valid number")
    
    await nc.connect("nats://localhost:4222")
    target_reached = asyncio.Event()
    
    async def message_handler(msg):
        try:
            data = json.loads(msg.data.decode())
            
            if 'panposition' in data:
                current_pan = float(data['panposition'])
                difference = abs(current_pan - pan_setpoint)
                
                if difference <= 0.1:
                    print('='* 80)
                    print(f"\nFinal position: {current_pan:.3f}, Final position Difference: {difference:.3f}")
                    print("Target position reached!")
                    target_reached.set()
                else:
                    print(f"Current position: {current_pan:.3f}, Difference: {difference:.3f}", end='\r')
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing message: {e}")
    
    await nc.subscribe(f"ptzinfo.camera{cam_id}", cb=message_handler)
    print("="*80)
    print(f"Subscribed to ptzinfo.camera{cam_id}")
    
    control_msg = {
        "pansetpoint": pan_setpoint,
        "gimbal_speed": gimbal_speed
    }
    print("Sending control message and starting timer...")
    timer.start()
    await nc.publish(f"ptzcontrol.camera{cam_id}", json.dumps(control_msg).encode())
    
    try:
        await asyncio.wait_for(target_reached.wait(), timeout=120.0)
        elapsed_time = timer.get_lapsed()
        print(f"Target reached in {BOLD}{elapsed_time/1000:.2f} Seconds {RESET}")  # Convert ms to seconds
    except asyncio.TimeoutError:
        print("\nTimeout: Target position not reached within 120 seconds")
    finally:
        timer.stop()
        await nc.drain()

if __name__ == "__main__":
    asyncio.run(main())