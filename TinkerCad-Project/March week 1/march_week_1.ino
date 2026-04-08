#include <Servo.h>

Servo doorServo;

int irSensor = 2;
int ledPin = 7;

int sensorState = 0;

void setup()
{
  doorServo.attach(9);
  
  pinMode(irSensor, INPUT);
  pinMode(ledPin, OUTPUT);

  Serial.begin(9600);

  doorServo.write(0); 
  Serial.println("System Ready - Door Closed");
}

void loop()
{
  sensorState = digitalRead(irSensor);

  if(sensorState == HIGH)
  {
    Serial.println("User detected - Opening door");
    
    digitalWrite(ledPin, HIGH);
    
    doorServo.write(90);  
    delay(3000);

    Serial.println("Closing door");
    
    doorServo.write(0);   
    digitalWrite(ledPin, LOW);
    
    delay(2000);
  }
}
