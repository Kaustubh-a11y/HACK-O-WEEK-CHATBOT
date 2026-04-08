#include <EEPROM.h>

const int sensorPin = 2;
const int relayPin = 8;

int count = 0;
int lastState = LOW;

void setup() {
  pinMode(sensorPin, INPUT);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);

  Serial.begin(9600);

  // Read stored count
  count = EEPROM.read(0);

  Serial.print("Initial Count: ");
  Serial.println(count);
}

void loop() {
  int sensorState = digitalRead(sensorPin);

  // Detect button press (rising edge)
  if (sensorState == HIGH && lastState == LOW) {

    Serial.println("Touch Detected → Dispensing");

    // Activate relay
    digitalWrite(relayPin, HIGH);
    delay(1000);
    digitalWrite(relayPin, LOW);

    // Increase count
    count++;

    // Store safely (only writes if changed)
    EEPROM.update(0, count);

    Serial.print("Items Dispensed: ");
    Serial.println(count);

    delay(300); // debounce
  }

  lastState = sensorState;
}
