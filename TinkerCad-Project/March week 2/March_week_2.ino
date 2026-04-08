#define trigPin 9
#define echoPin 10

#define buzzer 7

#define motorEnable 5
#define motor1 4
#define motor2 3

long duration;
int distance;

void setup()
{
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  pinMode(buzzer, OUTPUT);

  pinMode(motorEnable, OUTPUT);
  pinMode(motor1, OUTPUT);
  pinMode(motor2, OUTPUT);

  Serial.begin(9600);

  digitalWrite(motorEnable, HIGH);
}

void loop()
{
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);

  distance = duration * 0.034 / 2;

  Serial.print("Distance: ");
  Serial.println(distance);

  if(distance <= 200)
  {
    digitalWrite(buzzer, HIGH);

    digitalWrite(motor1, LOW);
    digitalWrite(motor2, LOW);

    Serial.println("Pedestrian detected - Motor stopped");
  }
  else
  {
    digitalWrite(buzzer, LOW);

    digitalWrite(motor1, HIGH);
    digitalWrite(motor2, LOW);

    Serial.println("Path clear - Motor running");
  }

  delay(500);
}
