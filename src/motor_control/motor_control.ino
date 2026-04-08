const int enA = 9;  const int in1 = 8;  const int in2 = 10;
const int enB = 6;  const int in3 = 11; const int in4 = 12;

void setup() {
  Serial.begin(9600);
  pinMode(enA, OUTPUT); pinMode(in1, OUTPUT); pinMode(in2, OUTPUT);
  pinMode(enB, OUTPUT); pinMode(in3, OUTPUT); pinMode(in4, OUTPUT);
  stopRobot();
}

int currentSpeed = 150;

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '0') currentSpeed = 90;       // Slow
    else if (cmd == '1') currentSpeed = 150; // Normal
    else if (cmd == '2') currentSpeed = 255; // Fast
    else if (cmd == 'F' || cmd == 'f') move(LOW, HIGH, LOW, HIGH); // FORWARD
    else if (cmd == 'B' || cmd == 'b') move(HIGH, LOW, HIGH, LOW); // BACKWARD
    else if (cmd == 'L' || cmd == 'l') move(HIGH, LOW, LOW, HIGH); // LEFT (Left backward, Right forward)
    else if (cmd == 'R' || cmd == 'r') move(LOW, HIGH, HIGH, LOW); // RIGHT (Left forward, Right backward)
    else if (cmd == 'S' || cmd == 's') stopRobot();
  }
}

void move(int l1, int l2, int r1, int r2) {
  digitalWrite(in1, l1); digitalWrite(in2, l2);
  digitalWrite(in3, r1); digitalWrite(in4, r2);
  analogWrite(enA, currentSpeed); analogWrite(enB, currentSpeed);
}

void stopRobot() {
  digitalWrite(in1, LOW); digitalWrite(in2, LOW);
  digitalWrite(in3, LOW); digitalWrite(in4, LOW);
  analogWrite(enA, 0); analogWrite(enB, 0);
}