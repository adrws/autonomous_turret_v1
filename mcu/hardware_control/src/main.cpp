#include <Arduino.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

#define SERVO_X_PIN 33
#define SERVO_Y_PIN 32
#define MOTOR_A_EN NULL
#define MOTOR_B_EN NULL
#define MOTOR_A_PWM NULL
#define MOTOR_B_PWM NULL

Servo SERVO_X;
Servo SERVO_Y;

void parseCommand(String incoming);
void setServo(int step, Servo& SERVO, int& position);
void initServo(Servo& SERVO, int SERVO_PIN);
void initMotor(int PWM, int ENABLE);

int x_position{90};
int y_position{90};

void setup() {
    Serial.begin(921600);
    initServo(SERVO_X, SERVO_X_PIN);
    initServo(SERVO_Y, SERVO_Y_PIN);
    initMotor(MOTOR_A_PWM, MOTOR_A_EN);
    initMotor(MOTOR_B_PWM, MOTOR_B_EN);
}

void loop() {
    if (Serial.available() > 0) {
        String incoming = Serial.readStringUntil('\n');
        parseCommand(incoming);
    }
}

void parseCommand(String incoming) {
    JsonDocument json;
    String command;
    DeserializationError error = deserializeJson(json, incoming);

    if (error) {
        return;
    }

    command = json["command"].as<String>();

    if (command == "setX") {
        x_position = json["angle"].as<int>();
        setServo(0, SERVO_X, x_position);
    }
    else if (command == "setY") {
        y_position = json["angle"].as<int>();
        setServo(0, SERVO_Y, y_position);
    }
    else if (command == "setSpeed") {
        int speed = json["speed"].as<int>();
        String motor = json["motor"].as<String>();

        if (motor == "left") {
            analogWrite(MOTOR_B_PWM, speed);
        }
        else if (motor == "right") {
            analogWrite(MOTOR_A_PWM, speed);
        }
    }
    else if (command == "releaseBall") {
        // TODO: figure out ball release mechanism
    }
}

void setServo(int step, Servo& SERVO, int& position) {
    position = constrain(position + step, 0, 180);
    SERVO.write(position);
}

void initServo(Servo& SERVO, int SERVO_PIN) {
    SERVO.setPeriodHertz(50);
    SERVO.attach(SERVO_PIN, 500, 2500);
    SERVO.write(90);
}

void initMotor(int PWM, int ENABLE) {
    pinMode(PWM, OUTPUT);
    pinMode(ENABLE, OUTPUT);
    digitalWrite(ENABLE, HIGH);
    analogWrite(PWM, 0);
}


