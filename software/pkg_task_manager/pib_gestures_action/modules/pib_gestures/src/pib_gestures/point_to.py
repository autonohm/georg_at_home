'''
pointing function for pib
pib can point to an object with left or right arm
with different gestures

pointing gesture represents straight arm or bent arm

straight arm: arm rotations and elbow form a straight arm,
pointing orientation only by shoulder vertical and horizontal joints
bent_arm: shoulder vertical and horizontal move arm downwards
pointing orientation only by upper arm rotation and elbow

pib hand represents index finger or open hand
open hand used for more polite gesture or closer objects

vector from camera to object is required
center and pointing vector are calculated by DH matrices 
'''

from core import point_to
from config import gestures

import sys
    
def usage_info():
    print("Usage: python3.9 point_to.py x_value y_value z_value pib_side pib_gesture pib_hand\n")
    print("Required values are in float: x value, y value, z value\n")
    print("Optional values are:")
    print("pib_side in", gestures.pib_side.keys())
    print("pib_gesture in", gestures.pib_gesture.keys())
    print("pib_hand in", gestures.pib_hand.keys())
    print("global coordinate system, adapted to ros and onshape configuration:")
    print("x axis pointing against pib, y axis pointing to pibs right side, z axis pointing upwards\n")
    print("usage example: python3.9 pyoint_to.py -1000 500 -200 right bent_arm index_finger")

if __name__ == "__main__":
    if len(sys.argv) < 4 or len(sys.argv) > 7:
        print("Faulty parameter count")
        usage_info()
        sys.exit()
    
    camera_vector_x = float(sys.argv[1])
    camera_vector_y = float(sys.argv[2])
    camera_vector_z = float(sys.argv[3])   
    
    if len(sys.argv) > 4:
        pib_side = sys.argv[4]
        if pib_side not in gestures.pib_side.keys():
            usage_info()
            print("pointing side", pib_side)
            raise ValueError("pib side is faulty")
    else:
        pib_side = gestures.pib_side['none']
    
    if len(sys.argv) > 5:
        pib_gesture = sys.argv[5]
        if pib_gesture not in gestures.pib_gesture.keys():
            usage_info()
            print("pointing mode:", pib_gesture)
            raise ValueError("pib gesture is faulty")
    else:
        pib_gesture = gestures.pib_gesture['none']
        
    if len(sys.argv) > 6:
        pib_hand = sys.argv[6]
        if pib_hand not in gestures.pib_hand.keys():
            usage_info()
            print("pointing gesture:", pib_hand)
            raise ValueError("pib hand is faulty")
    else:
        pib_hand = gestures.pib_hand['none']
    
    point_to(camera_vector_x, camera_vector_y, camera_vector_z, pib_side, pib_gesture, pib_hand)

