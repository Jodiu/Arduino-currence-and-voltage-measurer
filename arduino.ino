int voltagePin1 = A0;
int voltagePin2 = A1;
float U1 = 0;
float U2 = 0;
float I = 0;
int analogValue = 0;

void setup(){
  Serial.begin(9600);
}

void loop(){
  U1 = analogRead(voltagePin1);
  U2 = analogRead(voltagePin2);
  Serial.print(U1);
  Serial.print(" ");
  Serial.println(U2);
  delay(100);
}
