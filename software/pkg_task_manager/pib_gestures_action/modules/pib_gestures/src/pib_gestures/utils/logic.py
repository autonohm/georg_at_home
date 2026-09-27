'''
Function for choice of gesture configuration
3 optional parameters:
pib_side = which arm to use, left or right
pib_gesture = which arm position, straight arm or bent arm
pib_hand = which gesture to use, index finger or open hand

basic version:  omitted parameters are forced to defined preset

pro version:    function identifies the optimal pointing gesture (pib_side, pib_gesture and pib_hand)
                depending on object position, considering omitted or given parameters
'''

from ..classes.vectors import Object_Vector
from ..config import gestures

# import logging
# logger = logging.getLogger(__name__)

def pointing_gesture_logic(
    object_vector_center,
    pib_side = gestures.pib_side['none'],
    pib_gesture = gestures.pib_gesture['none'],
    pib_hand = gestures.pib_hand['none']):
    
    # TODO: implement true choosing logic depending on object position
    # object_vector_center needed for considering object localization area 
    
    # basic choosing function: simple setting omitted parameters
    if pib_side == gestures.pib_side['none']:
        pib_side = gestures.pib_side['right']
    if pib_gesture == gestures.pib_gesture['none']:
        pib_gesture = gestures.pib_gesture['bent_arm']
    if pib_hand == gestures.pib_hand['none']:
        pib_hand = gestures.pib_hand['open_hand']
        
    # logger.debug("Gesture set: " + str(pib_side) + " " + str(pib_gesture) + " " + str(pib_hand))

    return pib_side, pib_gesture, pib_hand




'''
Function for choice of greeting gesture
3 optional parameters:
pib_side = which arm to use, left or right
pib_gesture = which gesture to use, waving or shake hands

basic version:  omitted parameters are forced to defined preset

pro version:    function identifies the optimal greeting gesture (pib_side and pib_gesture)
                depending on person position, considering omitted or given parameters
'''

def greeting_gesture_logic(
    person_vector_center,
    pib_side = gestures.pib_side['none'],
    pib_gesture = gestures.pib_gesture['none']):

    # TODO: implement true choosing logic depending on person position
    # person_vector_center needed for considering object localization area 
    
    # basic choosing function: setting omitted parameters
    if pib_gesture == gestures.pib_gesture['none']:
        pib_gesture = gestures.pib_gesture['wave']
    if pib_side == gestures.pib_side['none'] or pib_gesture == gestures.pib_gesture['shake_hands']:
        pib_side = gestures.pib_side['right']
    
    # greeting always with open hand
    pib_hand = gestures.pib_hand['open_hand']
    
    # logger.debug("Gesture set: " + str(pib_side) + " " + str(pib_gesture) + " " + str(pib_hand))

    return pib_side, pib_gesture, pib_hand
