#include <Servo.h>

Servo servoFB; // Forward/Backward servo
Servo servoLR; // Left/Right servo

void setup() {
  Serial.begin(115200);

  // Attach servos to their respective pins
  servoFB.attach(9);  // Forward/Backward servo on pin 9
  servoLR.attach(10); // Left/Right servo on pin 10

  // Initialize servos to neutral position
  servoFB.write(90);  // Neutral position
  servoLR.write(90);  // Neutral position
}

void loop() {
    // Test servoFB (Forward/Backward servo)
  if (Serial.available() > 0) {
    // Read the incoming command
    char command = Serial.read();

    if (command == 'w') {      
      servoFB.write(0); //forward
      delay(100);
      servoFB.write(90);
      delay(3000);

      servoFB.write(180); // back to neutral 
      delay(100);
      servoFB.write(90);
      delay(500);
    }
    /*else if (command == "s") {      
      servoFB.write(180); // backward
      delay(100);
      servoFB.write(90);
      delay(3000);

      servoFB.write(0); // back to neutral
      delay(100);
      servoFB.write(90);
      delay(500);
    }
    else if (command == "a") {      
      servoLR.write(0); // left
      delay(150);
      servoLR.write(90);
      delay(4000);

      servoLR.write(180);
      delay(100);
      servoLR.write(90);
      delay(500);
    }
    else if (command == "d") {      
      servoLR.write(180); // right
      delay(150);
      servoLR.write(90);
      delay(4000);

      servoLR.write(0);
      delay(100);
      servoLR.write(90);
      delay(500);
    } */

  }
}
