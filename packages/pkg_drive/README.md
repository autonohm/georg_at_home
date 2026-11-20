# drive

Teleoperation und Motorsteuerung

Nodes:
- [edu_robot](https://github.com/EduArt-Robotik/edu_robot) - Kommunikation mit Rädern
- [edu_robot_contol](https://github.com/EduArt-Robotik/edu_robot_control) - joystick parser
- [twist_limiter](./twist_limiter/) - begrenzung der beschleunigung
- joy_linux - joystick einlesen

```mermaid
graph LR;
  joy_node--joy\n[Joy]-->remote_control;
  remote_control--teleop/cmd_vel\n[Twist]-->twist_mux;
  navigation--nav/cmd_vel\n[Twist]-->twist_mux;
  twist_mux--cmd_vel\n[Twist]-->thn-georg-bot\nmotoren

```