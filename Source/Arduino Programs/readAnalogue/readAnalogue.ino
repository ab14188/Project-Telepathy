#define N_SENSORS 4

unsigned long lastTimeMicro;
boolean readyFlag = false;  
boolean pauseFlag = true;

int minVals[N_SENSORS] = {0, 0, 0, 0};
int maxVals[N_SENSORS] = {1024, 1024, 1024, 1024};
static const int sensorPin[N_SENSORS] = {0, 1, 2, 3};

int sensorValues[N_SENSORS] = {0, 0, 0, 0};

void setup() {

  for (int i = 0; i < N_SENSORS; ++i) {
    pinMode(sensorPin[i], INPUT);
  }

  Serial.begin(19200);
  delay(30);

}
  
void calibrateRelaxed() {
  Serial.println("Calibrating relaxed hand pose...");
  for (int i = 0; i < N_SENSORS; ++i)
    minVals[i] = analogRead(sensorPin[i]);
}

void loop() {
  // send data only when you have received "ready" command:
  if (readyFlag == true && pauseFlag == false) {
    
    //write the timestamp
    const unsigned long currentMicros = millis();
    //Serial.print( currentMicros - lastTimeMicro);
    //Serial.print(" ");

    //write the data from the sensors
    for (int i = 0; i < N_SENSORS; i++) { // N_SENSORS instead of 3 
      // Smoothing to stop jagged movements 
      //sensorValues[i] = (sensorValues[i]*0.5)+(analogRead(sensorPin[i])*0.5);
      
      sensorValues[i] = analogRead(sensorPin[i]);
      //int v = map(sensorValues[i], minVals[i], maxVals[i], 0, 100);
      //v = constrain(v, 0, 100);
      Serial.print(sensorValues[i]);
      Serial.print(" ");
    }

    Serial.println();
    delay(20);
  }
}

// called once per loop after loop() function if there is data on the bus
void serialEvent() {

  for (int j = Serial.available(); j >= 0; --j) {
    char inChar = (char)Serial.read();
    if (inChar == '0') {
      calibrateRelaxed();
    } else if (inChar == 'b') { //start   added the pause such that the arduino stops sending information but it is still on 
      lastTimeMicro = millis();
      readyFlag = true;
      pauseFlag = false;
    } else if (inChar == 's') { //stop
      readyFlag = false;
    } else if (inChar == 'p'){ // pause 
      pauseFlag = true;
    }
  }

}
