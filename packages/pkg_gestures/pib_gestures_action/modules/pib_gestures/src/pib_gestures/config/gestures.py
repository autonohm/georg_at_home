'''
gesture parameters
gestures use pre-defined combinations of joint angles
calling or adding combinations by dictionary keys
radians are used for calculation with DH matrices
degrees are used for joint angles
'''

import numpy as np

pib_side = dict(
    none = 'none',
    left = 'left',
    right = 'right'
)

pib_gesture = dict(
    none = 'none',
    straight_arm = 'straight_arm',
    bent_arm = 'bent_arm',
    wave = 'wave',
    shake_hands = 'shake_hands',
    look = 'look'
)

pib_hand = dict(
    none = 'none',
    index_finger = 'index_finger',
    open_hand = 'open_hand'
)

# shoulder angles for pointing modes
q_shoulder_vertical_bent_arm = np.radians(-60.0)
q_shoulder_horizontal_bent_arm = np.radians(70.0) 
q_shoulder_vertical_straight_arm = np.radians(0.0)
q_shoulder_horizontal_straight_arm = np.radians(0.0) 
q_shoulder_vertical_waving = np.radians(0.0)
q_shoulder_horizontal_waving = np.radians(0.0) 
q_shoulder_vertical_shake_hands = np.radians(-70.0)
q_shoulder_horizontal_shake_hands = np.radians(90.0) 

# elbow angles for pointing modes
q_elbow_straight_arm = np.radians(0.0)
q_elbow_bent_arm = np.radians(90.0)
q_elbow_waving = np.radians(70.0)
q_elbow_shake_hands = np.radians(70.0)
q_elbow_gesture_angle = 20.0 # angle for waving or shaking hands
q_elbow_zero_offset = np.radians(-45.0) # zero angle for elbow equals bent elbow by 45 degrees

# arm rotation angles for pointing modes and gestures
q_upper_rot_straight_finger = np.radians(-35.0)
q_lower_rot_straight_finger = np.radians(-35.0)
q_upper_rot_straight_hand = np.radians(10.0)
q_lower_rot_straight_hand = np.radians(10.0)
q_upper_rot_bent_finger = np.radians(0.0)
q_lower_rot_bent_finger = np.radians(-30.0)
q_upper_rot_bent_hand = np.radians(0.0)
q_lower_rot_bent_hand = np.radians(60.0)
q_upper_rot_waving = np.radians(0.0)
q_lower_rot_waving = np.radians(0.0)
q_upper_rot_shake_hands = np.radians(0.0)
q_lower_rot_shake_hands = np.radians(0.0)

# q_wrist angles
q_wrist = np.radians(0.0)

# finger angles for stretched and tilted fingers
finger_stretched = 0.0
thumb_stretched = 45.0
thumb_opposition_stretched = 0.0
finger_half_tilted = 45.0
thumb_half_tilted = 45.0
thumb_opposition_half_tilted = 45.0
finger_tilted = 90.0
thumb_tilted = 90.0
thumb_opposition_tilted = 90.0

# arm joint angle arrays for pointing mode and gesture combinations
arm_gesture_joint_angles = dict(
    straight_arm = dict(
        index_finger = np.degrees(np.array([
                        q_shoulder_vertical_straight_arm,
                        q_shoulder_horizontal_straight_arm,
                        q_upper_rot_straight_finger,
                        q_elbow_straight_arm + q_elbow_zero_offset,
                        q_lower_rot_straight_finger,
                        q_wrist]
                    )
        ),
        
        open_hand = np.degrees(np.array([
                        q_shoulder_vertical_straight_arm,
                        q_shoulder_horizontal_straight_arm,
                        q_upper_rot_straight_hand,
                        q_elbow_straight_arm + q_elbow_zero_offset,
                        q_lower_rot_straight_hand,
                        q_wrist]
                    )
        )
    ),

    bent_arm = dict(
        index_finger = np.degrees(np.array([
                        q_shoulder_vertical_bent_arm,
                        q_shoulder_horizontal_bent_arm,
                        q_upper_rot_bent_finger,
                        q_elbow_bent_arm + q_elbow_zero_offset,
                        q_lower_rot_bent_finger,
                        q_wrist]
                    )
        ),
                        
        open_hand = np.degrees(np.array([
                        q_shoulder_vertical_bent_arm,
                        q_shoulder_horizontal_bent_arm,
                        q_upper_rot_bent_hand,
                        q_elbow_bent_arm + q_elbow_zero_offset,
                        q_lower_rot_bent_hand,
                        q_wrist]
                    )
        )
    ),
    
    wave = dict(
        open_hand = np.degrees(np.array([
                        q_shoulder_vertical_waving,
                        q_shoulder_horizontal_waving,
                        q_upper_rot_waving,
                        q_elbow_waving + q_elbow_zero_offset,
                        q_lower_rot_waving,
                        q_wrist]
                    )
        )
    ),
    
    shake_hands = dict(
        open_hand = np.degrees(np.array([
                        q_shoulder_vertical_shake_hands,
                        q_shoulder_horizontal_shake_hands,
                        q_upper_rot_shake_hands,
                        q_elbow_shake_hands + q_elbow_zero_offset,
                        q_lower_rot_shake_hands,
                        q_wrist]
                    )
        )
    )
)

# hand joint angle combinations for pointing gesture       
# order is: index finger, middle finger, ring finger, pinky finger, thumb, thumb opposition
hand_gesture_joint_angles = dict( 
    index_finger = np.array([
                finger_stretched,
                finger_tilted,
                finger_tilted,
                finger_tilted,
                thumb_tilted,
                thumb_opposition_tilted]
            ),
                    
    open_hand = np.array([
                finger_stretched,
                finger_stretched,
                finger_stretched,
                finger_stretched,
                thumb_stretched,
                thumb_opposition_half_tilted]
            ),
            
    wave = np.array([
                finger_stretched,
                finger_stretched,
                finger_stretched,
                finger_stretched,
                thumb_stretched,
                thumb_opposition_stretched]
            ),
                    
    shake_hands = np.array([
                finger_stretched,
                finger_stretched,
                finger_stretched,
                finger_stretched,
                thumb_half_tilted,
                thumb_opposition_half_tilted]
            )
)   

# number of greeting movement iterations
greeting_movement_count = 3
