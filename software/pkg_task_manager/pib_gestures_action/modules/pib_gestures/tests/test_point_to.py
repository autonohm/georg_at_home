'''
test scenario for pib pointing to an object 
800 mm in front of pib, 100 mm to the left and 300 mm upwards
with the right bent arm and an open hand
'''

from pib_gestures.point_to import point_to

if __name__ == "__main__":
    x_value = -800
    y_value = -100
    z_value = 300
    pib_side = 'right'
    pib_gesture = 'bent_arm'
    pib_hand = 'open_hand'
    
    point_to(x_value, y_value, z_value, pib_side, pib_gesture, pib_hand)
