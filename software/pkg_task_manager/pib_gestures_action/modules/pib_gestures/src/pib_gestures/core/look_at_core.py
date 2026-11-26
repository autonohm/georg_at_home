'''
core functionality of look at:

vector from center to object is required
calculation of looking vector by DH matrices
calculation of yaw and pitch joint angles for looking vector
considering joint limits and moving joints if within limits

IMPORTANT: joint rotation direction is adjusted to assigned pib unit
rotation direction may depend on pib setup
direction correction is done with param.joint_invert
'''

from pib_gestures.utils import transform, pib_control
from pib_sdk.control import *

from pathlib import Path

import logging.config

config_file = Path(__file__).parent.parent / "logging_utils" / "logger.config"
logging.config.fileConfig(config_file)
logger = logging.getLogger('pib_gestures.core')
    
def look_at(object_vector_center):

    logger.info("started, calculating head vector")
    
    # calculate looking vector head
    object_vector_head = transform.calculate_head_vector(object_vector_center)
    logger.info("head vector calculation finished, calculating joint angles")
    
    # calculate joint angles for head
    q_look_head = transform.calculate_joint_angles_for_head_vector(object_vector_head)
    
    # checking joint limits by object distance and calculated joint angles
    joint_limits_ok = transform.check_head_joint_limits(q_look_head, object_vector_head)
    if not joint_limits_ok:
        logger.info("Head angles out of limits with chosen coordinates")
        return 1
        
    logger.info("Confirmed head angles are within limits, adjusting joint rotation directions")
    
    # considering rotation directions for joint angles
    # left and right corresponding joints do not all move the same directions 
    # goal is mirrored movement for both arms when using identical joint angles
    q_look_head = transform.adjust_joint_rotation_direction(q_look_head, 'head')
    logger.info("adjusting joint rotation directions complete, moving joints")
    
    ## set up pib for movement
    pib_control.set_up_pib()
    head_joints = head # head from sdk.control
    
    # move joints 
    pib_control.move_joints(head_joints, q_look_head)
    
    logger.info("finished\n\n ")
    
    return 0
