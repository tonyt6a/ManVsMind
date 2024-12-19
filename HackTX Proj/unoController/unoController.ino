#define BUTTON_UP 2

#define BUTTON_RIGHT 3

#define BUTTON_DOWN 4

#define BUTTON_LEFT 5

#define BUTTON_E 6

#define BUTTON_F 7

#define BUTTON_K 8

#define PIN_ANALOG_X 0

#define PIN_ANALOG_Y 1

#define DELAY 500



void setup() {

  Serial.begin(115200);

  // to enable pull up resistors first write pin mode
  // and then make that pin HIGH

  pinMode(BUTTON_UP, INPUT);
  digitalWrite(BUTTON_UP, HIGH);

  pinMode(BUTTON_RIGHT, INPUT);
  digitalWrite(BUTTON_RIGHT, HIGH);

  pinMode(BUTTON_DOWN, INPUT);
  digitalWrite(BUTTON_DOWN, HIGH);


  pinMode(BUTTON_LEFT, INPUT);
  digitalWrite(BUTTON_LEFT, HIGH);

  pinMode(BUTTON_E, INPUT);
  digitalWrite(BUTTON_E, HIGH);

  pinMode(BUTTON_F, INPUT);
  digitalWrite(BUTTON_F, HIGH);

  pinMode(BUTTON_K, INPUT);
  digitalWrite(BUTTON_K, HIGH);
}


void loop() {
  // UP button
  if (digitalRead(BUTTON_UP) == LOW) {
    Serial.println("UP");
    delay(DELAY);
  }

  // RIGHT button
  else if (digitalRead(BUTTON_RIGHT) == LOW) {
    Serial.println("ATTACK");
    delay(DELAY);
  }

  // DOWN button
  else if (digitalRead(BUTTON_DOWN) == LOW) {
    Serial.println("JUMP");
    delay(DELAY);
  }

  // LEFT button
  else if (digitalRead(BUTTON_LEFT) == LOW) {
    Serial.println("L BUTTON");
    delay(DELAY);
  }

  else if (digitalRead(BUTTON_E) == LOW) {
    Serial.println("E");
    delay(DELAY);
  }

  else if (digitalRead(BUTTON_F) == LOW) {
    Serial.println("F");
    Serial.print("x:  ");
    Serial.println(analogRead(PIN_ANALOG_X));

    // Print y axis values
    Serial.print("y: ");
    Serial.println(analogRead(PIN_ANALOG_Y));

    // Some delay to clearly observe your values on serial monitor.
    if (analogRead(PIN_ANALOG_X) > 521) {
      Serial.println("joystick: right");
    } else if (analogRead(PIN_ANALOG_X) < 521) {
      Serial.println("joystick: left");
    }
    delay(500);
    delay(DELAY);
  }

  if (digitalRead(BUTTON_K) == LOW) {
    Serial.println("K");
    delay(DELAY);
  }


  // right movement
  if (analogRead(PIN_ANALOG_X) > 530) {
    Serial.println("RIGHT");
    delay(DELAY);

    // left movement
  } else if (analogRead(PIN_ANALOG_X) < 518) {
    Serial.println("LEFT");
    delay(DELAY);
  }
}
