#include <Servo.h>

Servo servoFB; // Forward/Backward servo
Servo servoLR; // Left/Right servo

void setup() {
  Serial.begin(9600);

  // Attach servos to their respective pins
  servoFB.attach(9);  // Forward/Backward servo on pin 9
  servoLR.attach(10); // Left/Right servo on pin 10

  // Initialize servos to neutral position
  servoFB.write(90);  // Neutral position
  servoLR.write(90);  // Neutral position
}

void loop() {
  for (int i = 0; i < 1; i++) {  // Repeat the sequence 3 times
    // Test servoFB (Forward/Backward servo)
    delay(100);
    servoFB.write(0); //forward
    delay(130);
    //delay(500);
    servoFB.write(90);
    delay(3000);

    servoFB.write(180); // back to neutral 
    delay(130);
    servoFB.write(90);
    delay(500);

    servoFB.write(180); // backward
    delay(100);
    servoFB.write(90);
    delay(3000);

    servoFB.write(0); // back to neutral
    delay(100);
    servoFB.write(90);
    delay(800);


    // Test servoLR (Left/Right servo)
    //right
    servoLR.write(0); //
    delay(200);
    servoLR.write(90);
    delay(4000);

    servoLR.write(180);
    delay(100);
    servoLR.write(90);
    delay(500);

    servoLR.write(180);
    delay(150);
    servoLR.write(90);
    delay(4000);

    servoLR.write(0);
    delay(100);
    servoLR.write(90);
    delay(500);
  }

  // Stop the loop after completing three cycles
  while (1) {}
}
