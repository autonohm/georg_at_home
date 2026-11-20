'''
greeting function for pib
pib can greet a person with left or right arm
with different gestures

greeting gesture represents waving or shake hands

vector with x- y- and z-values from camera to person is required
center and greeting vector are calculated by DH matrices 
'''

from core import greet_person
from config import gestures

import sys
    
def usage_info():
    print("Usage: python3.9 greet_to.py x_value y_value z_value pib_side pib_gesture\n")
    print("Required values are in float: x value, y value, z value\n")
    print("Optional values are:")
    print("pib_side in", gestures.pib_side.keys())
    print("pib_gesture in", gestures.pib_gesture.keys())
    print("global coordinate system, adapted to ros and onshape configuration:")
    print("x axis pointing against pib, y axis pointing to pibs right side, z axis pointing upwards\n")
    print("usage example: python3.9 greet_person.py -1000 500 -200 right wave")

if __name__ == "__main__":
    if len(sys.argv) < 4 or len(sys.argv) > 6:
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
            print("pib side", pib_side)
            raise ValueError("pib side is faulty")
    else:
        pib_side = gestures.pib_side['none']
    
    if len(sys.argv) > 5:
        pib_gesture = sys.argv[5]
        if pib_gesture not in gestures.pib_gesture.keys():
            usage_info()
            print("pib gesture:", pib_gesture)
            raise ValueError("pib gesture is faulty")
    else:
        pib_gesture = gestures.pib_gesture['none']
    
    greet_person(camera_vector_x, camera_vector_y, camera_vector_z, pib_side, pib_gesture)

