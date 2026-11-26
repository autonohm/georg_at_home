'''
test scenario for pib waving with the right arm to a person
1000 mm in front of pib, 200 mm to the left and 100 mm upwards
'''

from pib_gestures.greet_person import greet_person

if __name__ == "__main__":
    x_value = -1000
    y_value = -200
    z_value = 100
    pib_side = 'right'
    pib_gesture = 'wave'
    
    greet_person(x_value, y_value, z_value, pib_side, pib_gesture)
