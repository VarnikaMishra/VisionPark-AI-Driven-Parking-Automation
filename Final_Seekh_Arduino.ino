// Smart Parking System - Arduino Hardware Interface
// This sketch communicates with a Python script via Serial to manage sensors, servo, and LCD.

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>

// --- Pin Definitions (Adjust for your wiring) ---
const int ENTRY_IR_PIN = 8; // Digital pin for Entry IR Sensor (LOW when car detected)
const int EXIT_IR_PIN  = 7; // Digital pin for Exit IR Sensor (LOW when car detected)
const int SERVO_PIN    = 9; // PWM pin for Servo Motor

// --- Servo Configuration ---
Servo barrierServo;
const int CLOSED_ANGLE = 0;   // Angle for barrier closed (horizontal)
const int OPEN_ANGLE   = 90;  // Angle for barrier open (vertical)

// --- LCD Configuration (Adjust address if necessary - 0x27 and 0x3F are common) ---
LiquidCrystal_I2C lcd(0x27, 16, 2); // 16 columns, 2 lines

// --- State Variables ---
int currentEntryState = HIGH; // HIGH means clear/no car detected initially
int currentExitState = HIGH;  // HIGH means clear/no car detected initially

// --- Function Prototypes ---
void initLCD();
void openBarrier();
void closeBarrier();
void checkSensorsAndReport();
void processSerialCommand();
void updateLCD(const String& data);

// ===================================
// SETUP
// ===================================

void setup() {
  // 1. Initialize Serial Communication (MUST match Python's BAUD_RATE 9600)
  Serial.begin(9600);
  Serial.println("Arduino Ready.");

  // 2. Initialize Component Pins
  pinMode(ENTRY_IR_PIN, INPUT);
  pinMode(EXIT_IR_PIN, INPUT);

  // 3. Initialize Servo
  barrierServo.attach(SERVO_PIN);
  closeBarrier(); // Ensure the barrier starts closed

  // 4. Initialize LCD
  initLCD();
}

// ===================================
// MAIN LOOP
// ===================================

void loop() {
  // Check for new commands from the Python script
  processSerialCommand();

  // Continuously check sensor states and report changes to Python
  checkSensorsAndReport();

  // A small delay to keep the loop responsive
  delay(10);
}

// ===================================
// CORE FUNCTIONS
// ===================================

/**
 * Reads the IR sensors and reports state changes to the Python script.
 * Logic: LOW = Object detected (car is present).
 */
void checkSensorsAndReport() {
  int newEntryState = digitalRead(ENTRY_IR_PIN);
  int newExitState = digitalRead(EXIT_IR_PIN);

  // --- Entry Sensor Logic ---
  if (newEntryState != currentEntryState) {
    currentEntryState = newEntryState;
    if (currentEntryState == LOW) {
      // Car detected at Entry. Send signal to Python to start OCR.
      Serial.println("ENTRY:0");
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Entry Detected");
      lcd.setCursor(0, 1);
      lcd.print("Checking Plates...");
    } else {
      // Car has passed the Entry sensor (cleared).
      Serial.println("ENTRY:1");
    }
  }

  // --- Exit Sensor Logic ---
  if (newExitState != currentExitState) {
    currentExitState = newExitState;
    if (currentExitState == LOW) {
      // Car detected at Exit. Send signal to Python to start OCR and fare calculation.
      Serial.println("EXIT:0");
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Exit Detected");
      lcd.setCursor(0, 1);
      lcd.print("Calculating Fare...");
    } else {
      // Car has passed the Exit sensor (cleared).
      Serial.println("EXIT:1");
    }
  }
}

/**
 * Reads and processes incoming commands from the Python script.
 * Commands: 'O' (Open), 'C' (Close), 'SLOTS:X' (Update LCD).
 */
void processSerialCommand() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any leading/trailing whitespace

    if (command.startsWith("SLOTS:")) {
      // Update LCD command received (e.g., "SLOTS:3")
      updateLCD(command);

    } else if (command == "O") {
      // Open barrier command
      openBarrier();

    } else if (command == "C") {
      // Close barrier command
      closeBarrier();

    }
  }
}

// ===================================
// BARRIER CONTROL FUNCTIONS
// ===================================

void openBarrier() {
  // Move servo to the open position
  barrierServo.write(OPEN_ANGLE);
  delay(500);
}

void closeBarrier() {
  // Move servo to the closed position
  barrierServo.write(CLOSED_ANGLE);
  delay(500);
}

// ===================================
// LCD CONTROL FUNCTIONS
// ===================================

void initLCD() {
  lcd.init();
  lcd.backlight();

  // Display initial message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Smart Parking V1");
  lcd.setCursor(0, 1);
  lcd.print("System Booting...");
  delay(1000);
}

/**
 * Updates the LCD with available slot information received from Python.
 * The data string is in the format "SLOTS:X"
 */
void updateLCD(const String& data) {
  // Extract the number of slots from the string
  int slotIndex = data.indexOf(':');
  if (slotIndex != -1) {
    String slotsStr = data.substring(slotIndex + 1);
    int slots = slotsStr.toInt();

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Parking System");
    lcd.setCursor(0, 1);

    // Display different messages based on capacity
    if (slots > 0) {
      lcd.print("Slots Available: ");
      lcd.print(slots);
    } else {
      lcd.print("LOT FULL - WAIT");
    }
  }
}

