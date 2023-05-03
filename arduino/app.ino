// Accepted format: JSON
// {
//    hDelta: Độ lệch theo phương ngang, phải dương trái âm,
//    vDelta: Độ lệch theo phương thẳng, trên dương dưới âm
// }

// Include libs
#include <Servo.h>
#include <Arduino_JSON.h>

// Variables
const int hServoPin = 2;
const int vServoPin = 3;

const int MIN_HSERVO_ANGLE = 0;
const int MAX_HSERVO_ANGLE = 180;
const int INI_HSERVO_ANGLE = 90;

const int MIN_VSERVO_ANGLE = 0;
const int MAX_VSERVO_ANGLE = 90;
const int INI_VSERVO_ANGLE = 90;

float update_rate = 0.2;
long baudrate = 115200;

Servo hServo;
Servo vServo;

int hAngle;
int vAngle;
String data;

// Helper functions

// Update angle: giữ 80% góc cũ và cộng thêm 20% góc mới
int getWeightedAngle(int newAngle, int oldAngle, float updateRate){
  int wAngle = (int) ((float) newAngle * updateRate + (float) oldAngle * (1 - updateRate));
  if (wAngle == newAngle) return wAngle;
  else {
    if (wAngle > newAngle) {
      return min(wAngle - oldAngle, -1) + oldAngle; 
    }
    else {
      return max(wAngle - oldAngle, 1) + oldAngle;
    }
  }
}

// Convert delta to new angle
int deltaToAngle(int delta, bool horizontal, bool reset){
  int value;
  if (horizontal) {
    if (reset) {
      value = INI_HSERVO_ANGLE;
    }
    else{
      value = hAngle - delta;
    
      if (value >= MAX_HSERVO_ANGLE){
        value = MAX_HSERVO_ANGLE;
      }
  
      if (value <= MIN_HSERVO_ANGLE) {
        value = MIN_HSERVO_ANGLE;
      }
    }
  }
  else{
    if (reset) {
      value = INI_VSERVO_ANGLE;
    }
    else{ 
       value = vAngle - delta;
    
      if (value >= MAX_VSERVO_ANGLE){
        value = MAX_VSERVO_ANGLE;
      }
  
      if (value <= MIN_VSERVO_ANGLE) {
        value = MIN_VSERVO_ANGLE;
      }
    } 
  }

  return value;
}

// Setup functions
void setup(){
  // Init Serial speed
  Serial.begin(baudrate);
  Serial.setTimeout(10);
  Serial.print("Start Arduino at "); Serial.print(baudrate); Serial.println(" baud rate!");

  // Attach servo to pin
  hServo.attach(hServoPin);
  vServo.attach(vServoPin);
  Serial.print("Attach horizontal servo to pin "); Serial.println(hServoPin);
  Serial.print("Attach vertical servo to pin "); Serial.println(vServoPin);

  // Init servo angle
  hServo.write(INI_HSERVO_ANGLE);
  vServo.write(INI_VSERVO_ANGLE);
  hAngle = INI_HSERVO_ANGLE;
  vAngle = INI_VSERVO_ANGLE;
}

// Loop functions
void loop(){
  // Đợi có dữ liệu truyền tới
  while (Serial.available() == 0) {}

  // Đọc dữ liệu
  data = Serial.readString();
  data.trim();
  Serial.print("\nRecieve data: "); Serial.println(data);

  // Convert sang JSON
  JSONVar object = JSON.parse(data);
  if (JSON.typeof(object) == "undefined") {
    Serial.println("Parsing input failed!");
    return;
  }

  // Update servo angle
  Serial.print("Old hAngle: "); Serial.print(hAngle);
  hAngle = getWeightedAngle(deltaToAngle((int) object["hDelta"], true, (bool) object["reset"]), hAngle, update_rate);
  hServo.write(hAngle);
  Serial.print(" - New hAngle: "); Serial.println(hAngle);

  Serial.print("Old vAngle: "); Serial.print(vAngle);
  vAngle = getWeightedAngle(deltaToAngle((int) object["vDelta"], false, (bool) object["reset"]), vAngle, update_rate);
  vServo.write(vAngle);
  Serial.print(" - New vAngle: "); Serial.println(vAngle);
}
