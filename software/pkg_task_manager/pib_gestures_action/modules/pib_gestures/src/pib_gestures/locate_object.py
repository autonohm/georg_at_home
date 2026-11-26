'''
locate object function for pib
pib can locate an object with the depth camera

current turn and tilt head joint angles are considered through calculation
object vector from center to object is calculated by DH matrices

vector from camera to object is required
'''

from core.locate_object_core import locate_object as locate_object_core
from geometry import Object_Vector

import argparse
    


def locate_object(
    x_value,
    y_value,
    z_value
):
    """pib calculates the position of an object detected with the depth camera"""

    object_vector_camera = Object_Vector.create_object_vector(
        "vector from camera to object",
        (float(x_value), float(y_value), float(z_value)),
    )

    return locate_object_core(object_vector_camera)
    


def main():
    parser = argparse.ArgumentParser(
        description = "pib calculates the position of an object detected with the depth camera"
    )

    parser.add_argument("x", type = float, help = "X coordinate of the object")
    parser.add_argument("y", type = float, help = "Y coordinate of the object")
    parser.add_argument("z", type = float, help = "Z coordinate of the object")
    
    args = parser.parse_args()
    print(locate_object(args.x, args.y, args.z))
    
    
    
if __name__ == "__main__":
    main()
