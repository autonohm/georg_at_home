'''
core functionality of look at:

transformation of camera vector into vector from center to object by DH matrices
automatic choosing logic for pointing side and gestures if parameters are omitted
calculation of pointing vector for used pointing side and gesture
calculation of arm and hand joint angles for pointing vector
checking pointability considering vector length and joint limits
moving joints for used pointing gesture

IMPORTANT: joint rotation direction is adjusted to assigned pib unit
rotation direction may depend on pib setup
direction correction is done with param.joint_invert
'''

###from pib_sdk.control import *

from ..classes import Object_Vector as vectors
from ..utils import transform, logic, pib_control
from ..config import param, gestures

from pathlib import Path

import numpy as np
import sys, time
import logging.config

config_file = Path(__file__).parent.parent / "logging_utils" / "logger.config"
logging.config.fileConfig(config_file)

logger = logging.getLogger('pib_gestures.core')
    
def look_at(
    object_vector_x,
    object_vector_y,
    object_vector_z) -> int:

    logger.info("started, calculating center vector")
    
    # calculate vector from center to object, considering head joint angles
    object_vector_center = transform.calculate_object_vector_center(object_vector_x, object_vector_y, object_vector_z)
    logger.info("center vector calculation finished, calculating head vector")
    
    # calculate looking vector head
    object_vector_head = transform.calculate_head_vector(object_vector_center)
    logger.info("head vector calculation finished, calculating joint angles")
    
    # calculate joint angles for head
    q_look_head = transform.calculate_joint_angles_for_head_vector(object_vector_head)
    
    # checking joint limits by object distance and calculated joint angles
    head_limits_ok = transform.check_head_joint_limits(q_look_head, object_vector_head)
    if not head_limits_ok:
        logger.info("Head angles out of limits with chosen gesture")
        return 1
    logger.info("Confirmed head angles are within limits, adjusting joint rotation directions")
    
    # considering rotation directions for joint angles
    # left and right corresponding joints do not all move the same directions 
    # goal is mirrored movement for both arms when using identical joint angles
    q_look_head = transform.adjust_joint_rotation_direction(q_look_head, 'head')
    logger.info("adjusting joint rotation directions complete, setting up pib")
    
    # set up pib for movement
    ###pib_control.set_up_pib()
    ###head_joints = head # head from sdk.control
    logger.info("setting up pib complete, moving joints")
    
    # move joints 
    ###pib_control.move_joints(head_joints, q_look_head)
    
    time.sleep(3)
    
    logger.info("finished\n\n")
    
    return 0
