'''
core functionality of greeting function:

vector from center to object is required
automatic choosing logic for greeting side and mode if parameters are omitted

calculation of gesture vector for used greeting side and mode
calculation of arm and hand joint angles for gesture vector
checking joint angles and distance considering vector length and joint limits

IMPORTANT: joint rotation direction is adjusted to assigned pib unit
rotation direction may depend on pib setup
direction correction is done with param.joint_invert
'''

from pib_gestures.utils import transform, logic, pib_control
from pib_gestures.config import gestures
from pib_sdk.control import *

from pathlib import Path
import time

import logging.config

config_file = Path(__file__).parent.parent / "logging_utils" / "logger.config"
logging.config.fileConfig(config_file)
logger = logging.getLogger('pib_gestures.core')

def greet_person(
    object_vector_center,
    pib_side,
    pib_mode = "none"
):

    logger.info("started, running gesture choosing logic")
    
    # Selecting greeting gesture if side, mode or gesture parameters are omitted
    pib_side, pib_mode, pib_hand = logic.greeting_gesture_logic(object_vector_center, pib_side, pib_mode)
    logger.info("gesture configuration set, calculating arm vector")
    
    # calculate object vector from pointing side and mode
    object_vector_arm = transform.calculate_arm_vector(object_vector_center, pib_side, pib_mode)
    logger.info("arm vector calculation finished, calculating joint angles")

    # calculate joint angles for gesture
    q_gesture_arm, q_gesture_hand = transform.calculate_joint_angles_for_arm_vector(object_vector_arm, pib_hand)
    logger.info("joint angle calculation finished, checking joint angle and distance limits")
    
    # checking joint limits by object distance and calculated joint angles
    joint_limits_ok = transform.check_arm_angle_and_distance_limits(object_vector_arm, q_gesture_arm)
    if not joint_limits_ok:
        logger.info("arm angles out of limits with chosen gesture\n\n ")
        return 1
        
    logger.info("confirmed arm angles are within limits, adjusting joint rotation directions")
    
    # considering rotation directions for joint angles
    # left and right corresponding joints do not all move the same directions 
    # goal is mirrored movement for both arms when using identical joint angles
    q_gesture_arm = transform.adjust_joint_rotation_direction(q_gesture_arm, pib_side)
    
    # second gesture for waving or shaking hands movement
    q_gesture_arm_moving = q_gesture_arm.copy()
    q_gesture_arm_moving[3] = q_gesture_arm_moving[3] + gestures.q_elbow_gesture_angle
    logger.info("adjusting joint rotation directions complete, moving joints")
    
    # using objects from pib sdk
    if pib_side == gestures.pib_side['left']:
        arm_joints = left_arm # left_arm from sdk.control
        hand_joints = left_hand # left hand from sdk.control
    if pib_side == gestures.pib_side['right']:
        arm_joints = right_arm # right_arm from sdk.control
        hand_joints = right_hand # right_hand from sdk.control
    
    logger.info("publishing joint angles") 
    
    # move joints 
    pib_control.move_joints(hand_joints, q_gesture_hand)
    pib_control.move_joints(arm_joints, q_gesture_arm)
    
    # do gesture movement
    for movement_count in range(gestures.greeting_movement_count):
        time.sleep(0.2)
        pib_control.move_joints(arm_joints, q_gesture_arm_moving)
        time.sleep(0.2)
        pib_control.move_joints(arm_joints, q_gesture_arm)
    
    logger.info("finished\n\n ")
    
    return 0
