'''
Function for choice of gesture configuration
3 optional parameters:
pib_side = which arm to use, left or right
pib_mode = which arm position, straight arm or bent arm
pib_hand = which gesture to use, index finger or open hand

basic version:  omitted parameters are forced to defined preset

pro version:    function identifies the optimal pointing gesture (pib_side, pib_mode and pib_hand)
                depending on object position, considering omitted or given parameters
'''

from pib_gestures.geometry.vectors import Object_Vector
from pib_gestures.config import gestures

import logging
logger = logging.getLogger(__name__)

def pointing_gesture_logic(
    object_vector_center,
    pib_side,
    pib_mode = "none",
    pib_hand = "none"
):
    
    logger.debug("Parameters for pointing loaded : " + str(pib_side) + " " + str(pib_mode) + " " + str(pib_hand))
    
    # TODO: implement true choosing logic depending on object position
    # object_vector_center needed for considering object localization area 
    
    # basic choosing function: simple setting omitted parameters
    if pib_mode == "none":
        pib_mode = gestures.pib_gesture_modes['point_to']['bent_arm']
    if pib_hand == "none":
        pib_hand = "open_hand"
        
    logger.debug("Gesture configuration set: " + str(pib_side) + " " + str(pib_mode) + " " + str(pib_hand))
    logger.debug("\n\n ")

    return pib_side, pib_mode, pib_hand




'''
Function for choice of greeting gesture
3 optional parameters:
pib_side = which arm to use, left or right
pib_mode = which gesture mode to use, waving or shake hands

basic version:  omitted parameters are forced to defined preset

pro version:    function identifies the optimal greeting gesture (pib_side and pib_gesture)
                depending on person position, considering omitted or given parameters
'''

def greeting_gesture_logic(
    person_vector_center,
    pib_side,
    pib_mode = "none"
):
    
    logger.debug("Parameters for greeting loaded : " + str(pib_side) + " " + str(pib_mode))

    # TODO: implement true choosing logic depending on person position
    # person_vector_center needed for considering object localization area 
    
    # basic choosing function: setting omitted parameters
    if pib_mode == "none":
        pib_mode = gestures.pib_gesture_modes['greet_person']['wave']
    
    # greeting always with open hand
    pib_hand = "open_hand"
    
    logger.debug("Gesture configuration set: " + str(pib_side) + " " + str(pib_mode) + " " + str(pib_hand))
    logger.debug("\n\n ")

    return pib_side, pib_mode, pib_hand
