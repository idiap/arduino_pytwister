// SPDX-FileCopyrightText: 2024 Idiap Research Institute <contact@idiap.ch>
//
// SPDX-FileContributor: Michael Liebling <michael.liebling@idiap.ch>
//
// SPDX-License-Identifier: BSD-3-Clause

/*
  Firmware for Arduino connected to a Sparkfun stepper motor driver
  that interacts with a computer over a serial port and via
  the Python library arduino_twister.
*/

const char FIRMWARE_NAME[] = "ArduinoPyTwister";
const char VERSION[] = "0.1";

/* Acceptable instruction codes */
const String RESET_CODE = "RES";
const String FIRMWARE_CODE = "FIR";
const String VERSION_CODE = "VER";
const unsigned char TURN_CODE_PREFIX = 'T';

/* Error and Acknowledgement codes (single byte) */
const unsigned char ACK = 0;
const unsigned char ERR = 1;

/* How Sparkfun Easy Driver stepper motor driver
connectors are connected to Arduino */
const unsigned short PIN_ENABLE = 2;
const unsigned short PIN_DIR = 3;
const unsigned short PIN_STEP = 4;

/* How long to wait between rotation steps */
const unsigned short stepDelayMs = 2; //ms
/* How long to wait after rotation is complete */
const unsigned short stopDelayMs = 200; //ms

void reset()
{ /*  Reset Easy Driver pins to default states */
  digitalWrite(PIN_STEP, LOW);
  digitalWrite(PIN_DIR, LOW);
  digitalWrite(PIN_ENABLE, LOW);
}

void setup()
{ /* This function is run automatically when Arduino is powered up */
  pinMode(PIN_STEP, OUTPUT);
  pinMode(PIN_DIR, OUTPUT);
  pinMode(PIN_ENABLE, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  reset();
  //Serial.begin(19200);
  Serial.begin(9600);
}

void loop()
{ /* This function loops over to accept instructions over the serial port
  Properly formatted commands are three characters long. If the first
  character is TURN_CODE_PREFIX the last two characters are interpreted as
  the number of steps and rotation direction direction.
  */
  char received_command[3];
  if (Serial.available() >= 3)
  { /* All commands are made of three characters; as soon as buffer contains
       three characters, we read themm in. */
    received_command[0] = Serial.read();
    received_command[1] = Serial.read();
    received_command[2] = Serial.read();
    /* DEBUG
    Serial.print("Received:");
    Serial.println(received_command);
    DEBUG */
    /* Next we interpret the commands */
    if (String(received_command)==RESET_CODE){ // Reset Arduino
      reset();
    }else if (String(received_command)==FIRMWARE_CODE){
      /* Return the firmware name */
      //Serial.println("Firmware");
      Serial.println(FIRMWARE_NAME);
    } else if(String(received_command)==VERSION_CODE){
      /* Return the firmare version number */
      Serial.println(VERSION);
    } else if (received_command[0]==TURN_CODE_PREFIX){
      /* Rotate the twister */
      int16_t steps = rotation_code_to_int16(received_command);
      /* DEBUG
      Serial.print("Rotating by ");
      Serial.print(steps,DEC);
      Serial.println(" steps.");
      DEBUG */
      rotate_by_steps(steps);
      Serial.write(ACK);
    }else{
      /* The command is unrecognized. */
      //Serial.write(ERR);
      /* DEBUG
      Serial.println("Unrecognized command.");
      DEBUG */
      Serial.write(ERR);
    }
  }
}

int16_t rotation_code_to_int16(char* rotation_command ){
/*
Extract the last two bytes of a 3-byte rotation command
and convert them to a signed integer that represents
the number of steps to take in the rotation. The first
byte or the 3-byte rotation command, which contains the
rotation code that serves to identify the instruction,
is ignored by this function.
The sign corresponds to the direction of the rotation.
Returns: steps as an int16_t (signed 2-byte integer)
*/
  uint8_t steps_b[2];
  steps_b[0] = rotation_command[1];
  steps_b[1] = rotation_command[2];
  int16_t steps = steps_b[0] | (int16_t)steps_b[1] << 8;
  return(steps);
}

void rotate_by_steps(int steps)
{
  /*
  Instruct the stepper motor to turn by
  `steps` times 0.225° degrees.

  Rotation table for Sparkfun Easy Driver
  in eigth-step mode:
  1 step: 1.8°/8 = 0.2250°
  8 steps: 1.8°

  1 step: 1.8°/8 = 0.2250°
  8 steps: 1.8°
  steps   angle      # steps    # steps
          increment  in 180°    in 360°
      1    0.225°        800       1600
      8    1.8°          100        200
      16    3.6°           50        100
      80   18°             10         20
    100   22.5°            8         16
    200   45°              4          8
    400   90°              2          4
    800  180°              1          2
  */
  if (steps < 0)
  {
    digitalWrite(PIN_DIR, HIGH);
    steps = -steps;
  }
  else
  {
    digitalWrite(PIN_DIR, LOW);
  }
  for (int i = 0; i < steps; i++)
  {
    digitalWrite(PIN_STEP, HIGH);
    delay(stepDelayMs);
    digitalWrite(PIN_STEP, LOW);
    delay(stepDelayMs);
  }
  delay(stopDelayMs);
}
