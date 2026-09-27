'''
parameters for pib kinematics
distances between joint axis
arm length limits and joint limits 
'''

import numpy as np

# Parameters for DH matrices representing distances between different joints axis
DH_param = dict(
    H_Base = 100.0,
    L_Neck = 8.86,
    H_Neck = 67.5,
    L_Pitch = 48.0,
    L_Camera = 48.7,
    L_Arm = 216.3,
    L_Shoulder = 225.0
)

# arm length for checking if object is far away enough to not touch object when moving
arm_length_with_reserve = dict(
    none = 0.0,
    straight_arm = 800.0,
    bent_arm = 500.0,
    wave = 500.0,
    shake_hands = 500.0
)

# joint rotation direction invert parameters
# left and right corresponding joints do not all move the same directions
# goal is mirrored movement for both arms when using identical joint angles
# IMPORTANT: may depend on pib setup
# this configuration is adapted to assigned pib unit
joint_invert = dict(
    left = [-1.0, -1.0, 1.0, 1.0, 1.0, 1.0],
    right = [1.0, 1.0, -1.0, 1.0, -1.0, 1.0],
    head = [-1.0, 1.0]
)

# movement limits for joint angles:
# mechanical limits
# safety distance so arms do not touch body when moving 
joint_limits = dict(
    straight_arm = dict(
        lower = np.array([-90.0, -90.0, -90.0, -45.0, -90.0, -45.0]),
        upper = np.array([90.0, 90.0, 90.0, 90.0, 90.0, 45.0])
    ),
    
    bent_arm = dict(
        lower = np.array([-90.0, 0.0, -45.0, -45.0, -90.0, -45.0]),
        upper = np.array([0.0, 90.0, 90.0, 90.0, 90.0, 45.0])
    ),
    
    wave = dict(
        lower = np.array([-90.0, -90.0, -45.0, -25.0, -90.0, -45.0]),
        upper = np.array([90.0, 90.0, 45.0, 65.0, 90.0, 45.0])
    ),
    
    shake_hands = dict(
        lower = np.array([-90.0, 0.0, -30.0, -25.0, -90.0, -45.0]),
        upper = np.array([0.0, 90.0, 45.0, 55.0, 90.0, 45.0])
    ),
    
    look = dict(
        lower = np.array([-90.0, -40.0]),
        upper = np.array([90.0, 40.0])
    )
)

# minimum distance in y direction
# so shoulder horizontal does not move to 90 degree mechanical limit
# when pointing with straight arm
min_y_offset = 50.0
