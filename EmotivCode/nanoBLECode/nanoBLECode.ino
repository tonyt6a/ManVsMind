#include <ArduinoBLE.h>

// Define the service and characteristic UUIDs
BLEService controlService("12345678-1234-1234-1234-123456789abc");  // Custom service
BLEByteCharacteristic commandCharacteristic("87654321-4321-4321-4321-abcdefabcdef", BLEWrite);

void setup() {
    Serial.begin(9600);
    while (!Serial);

    // Initialize the BLE module
    if (!BLE.begin()) {
        Serial.println("Starting BLE failed!");
        while (1);
    }

    // Set up the BLE service and characteristic
    BLE.setLocalName("Nano33Control");
    BLE.setAdvertisedService(controlService);
    controlService.addCharacteristic(commandCharacteristic);
    BLE.addService(controlService);

    // Begin advertising
    BLE.advertise();
    Serial.println("Waiting for BLE connection...");
    
    // Set the onboard LED pin mode
    pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
    // Listen for BLE connections
    BLEDevice central = BLE.central();

    // If a device is connected, process commands
    if (central) {
        Serial.println("Connected to central device");
        while (central.connected()) {
            // Check if there's a new command written
            if (commandCharacteristic.written()) {
                // Read the incoming command as a byte
                byte command = commandCharacteristic.value();
                Serial.print("Command received: ");
                Serial.println(command);

                // Perform actions based on command
                switch (command) {
                    case 0x01:
                        // Command 1: Move forward (Blink once)
                        Serial.println("Moving forward...");
                        digitalWrite(LED_BUILTIN, HIGH);   // LED on
                        delay(500);                        // Wait for 500ms
                        digitalWrite(LED_BUILTIN, LOW);    // LED off
                        delay(500);                        // Wait for 500ms
                        break;
                    case 0x02:
                        // Command 2: Stop (Double blink)
                        Serial.println("Stopping...");
                        for (int i = 0; i < 2; i++) {    // Blink twice
                            digitalWrite(LED_BUILTIN, HIGH);   // LED on
                            delay(250);                        // Wait for 250ms
                            digitalWrite(LED_BUILTIN, LOW);    // LED off
                            delay(250);                        // Wait for 250ms
                        }
                        break;
                    // Add more cases as needed
                    default:
                        Serial.println("Unknown command");
                        break;
                }
            }
        }
        Serial.println("Disconnected from central device");
    }
}
