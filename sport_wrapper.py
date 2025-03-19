import subprocess
import re
import json
import sys

def run_sport_script():
    # Run the sport.py script and capture its output
    result = subprocess.run(['python', 'sport.py'], 
                           capture_output=True, 
                           text=True)
    
    output = result.stdout
    
    # Write the complete output to a log file for debugging
    with open('sport_output.log', 'w') as f:
        f.write(output)
    
    # Search for booking code in the output
    booking_code_match = re.search(r'BOOKING CODE:\s*([A-Z0-9]+)', output)
    
    if booking_code_match:
        booking_code = booking_code_match.group(1)
        
        # Save the code to a file
        with open('sporty_code.txt', 'w') as f:
            f.write(booking_code)
        
        # Also update the real.json file with the code
        try:
            with open('real.json', 'r') as f:
                data = json.load(f)
            
            data['sporty_code'] = booking_code
            
            with open('real.json', 'w') as f:
                json.dump(data, f, indent=4)
                
            print(f"Booking code extracted: {booking_code}")
            return True
        except Exception as e:
            print(f"Error updating real.json: {str(e)}")
    else:
        print("No booking code found in output")
    
    return False

if __name__ == "__main__":
    success = run_sport_script()
    sys.exit(0 if success else 1)