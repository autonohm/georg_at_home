'''
test scenario for pib locating an object 
1000 mm in front of pib, 500 mm to the right and 500 mm below
and calculating the vector from the center to the object
'''

from pib_gestures.locate_object import locate_object

if __name__ == "__main__":
    x_value = -1000
    y_value = 500
    z_value = 500
    
    locate_object(x_value, y_value, z_value)
