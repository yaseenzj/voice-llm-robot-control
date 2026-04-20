// --- PINS FROM YOUR HANDWRITTEN NOTES ---
const int DIR1 = 6;   // Left Direction
const int PWM1 = 10;  // Left Speed
const int DIR2 = 5;   // Right Direction
const int PWM2 = 9;   // Right Speed

// --- SPEED SETTINGS ---
const int SLOW_MOVE_SPEED = 140; 
const int SLOW_TURN_SPEED = 120; 

// --- ENCODER PINS ---
const int L_ENC_B = 2; // Interrupt
const int L_ENC_A = 3; // Interrupt
volatile long left_ticks = 0;
const int TICKS_FOR_90 = 480; 

void setup() {
  Serial.begin(9600);
  
  pinMode(DIR1, OUTPUT); pinMode(PWM1, OUTPUT);
  pinMode(DIR2, OUTPUT); pinMode(PWM2, OUTPUT);
  
  pinMode(L_ENC_B, INPUT_PULLUP);
  pinMode(L_ENC_A, INPUT_PULLUP);
  
  // Attach interrupts for precise counting
  attachInterrupt(digitalPinToInterrupt(L_ENC_B), [](){ left_ticks++; }, RISING);
  attachInterrupt(digitalPinToInterrupt(L_ENC_A), [](){ left_ticks++; }, RISING);
  
  stopRobot();
  Serial.println("System Ready: Slow Mode + Logic Fixed");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    
    if (cmd == 'F')      moveForward();
    else if (cmd == 'B') moveBackward(); // Now defined below
    else if (cmd == 'S') stopRobot();
    else if (cmd == 'L') pivotLeft();    // Just turns, no auto-forward
    else if (cmd == 'R') pivotRight();   // Just turns, no auto-forward
  }
}

// --- MOVEMENT FUNCTIONS ---

void moveForward() {
  digitalWrite(DIR1, LOW); 
  digitalWrite(DIR2, LOW);
  analogWrite(PWM1, SLOW_MOVE_SPEED);  
  analogWrite(PWM2, SLOW_MOVE_SPEED);
}

void moveBackward() {
  // Setting DIR pins HIGH reverses the Cytron Maker Drive channels
  digitalWrite(DIR1, HIGH); 
  digitalWrite(DIR2, HIGH);
  analogWrite(PWM1, SLOW_MOVE_SPEED);  
  analogWrite(PWM2, SLOW_MOVE_SPEED);
}

void pivotLeft() {
  left_ticks = 0;
  digitalWrite(DIR1, HIGH); // Left Back
  digitalWrite(DIR2, LOW);  // Right Forward
  analogWrite(PWM1, SLOW_TURN_SPEED);   
  analogWrite(PWM2, SLOW_TURN_SPEED);
  while(left_ticks < TICKS_FOR_90); 
  stopRobot(); 
}

void pivotRight() {
  left_ticks = 0;
  digitalWrite(DIR1, LOW);  // Left Forward
  digitalWrite(DIR2, HIGH); // Right Back
  analogWrite(PWM1, SLOW_TURN_SPEED);   
  analogWrite(PWM2, SLOW_TURN_SPEED);
  while(left_ticks < TICKS_FOR_90); 
  stopRobot();
}

void stopRobot() {
  analogWrite(PWM1, 0); 
  analogWrite(PWM2, 0);
}