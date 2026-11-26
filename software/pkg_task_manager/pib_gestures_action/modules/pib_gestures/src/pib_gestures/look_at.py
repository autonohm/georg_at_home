'''
looking function for pib
pib can look to an object by rotating turn and tilt head joints

vector from center to object is required
looking vector is calculated by DH matrices 
'''

from core.look_at_core import look_at as look_at_core
from geometry import Object_Vector

import argparse
    


def look_at(
    x_value,
    y_value,
    z_value
):
    """pib looks towards an object at the given coordinates."""

    object_vector_center = Object_Vector.create_object_vector(
        "vector from center to object",
        (float(x_value), float(y_value), float(z_value)),
    )

    return look_at_core(object_vector_center)
    


def main():
    parser = argparse.ArgumentParser(
        description = "pib looks at an object at the given coordinates"
    )
    
    parser.add_argument("x", type = float, help = "X coordinate of the object")
    parser.add_argument("y", type = float, help = "Y coordinate of the object")
    parser.add_argument("z", type = float, help = "Z coordinate of the object")
    
    args = parser.parse_args()
    print(look_at(args.x, args.y, args.z))
    
    
    
if __name__ == "__main__":
    main()
