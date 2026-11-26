'''
test scenario for pib looking at an object 
900 mm in front of pib, 400 mm to the right and 200 mm upwards
'''

from pib_gestures.look_at import look_at

if __name__ == "__main__":
    x_value = -900
    y_value = 400
    z_value = 200

    look_at(x_value, y_value, z_value)
