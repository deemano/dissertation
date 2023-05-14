#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>
#include <ODriveArduino.h>

//=========================== 
/* 
Arduino Due (ODrive 3.6):
Connect pin 18 (TX1) on the Arduino Due to the RX (GPIO1) pin on the ODrive 3.6.
Connect pin 19 (RX1) on the Arduino Due to the TX (GPIO2) pin on the ODrive 3.6.

Arduino Due (ODrive 3.5):
Connect pin 16 (TX2) on the Arduino Due to the RX (GPIO1) pin on the ODrive 3.5.
Connect pin 17 (RX2) on the Arduino Due to the TX (GPIO2) pin on the ODrive 3.5.

In both cases:
Connect a GND (ground) pin of the Arduino to a GND pin of the ODrive. 
This is to ensure that they have a common ground reference. 
*/
// ============================

// IMU setup
Adafruit_BNO055 bno = Adafruit_BNO055(55);

// ODrive setup
HardwareSerial& odrive_serial1 = Serial1;
HardwareSerial& odrive_serial2 = Serial2;
ODriveArduino odrive1(odrive_serial1);
ODriveArduino odrive2(odrive_serial2);

// Offset for X-axis angle
float angleOffset = 0;

void setup(void) 
{
  // Start communication with IMU
  Serial.begin(9600);
  Serial.println("Orientation Sensor Test"); 
  Serial.println("");

  if(!bno.begin())
  {
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while(1);
  }

  // Start communication with ODrives
  odrive_serial1.begin(115200);
  odrive_serial2.begin(115200);

  // Initialize the angle offset at startup
  sensors_event_t event; 
  bno.getEvent(&event);
  angleOffset = event.orientation.x;

  delay(1000);
}

void loop(void) 
{
  // Get a new sensor event
  sensors_event_t event; 
  bno.getEvent(&event);

  // Adjust the X-axis angle with the offset
  float angle = event.orientation.x - angleOffset;

  // Display the adjusted angle data
  Serial.print("Adjusted X: ");
  Serial.print(angle, 4);
  Serial.print("\tY: ");
  Serial.print(event.orientation.y, 4);
  Serial.print("\tZ: ");
  Serial.print(event.orientation.z, 4);
  Serial.println("");

  // If the adjusted angle is 90 degrees or more, stop Odrive 3.5
  if(angle >= 90) {
    odrive2.SetVelocity(0, 0);
  }

  // Read input from the serial monitor
  if (Serial.available() > 0) {
    char c = Serial.read();

    // Rotate Odrive 3.5 at 100 speed in the negative direction for 7 seconds and stop when 'R' is pressed
    if (c == 'R') {
      odrive2.SetVelocity(0, -100);
      delay(7000);
      odrive2.SetVelocity(0, 0);
    }

    // Rotate Odrive 3.5 at 100 speed in the positive direction for 7 seconds and stop when 'L' is pressed
    else if (c == 'L') {
      odrive2.SetVelocity(0, 100);
      delay(7000);
      odrive2.SetVelocity(0, 0);
    }
  }

  // Move Odrive 3.6 to position 2
  odrive1.SetPosition(0, 2);
  delay(10000); // Wait 10 seconds

  // Move Odrive 3.6 to position -2
  odrive1.SetPosition(0, -2);

  delay(3);
}
