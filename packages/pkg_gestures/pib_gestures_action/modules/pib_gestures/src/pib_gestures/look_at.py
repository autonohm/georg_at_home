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

from core import look_at
from config import gestures

import sys
    
def usage_info():
    print("Usage: python3.9 look_at.py x_value y_value z_value\n")
    print("Required values are in float: x value, y value, z value\n")
    print("global coordinate system, adapted to ros and onshape configuration:")
    print("x axis pointing against pib, y axis pointing to pibs right side, z axis pointing upwards\n")
    print("usage example: python3.9 pyoint_to.py -1000 500 -200")

if __name__ == "__main__":
    if not len(sys.argv) == 4:
        print("Faulty parameter count")
        usage_info()
        sys.exit()
    
    camera_vector_x = float(sys.argv[1])
    camera_vector_y = float(sys.argv[2])
    camera_vector_z = float(sys.argv[3])   
    
    look_at(camera_vector_x, camera_vector_y, camera_vector_z)

