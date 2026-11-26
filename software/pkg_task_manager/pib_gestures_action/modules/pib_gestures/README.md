## ReadMe for usage of pib_gestures_action
pib_gestures_action is a ROS2 action based feature for performing pre-defined gestures with pib.
Access via action client, execution by action server. Core functionality is a pure python package.
Joint movement uses pib-sdk (https://github.com/pib-rocks/pib-sdk)

### Terminal (for gestures):
```python
source install/setup.bash
```

### Terminal 1
Start action server:
```python
ros2 run pib_gestures_action pib_gestures_server.py
```

### Terminal 2
Run action client
```python
ros2 run pib_gestures_action pib_gestures_client *pib_gesture* [*--x* X][*--y* Y][*--z* Z][*--pib_side* pib_side][*--pib_mode* pib_mode][*--pib_hand* pib_hand]
```

#### pib_gesture
*pib_gesture* represents the gesture to be performed and is always required

provided gestures:

**point_to**:           pib points at given coordinates
*required parameters*:  x, y, z, pib_side, pib_mode, pib_hand

**greet_person**:       pib greets a person at given coordinates
*required parameters*:  x, y, z, pib_side, pib_mode

**look_at**:            pib moves his head to look at given coordinates
*required parameters*:  x, y, z

**offer_hand**:         pib moves his arm to a fixed position in front of his upper body
*required parameters*:  pib_side, pib_mode

**open_hand**:          pib opens his hand at the determined side
*required parameters*:  pib_side

**close_hand**:         pib closes his hand at the determined side
*required parameters*:  pib_side

**locate_object**:      pib calculates the vector to the central upper body coordinate system, considering current head joint angles
*required parameters*:  x, y, z **(camera vector)** coordinates relative to the head camera


#### --x, --y, --z
*x y z* represent the vector from pibs central upper body coordinate system to the object/person (except for locate_object)
coordinate center:      pibs center in the exact height of both shoulder vertical joint axis
positive x axis:        points to the front of pib
positive y axis:        points to the left side of pib
positive z axis:        points upwards
Value unit:             mm


#### --pib_side
*pib_side* represents the left or right arm/hand to use
valid parameters:       "left", "right"


#### --pib_mode
*pib_mode* represents the the gesture mode to perform
valid parameters depend on pib_gesuture

**point_to**:           valid pib_mode values are "straight_arm", "bent_arm"
*straight_arm*:         pib points at the given coordiantes with a fully stretched arm
                        pointing direction is determined by both shoulder joints
*bent_arm*:             pib points at the given coordinates with an angled elbow and upper arm hanging down
                        pointing direction is determined by upper arm rotation and elbow joints

**greet_person**:       valid pib_mode values are "wave", "shake_hands"
*wave*:                 pib waves at the person, moving his elbow to perform the waving movement
                        waving direction is determined by both shoulder joints
*shake_hands*:          pib moves his arm in front, moving his elbow to perform the waving movement, not closing his hand
                        arm direction is determined by upper arm rotation and elbow joints

**offer_hand**:         valid pib_mode values are "horizontal_hand", "vertical_hand"
*horizontal_hand*:      pib holds his hand horizontal so an object can be placed on his hand
*vertical_hand*:        pib holds his hand vertical so it could hold a bottle upwards


#### pib_hand
*pib_hand* represents the hand configuration while performning the gesture
valid parameters:       "open_hand", "index_finger"

*index_finger*:         pib uses only the index finger to point at an object
*open_hand*:            pib uses a fully opened hand for more polite pointing gesture


#### return values        
for **point_to, greet_person, look_at, offer_hand, open_hand, close_hand**:
-  0:   gesture executed succesfully
-  1:   calculated successfully, but joint angles for dedicated gesture are out of limits
-  2:   faulty gesture parameters
- -1:   exception in execution

for **locate_object**:
x, y, z **(object_vector)** coordinates from pibs central upper body coordinate system


#### Examples
Terminal 1:
```python
ros2 run pib_gestures_action pib_gestures_server.py
```

Terminal 2:
```python
ros2 run pib_gestures_action pib_gestures_client point_to \
    --x 1000 --y -200 --z -200 --pib_side left, -- pib_mode bent_arm --pib_hand open_hand

ros2 run pib_gestures_action pib_gestures_client greet_person \
    --x 1000 --y 800 --z -100 --pib_side right -- pib_mode wave

ros2 run pib_gestures_action pib_gestures_client look_at \
    --x 1000 --y -200 --z -200

ros2 run pib_gestures_action pib_gestures_client offer_hand \
    --pib_side right --pib_mode horizontal_hand

ros2 run pib_gestures_action pib_gestures_client close_hand \
    --pib_side right

ros2 run pib_gestures_action pib_gestures_client open_hand \
    --pib_side right

ros2 run pib_gestures_action pib_gestures_client locate_object \
    --x 800 --y -600 --z 300
```

### If no executable is found:

Execute these terminal commands:

cd ~/Task_Manager_Pib/src/pib_gestures_action/modules
chmod +x pib_gestures_client.py
chmod +x pib_gestures_server.py

cd ~/Task_Manager_Pib/src/pib_gestures_action/modules/pib_gestures/src/pib_gestures/core
chmod +x point_to_core.py
chmod +x greet_person_core.py
chmod +x look_at_core.py
chmod +x offer_hand_core.py
chmod +x open_hand_core.py
chmod +x close_hand_core.py
chmod +x locate_object_core.py