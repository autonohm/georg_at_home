'''
core functionality of greeting function:

transformation of camera vector into vector from center to object by DH matrices
automatic choosing logic for greeting side and gesture if parameters are omitted
calculation of gesture vector for used greeting side  and gesture
calculation of arm and hand joint angles for gesture vector
checking joint angles and distance considering vector length and joint limits
moving joints for used gesture

IMPORTANT: joint rotation direction is adjusted to assigned pib unit
rotation direction may depend on pib setup
direction correction is done with param.joint_invert
'''

###from pib_sdk.control import *

from ..classes import Object_Vector as vectors
from ..utils import transform, logic, pib_control
from ..config import param, gestures
from ..core import look_at

from pathlib import Path

import time
import numpy as np
#import logging.config

#config_file = Path(__file__).parent.parent / "logging_utils" / "logger.config"
#logging.config.fileConfig(config_file)
#logger = logging.getLogger('pib_gestures.core')

def greet_person(
    object_vector_x,
    object_vector_y,
    object_vector_z,
    pib_side = gestures.pib_side['none'],
    pib_gesture = gestures.pib_gesture['none']) -> int:
    
    # logger.info("started, calculating center vector")
   
    # calculate vector from center to object, considering head joint angles
    object_vector_center = transform.calculate_object_vector_center(object_vector_x, object_vector_y, object_vector_z)
    # logger.info("center vector calculation finished, running gesture choosing logic")
    
    # Selecting greeting gesture if side, mode or gesture parameters are omitted
    pib_side, pib_gesture, pib_hand = logic.greeting_gesture_logic(object_vector_center, pib_side, pib_gesture)
    # logger.info("gesture set, calculating arm vector")
    
    # calculate object vector from pointing side and mode
    object_vector_arm = transform.calculate_arm_vector(object_vector_center, pib_side, pib_gesture)
    # logger.info("arm vector calculation finished, calculating joint angles")
    
    # calculate joint angles for gesture
    q_gesture_arm, q_gesture_hand = transform.calculate_joint_angles_for_arm_vector(object_vector_arm, pib_hand)
    # logger.info("joint angle calculation finished, checking joint angle and distance limits")
    
    # checking joint limits by object distance and calculated joint angles
    gesture_limits_ok = transform.check_arm_angle_and_distance_limits(object_vector_arm, q_gesture_arm)
    if not gesture_limits_ok:
        # logger.info("arm angles out of limits with chosen gesture")
        return 1
    # logger.info("confirmed arm angles are within limits, adjusting joint rotation directions")
    
    # considering rotation directions for joint angles
    # left and right corresponding joints do not all move the same directions 
    # goal is mirrored movement for both arms when using identical joint angles
    q_gesture_arm = transform.adjust_joint_rotation_direction(q_gesture_arm, pib_side)
    # logger.info("adjusting joint rotation directions complete, moving joints")
    
    # look at object
    look_at.look_at(object_vector_center.x, object_vector_center.y, object_vector_center.z)
    
    # using arm objects from pib sdk
    if pib_side == gestures.pib_side['left']:
        pass
        ###arm_joints = left_arm # left_arm from sdk.control
        ###hand_joints = left_hand # left hand from sdk.control
        ###elbow_joint = 'elbow_left' # left elbow from sdk.control
    if pib_side == gestures.pib_side['right']:
        pass
        ###arm_joints = right_arm # right_arm from sdk.control
        ###hand_joints = right_hand # right_hand from sdk.control
        ###elbow_joint = 'elbow_right' # right elbow from sdk.control
    
    # logger.info("publishing joint angles")
    # move joints 
    ###pib_control.move_joints(hand_joints, q_gesture_hand)    
    ###pib_control.move_joints(arm_joints, q_gesture_arm)
    
    # Waiting a moment if gesture is shake hands, so person can take pibs hand before shaking
    # in future: use hand sensors to verify person has taken pibs hand, then shake
    if pib_gesture == gestures.pib_gesture['shake_hands']:
        time.sleep(2)
        
    for number in range(gestures.greeting_movement_count): 
        # waving or shaking hands is identical movement for elbow
        ###pib_control.move_joints(elbow_joint, [q_gesture_arm[3] + gestures.q_elbow_gesture_angle])
        time.sleep(0.5)
        ###pib_control.move_joints(elbow_joint, [q_gesture_arm[3] - gestures.q_elbow_gesture_angle])
        time.sleep(0.5)
        
    # logger.info("gesture executed")
    
    # Waiting a moment if gesture is shake hands, so person can let go pibs hand after shaking
    # in future: use hand sensors to verify person has let go pibs hand, then move back
    if pib_gesture == gestures.pib_gesture['shake_hands']:
        time.sleep(2)
        
    # Move back into zero position
    ###pib_control.move_joints(arm_joints, [0.0])
    ###pib_control.move_joints(hand_joints, [0.0])
    
    look_at.look_at(0, 0, 0)

    # logger.info("finished\n\n")
    
    return 0
