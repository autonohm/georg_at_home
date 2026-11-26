'''
vector transformation functions with DH matrices
using DH parameters from param
calculation of pointing vectors for chosen pointing side, mode and gesture
calculation of joint angles for desired pointing movement 
'''

#TODO import read joint angles function from pib_sdk
# from pib_sdk.robot import Robot

from pib_gestures.geometry.matrices import DH_Matrix
from pib_gestures.geometry.vectors import Object_Vector
from pib_gestures.config import param, gestures

import numpy as np
import logging
logger = logging.getLogger(__name__)

np.set_printoptions(formatter = {'float_kind': lambda value: f"{value:6.2f}"})

# get current angles for head joints
def get_head_joint_angles_in_radians():
    #with Robot(host = "pib.local") as robot:
    #    current_turn_angle = np.radians(robot.telemetry.get_position_deg("turn_head_motor"))
    #    current_tilt_angle = np.radians(robot.telemetry.get_position_deg("tilt_head_motor"))
    current_turn_angle = np.radians(0.0)
    current_tilt_angle = np.radians(0.0)
    return current_turn_angle, current_tilt_angle
    
    
# transformation from camera vector to absolute vector from center to object considering head joint angles
# calculation with DH matrices on the base of camera vector and head orientation
def calculate_object_vector_center(object_vector_camera):
    logger.debug(object_vector_camera)
    
    # get head joint angles    
    angle_turn_joint, angle_tilt_joint = get_head_joint_angles_in_radians()
    logger.debug("angle turn joint in radians: " + str(angle_turn_joint))
    logger.debug("angle tilt joint in radians: " + str(angle_tilt_joint))
    logger.debug(__file__)
        
    # create DH matrices
    matrix_CAN = DH_Matrix("DH matrix center to neck point", 0.0, param.DH_param['H_Base'], param.DH_param['L_Neck'], 0.0)
    matrix_NAT = DH_Matrix("DH matrix neck point to turn joint", 0.0, param.DH_param['H_Neck'], param.DH_param['L_Tilt'], np.pi/2)
    matrix_TAC = DH_Matrix("DH matrix turn joint to camera center", 0.0, 0.0, param.DH_param['L_Camera'], -np.pi/2)
    matrix_NAT.update_angle(angle_turn_joint)
    matrix_TAC.update_angle(angle_tilt_joint)
    
    # final transformation matrix from camera vector to center vector
    matrix_center = matrix_CAN * matrix_NAT * matrix_TAC
    logger.debug("matrix_center, " + str(matrix_center))
    
    # transformation from camera vector to center vector
    object_vector_center = matrix_center.create_vector_from_multiplication(
        "vector from center to object", object_vector_camera
    )
    logger.debug(object_vector_center)
    
    return object_vector_center
    

# transformation from center vector to head vector to object
# calculation with DH matrices on the base of center vector and chosen pointing mode
def calculate_head_vector(object_vector_center):
    # DH matrix from neck to center
    matrix_head = DH_Matrix("DH matrix from neck to center", 0.0, -param.DH_param['H_Base'] - param.DH_param['H_Neck'], -param.DH_param['L_Neck'], 0.0)
    
    # transformation to looking vector
    object_vector_head = matrix_head.create_vector_from_multiplication(
        "head vector", object_vector_center,
        "none", "look"
    )   
    
    logger.debug("matrix_head, " + str(matrix_head))
    logger.debug(object_vector_head)
    
    return object_vector_head
    
    
# transformation from center vector to pointing vector to object
# calculation with DH matrices on the base of center vector and chosen pointing mode
def calculate_arm_vector(object_vector_center, pib_side, pib_mode):
    # DH matrix from chosen side to center
    if pib_side == gestures.pib_side['left']:
        matrix_side = DH_Matrix("DH matrix left shoulder horizontal to center", 0.0, param.DH_param['L_Shoulder'], 0.0, -np.pi/2)
    if pib_side == gestures.pib_side['right']:
        matrix_side = DH_Matrix("DH matrix right shoulder horizontal to center", 0.0, -param.DH_param['L_Shoulder'], 0.0, -np.pi/2)
    # DH matrices for chosen gesture
    if pib_mode == gestures.pib_gesture_modes['point_to']['straight_arm']:
        matrix_arm = DH_Matrix("DH matrix shoulder environment to shoulder horizontal", 0.0, 0.0, 0.0, np.pi/2)
    if pib_mode == gestures.pib_gesture_modes['greet_person']['wave']:
        matrix_arm = DH_Matrix("DH matrix shoulder environment to shoulder horizontal", 0.0, 0.0, 0.0, np.pi/2)
    if pib_mode == gestures.pib_gesture_modes['point_to']['bent_arm']:
        matrix_GAE = DH_Matrix("DH matrix gesture environment to elbow", 0.0, 0.0, 0.0, np.pi/2)
        matrix_EAR = DH_Matrix("DH matrix elbow to upper arm rotation", 0.0, -param.DH_param['L_Arm'], 0.0, -np.pi/2)
        matrix_RAH = DH_Matrix("DH matrix upper arm rotation to shoulder horizontal", 0.0, 0.0, 0.0, np.pi/2)
        matrix_HAV = DH_Matrix("DH matrix shoulder horizontal to shoulder vertical", 0.0, 0.0, 0.0, 0.0) 
        matrix_RAH.update_angle(-gestures.q_shoulder_horizontal_bent_arm)
        matrix_HAV.update_angle(-gestures.q_shoulder_vertical_bent_arm)
        matrix_arm = matrix_GAE * matrix_EAR * matrix_RAH * matrix_HAV
    if pib_mode == gestures.pib_gesture_modes['greet_person']['shake_hands']:
        matrix_GAE = DH_Matrix("DH matrix gesture environment to elbow", 0.0, 0.0, 0.0, np.pi/2)
        matrix_EAR = DH_Matrix("DH matrix elbow to upper arm rotation", 0.0, -param.DH_param['L_Arm'], 0.0, -np.pi/2)
        matrix_RAH = DH_Matrix("DH matrix upper arm rotation to shoulder horizontal", 0.0, 0.0, 0.0, np.pi/2)
        matrix_HAV = DH_Matrix("DH matrix shoulder horizontal to shoulder vertical", 0.0, 0.0, 0.0, 0.0)
        matrix_RAH.update_angle(-gestures.q_shoulder_horizontal_shake_hands)
        matrix_HAV.update_angle(-gestures.q_shoulder_vertical_shake_hands)
        matrix_arm = matrix_GAE * matrix_EAR * matrix_RAH * matrix_HAV  
        
    # transformation to the used point side
    object_vector_side = matrix_side.create_vector_from_multiplication(
        "side vector", object_vector_center,
         pib_side, pib_mode
    )
    
    # inverting vector z axis if side is left to mirror match right side orientations
    # allows usage of same matrices for both sides
    if pib_side == gestures.pib_side['right']:
        object_vector_side.invert_axis('z')
    
    # final transformation from side vector to pointing vector
    object_vector_arm = matrix_arm.create_vector_from_multiplication(
        "gesture vector", object_vector_side,
        pib_side, pib_mode
    )
    
    logger.debug("matrix_side, " + str(matrix_side))
    logger.debug("matrix_arm, " + str(matrix_arm))
    logger.debug(object_vector_arm)

    return object_vector_arm


# calculation of required joint angles for desired pointing movement
# joint angles are not checked yet if they are in joint limits
def calculate_joint_angles_for_arm_vector(vector, pib_hand):
    q_deg_hand = gestures.hand_gesture_joint_angles[pib_hand].copy()
    q_deg_arm = gestures.arm_gesture_joint_angles[vector.mode][pib_hand].copy()
    
    # calculation on the base of trigonometrical relations
    # base is central shoulder point 
    if vector.mode == gestures.pib_gesture_modes['point_to']['straight_arm']:
        q_shoulder_vertical = np.arctan2(vector.z, vector.x)
        q_shoulder_horizontal = np.arctan2(np.sqrt(vector.x * vector.x + vector.z * vector.z), vector.y)
        q_deg_arm[0] = np.degrees(q_shoulder_vertical)
        q_deg_arm[1] = np.degrees(q_shoulder_horizontal)
    
    # base is central elbow point
    if vector.mode == gestures.pib_gesture_modes['point_to']['bent_arm']:
        q_upper_arm_rotation = np.arctan2(vector.x, vector.z)
        q_elbow = np.arctan2(vector.y, np.sqrt(vector.x * vector.x + vector.z * vector.z))
        q_deg_arm[2] = np.degrees(q_upper_arm_rotation)
        q_deg_arm[3] += np.degrees(q_elbow)
        
    # base is central shoulder point 
    if vector.mode == gestures.pib_gesture_modes['greet_person']['wave']:
        q_shoulder_horizontal = -np.arctan2(vector.y, vector.x)
        q_shoulder_vertical = np.arctan2(vector.z, np.sqrt(vector.x * vector.x + vector.y * vector.y))
        q_deg_arm[0] = np.degrees(q_shoulder_vertical)
        q_deg_arm[1] = np.degrees(q_shoulder_horizontal)
    
    # base is central elbow point
    if vector.mode == gestures.pib_gesture_modes['greet_person']['shake_hands']:
        q_upper_arm_rotation = np.arctan2(vector.x, vector.z)
        q_elbow = np.arctan2(vector.y, np.sqrt(vector.x * vector.x + vector.z * vector.z))
        q_deg_arm[2] = np.degrees(q_upper_arm_rotation)
        q_deg_arm[3] += np.degrees(q_elbow)
        
    logger.debug("arm joint angles:  " + str(q_deg_arm))
    logger.debug("hand joint angles: " + str(q_deg_hand))
    
    return q_deg_arm, q_deg_hand  

   
# calculate angles for head motors to directly look at object
def calculate_joint_angles_for_head_vector(vector):
    q_turn_head = np.arctan2(vector.y, vector.x)
    q_tilt_head = np.arctan2(vector.z, np.sqrt(vector.x * vector.x + vector.y * vector.y))
    q_deg_head = np.degrees(np.array([q_turn_head, q_tilt_head]))
    
    logger.debug("head joint angles: " + str(q_deg_head))
    
    return q_deg_head  

# check if arm joint angles are within limits and object is far away not to touch it
def check_arm_angle_and_distance_limits(vector, q_gesture_arm):
    limits_ok = False
    if vector.mode == gestures.pib_gesture_modes['point_to']['straight_arm']:
        limits_ok = (q_gesture_arm >= param.joint_limits[vector.mode]['lower']).all() and (q_gesture_arm <= param.joint_limits[vector.mode]['upper']).all() and vector.y > param.min_y_offset
    else:
        limits_ok = (q_gesture_arm >= param.joint_limits[vector.mode]['lower']).all() and (q_gesture_arm <= param.joint_limits[vector.mode]['upper']).all()
    
    distance_ok = vector.length > param.arm_length_with_reserve[vector.mode]
            
    logger.debug("upper arm joint limits for " + vector.mode + ": " + str(param.joint_limits[vector.mode]['upper']))
    logger.debug("using arm joint angles for " + vector.mode + ": " + str(q_gesture_arm))
    logger.debug("lower arm joint limits for " + vector.mode + ": " + str(param.joint_limits[vector.mode]['lower']))
    logger.debug("distance okay: " + str(distance_ok) + ", limits okay: " + str(limits_ok))
    logger.debug("\n\n ")
    
    return limits_ok and distance_ok 

# check if head joint angles are within limits
def check_head_joint_limits(q_look_head, vector):
    limits_ok = (q_look_head >= param.joint_limits[vector.mode]['lower']).all() and (q_look_head <= param.joint_limits[vector.mode]['upper']).all()
    
    logger.debug("upper head joint limits for " + vector.mode + ": " + str(param.joint_limits[vector.mode]['upper']))
    logger.debug("using head joint angles for " + vector.mode + ": " + str(q_look_head))
    logger.debug("lower head joint limits for " + vector.mode + ": " + str(param.joint_limits[vector.mode]['lower']))
    logger.debug("limits okay: " + str(limits_ok))
    logger.debug("\n\n ")
    
    return limits_ok

# adjust the joint rotation direction for mirrored movement when using identical angles
# IMPORTANT: may depend on pib setup
def adjust_joint_rotation_direction(deg_angles, pib_joint_group):
    return deg_angles * param.joint_invert[pib_joint_group]
