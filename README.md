# VisionPark-AI-Driven-Parking-Automation
This is my IOT, CV and ML integrated project. I have completed this project during my 1st year B.E degree.(in 2025)

🚗 VisionPark: AI-Driven Parking Automation
🌟 Project Overview
VisionPark is a highly efficient, cost-effective, and infinitely scalable automated parking management system built specifically to address infrastructure challenges. It leverages low-cost hardware and open-source Computer Vision to provide a full-cycle solution for vehicle entry, automated access control, capacity management, and dynamic billing.

The system's core differentiator is its decentralized processing model, which ensures rapid response times and allows for unlimited scaling across multiple parking lanes using accessible components.

Key Advantages
Cost-Effective: Eliminates the need for expensive proprietary hardware (e.g., RFID/FASTag) by utilizing simple IR sensors and accessible webcams/IP cameras.

Massive Scalability: Processing is handled locally at each lane, while global state (capacity, records) is managed by a central database, ensuring unlimited capacity.

Integrated Security: The same vision hardware is used for Gesture-Based Emergency Detection and Unusual Activity Monitoring via OpenCV.

Automated Billing: Calculates fees automatically based on a customizable, tiered fare structure upon vehicle exit.

⚙️ The 3-Step Automated Process
VisionPark runs on a reliable, three-stage workflow to manage vehicle entry and exit with minimal latency:

💻 Tech Stack
This project integrates hardware control with advanced computer vision capabilities:

🚀 Getting Started
This guide assumes you are setting up the core Python service responsible for ANPR, decision-making, and communication with the Arduino.

Prerequisites
Python 3.8+

The requirements.txt file (for Python dependencies).

An Arduino setup with a serial connection to the host system.

Installation
Clone the Repository:

Install Python Dependencies:

Setup Hardware:

Upload the necessary Arduino sketch (e.g., visionpark_gate_control.ino) to your Arduino board.

Ensure the host system can access the specified Video Feed URL (IP camera stream or local webcam path).

Configuration
The system requires setting up several parameters, typically handled via a configuration file (e.g., config.py or .env file):

Running the System
Execute the main Python script to initialize the ANPR and monitoring service:

The system will now listen for serial commands from the Arduino trigger and begin processing plate recognition.

🛡️ Integrated Safety and Security
A key advantage of VisionPark is the dual-use nature of its vision pipeline.

Gesture-Based Emergency Alert: The video stream is constantly analyzed using OpenCV to detect pre-defined distress signals (e.g., waving arms) from a driver or pedestrian.

Unusual Activity Detection: The system flags erratic vehicle behavior or objects crossing the barrier line that require security attention.

Instant Notification: Upon detection, the system triggers an immediate alert to security personnel via a central API, providing the exact camera location and timestamp.

🤝 Contributing
We welcome contributions! Please refer to the CONTRIBUTING.md file (if you create one) for specific guidelines.

Fork the repository.

Create a feature branch (git checkout -b feature/your-feature).

Commit your changes (git commit -m 'feat: added improved fare calculation').

Push to the branch.

Open a Pull Request.
