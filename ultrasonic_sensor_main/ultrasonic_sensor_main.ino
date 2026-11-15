
const int trigPin = 9;
const int echoPin = 10;

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {

  for (int i = 5; i <= 30; i += 5) {

    Serial.print("Measuring distance for Object at ");
    Serial.print(i);
    Serial.println(" cm in:");

    // 10-second countdown
    for (int j = 10; j >= 1; j--) {
      Serial.println(j);
      delay(1000);
    }

    // Take 100 measurements at each distance
    for (int j = 1; j <= 100; j++) {

      digitalWrite(trigPin, LOW);
      delayMicroseconds(2);

      digitalWrite(trigPin, HIGH);
      delayMicroseconds(10);
      digitalWrite(trigPin, LOW);

      unsigned long duration = pulseIn(echoPin, HIGH, 30000);

      if (duration == 0) {
        Serial.println("NaN");
      }
      else {
        float distance = duration * 0.0343 / 2.0;
        Serial.println(distance);
      }

      delay(100);
    }
  }

  Serial.println("All measurements completed.");
  Serial.println("Do you want to repeat the measurements? (y/n)");

  while (true) {

    if (Serial.available() > 0) {

      char answer = Serial.read();

      if (answer == 'y' || answer == 'Y') {
        Serial.println("Repeating measurements...");
        break;
      }
      else if (answer == 'n' || answer == 'N') {
        Serial.println("Program stopped.");

        while (true) {
          // Stop program
        }
      }
    }
  }
}
