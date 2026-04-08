#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

int sensorPin = 7;
int count = 0;
int lastState = LOW;

void setup() {
  lcd.begin(16, 2);
  pinMode(sensorPin, INPUT);
  lcd.print("Object Counter");
  delay(2000);
  lcd.clear();
}

void loop() {
  int currentState = digitalRead(sensorPin);

  // Detect button press (rising edge)
  if (currentState == HIGH && lastState == LOW) {
    count++;
    lcd.clear();
    lcd.print("Count: ");
    lcd.print(count);
    delay(300); // debounce
  }

  lastState = currentState;
}
