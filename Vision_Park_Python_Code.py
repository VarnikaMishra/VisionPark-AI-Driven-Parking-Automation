import serial
import time
import requests
from datetime import datetime
# REMOVED: import pytesseract
import easyocr
import cv2
import numpy as np

# --- Configuration (MUST BE SET) ---
# Change to your Arduino's serial port (e.g., '/dev/ttyACM0' on Linux/Mac)
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600      # Must match Arduino's Serial.begin()

# IP Webcam URL (change to your phone’s IP)
CAMERA_URL = "http://172.20.10.3:8080/shot.jpg"

# --- EasyOCR Initialization ---
# Initialize the EasyOCR Reader once. 
# Using 'en' (English) language model. Add other languages like 'hi' for Hindi if needed.
try:
    reader = easyocr.Reader(['en'], gpu=False) # Set gpu=True if you have CUDA installed
    print("EasyOCR Reader initialized successfully.")
except Exception as e:
    print(f"Error initializing EasyOCR. Ensure it is installed: {e}")

# --- Global State Variables ---
arduino = None
detections_entry = {}  # Store {plate_text: timestamp}
detections_exit = {}   # Store {plate_text: timestamp}
available_parking = 4
MAX_CAPACITY = 4

# --- Helper Functions ---

def capture_image_from_mobile():
    """Captures an image from the mobile IP webcam."""
    try:
        response = requests.get(CAMERA_URL)
        if response.status_code == 200:
            img_array = np.array(bytearray(response.content), dtype=np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return image
        else:
            print("Failed to capture image from mobile. Status Code:", response.status_code)
            return None
    except requests.exceptions.ConnectionError:
        print("Connection Error: Check if mobile camera server is running and IP is correct.")
        return None
    except Exception as e:
        print("Error capturing image:", e)
        return None

def extract_text(image):
    """Extracts text (license plate) from an image using EasyOCR."""
    try:
        # EasyOCR's readtext returns a list of [bbox, text, confidence]
        results = reader.readtext(image)
        
        # Concatenate all detected text strings into one (useful for plates that might be split)
        all_text = " ".join([text for (bbox, text, conf) in results])
        
        # Clean up and return the text
        return all_text.strip().replace('\n', '').replace('\r', '').upper()
    except Exception as e:
        print("EasyOCR error during text extraction:", e)
        return ""


def calculate_fare(entry_time_str, exit_time_str):
    """Calculates parking fare based on duration."""
    entry_time = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
    exit_time = datetime.strptime(exit_time_str, "%Y-%m-%d %H:%M:%S")

    duration = (exit_time - entry_time).total_seconds() / 60
    print(f"Parking Duration: {duration:.2f} minutes")

    if duration <= 30:
        fare = 20
    elif duration <= 60:
        fare = 40
    elif duration <= 120:
        fare = 60
    else:
        fare = 100

    print(f"Parking Fare: ₹{fare}")
    return fare

# --- Serial Communication Functions ---

def initialize_arduino():
    """Initializes and returns the global serial connection."""
    global arduino
    try:
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2) # Wait for the Arduino to reset
        print(f"Connected to Arduino on {SERIAL_PORT} at {BAUD_RATE} baud.")
        return True
    except serial.SerialException as e:
        print(f"Error connecting to Arduino. Check port and connection: {e}")
        return False

def send_command(command):
    """Sends a command (e.g., 'O\n', 'C\n', 'SLOTS:X\n') to the Arduino."""
    if arduino and arduino.is_open:
        # Ensure command is terminated with a newline for Arduino's readline()
        arduino.write(f"{command}\n".encode('utf-8'))
        # print(f"Sent: {command}") # Uncomment for debugging

def process_detection(is_entry):
    """Handles image capture and OCR when a car is detected at entry/exit."""
    image = capture_image_from_mobile()
    if image is not None:
        text = extract_text(image)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if text: # Only process if OCR found something
            if is_entry:
                detections_entry[text] = timestamp
                print(f"Entry Plate Detected: '{text}' at {timestamp}")
                
                # Check for available parking and open gate immediately if available
                global available_parking
                if available_parking > 0:
                    handle_entry_success(text)
                else:
                    print("Entry DENIED: Parking lot is full.")
            else:
                detections_exit[text] = timestamp
                print(f"Exit Plate Detected: '{text}' at {timestamp}")
                
                # Try to process exit logic immediately
                handle_exit_attempt(text)

        else:
            print(f"No readable text detected at {'Entry' if is_entry else 'Exit'}.")
    else:
        print("No image to process.")

# --- Logic Handlers ---

def handle_entry_success(plate_text):
    """Opens the gate for entry and updates capacity."""
    global available_parking
    
    # 1. Update capacity
    available_parking -= 1
    
    # 2. Open the gate
    send_command('O') 
    print(f"Entry gate OPENED for {plate_text}. Slots left: {available_parking}")
    
    # 3. Update LCD on Arduino
    send_command(f'SLOTS:{available_parking}')
    
    # NOTE: In a real system, you'd wait for a clear sensor signal before closing.
    # For this simplified model, we wait 5 seconds and close.
    time.sleep(5) 
    send_command('C')
    print("Entry gate CLOSED.")


def handle_exit_attempt(exit_plate):
    """Handles the exit process (fare calculation, payment simulation, gate open)."""
    global available_parking
    
    # Check if the exit plate matches a known entry plate
    if exit_plate in detections_entry:
        entry_time = detections_entry[exit_plate]
        exit_time = detections_exit[exit_plate]
        
        print(f"Vehicle '{exit_plate}' entered at {entry_time} and exited at {exit_time}")

        # Calculate fare
        fare_to_pay = calculate_fare(entry_time, exit_time)

        # Payment Simulation
        print(f"\nPlease pay parking fee: ₹{fare_to_pay}")
        time.sleep(2)
        print("Payment Done (Simulated).")

        # 1. Open the exit gate
        send_command('O')
        print("Exit gate OPENED.")

        # 2. Update capacity and records
        available_parking += 1
        del detections_entry[exit_plate]
        del detections_exit[exit_plate] # Clean exit record too
        
        # 3. Update LCD on Arduino
        send_command(f'SLOTS:{available_parking}')
        
        # 4. Close the gate after exit
        time.sleep(5)
        send_command('C')
        print("Exit gate CLOSED.")
        
    else:
        print(f"Exit DENIED for {exit_plate}: No matching entry record found.")

# --- Main Program Loop ---

def parking_system():
    global available_parking
    
    if not initialize_arduino():
        return

    # Initial LCD update
    send_command(f'SLOTS:{available_parking}')
    print("\nSmart Parking System Started. Monitoring Sensors...")
    
    try:
        while True:
            # Check for incoming serial data (sensor state changes) from Arduino
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').strip()

                if line.startswith('ENTRY:0'):
                    # Entry sensor detected a car
                    process_detection(is_entry=True)
                    
                elif line.startswith('EXIT:0'):
                    # Exit sensor detected a car
                    process_detection(is_entry=False)
                    
                # We ignore ENTRY:1 and EXIT:1 since the car is gone and the logic is complete
            
            time.sleep(0.01) # Small delay to keep the loop responsive

    except KeyboardInterrupt:
        print("\nParking System Stopped by User. Closing serial port.")
    finally:
        # Ensure gate is closed and serial port is released
        if arduino and arduino.is_open:
            send_command('C')
            arduino.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    parking_system()