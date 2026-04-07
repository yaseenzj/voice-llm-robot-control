// Left Motor: Speed(9), Direction(8, 10)
// Right Motor: Speed(6), Direction(11, 12)

const int enA = 9;  const int in1 = 8;  const int in2 = 10;
const int enB = 6;  const int in3 = 11; const int in4 = 12;

void setup() {
  Serial.begin(9600);
  pinMode(enA, OUTPUT); pinMode(in1, OUTPUT); pinMode(in2, OUTPUT);
  pinMode(enB, OUTPUT); pinMode(in3, OUTPUT); pinMode(in4, OUTPUT);
  stopRobot();
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'F') move(HIGH, LOW, HIGH, LOW);    // Forward
    else if (cmd == 'B') move(LOW, HIGH, LOW, HIGH); // Backward
    else if (cmd == 'L') move(LOW, HIGH, HIGH, LOW); // Left Turn
    else if (cmd == 'R') move(HIGH, LOW, LOW, HIGH); // Right Turn
    else if (cmd == 'S') stopRobot();                // Stop
  }
}

void move(int l1, int l2, int r1, int r2) {
  digitalWrite(in1, l1); digitalWrite(in2, l2);
  digitalWrite(in3, r1); digitalWrite(in4, r2);
  analogWrite(enA, 255); // Full Speed Left
  analogWrite(enB, 255); // Full Speed Right
}

void stopRobot() {
  digitalWrite(in1, LOW); digitalWrite(in2, LOW);
  digitalWrite(in3, LOW); digitalWrite(in4, LOW);
  analogWrite(enA, 0); analogWrite(enB, 0);
}
