'''
Vector class 
4x1 vector
represents coordinates in x, y and z directions
parameter "one" is included for homogeneous transformations with DH matrices
'''

import numpy as np

class Object_Vector:
    def __init__(self, name, vector_values, side, mode):
        self.name = name
        self.x = vector_values[0]
        self.y = vector_values[1]
        self.z = vector_values[2]
        self.one = 1.0
        self.values = np.array([self.x, self.y, self.z, self.one]).transpose()
        self.length = np.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        self.side = side
        self.mode = mode     
            
    def invert_axis(self, axis):
        if axis == 'x':
            self.x *= -1
            self.values[0] *= -1
        if axis == 'y':
            self.y *= -1
            self.values[1] *= -1
        if axis == 'z':
            self.z *= -1
            self.values[2] *= -1
    
    def __str__(self):
        return_string = self.name + ", x = " + str(np.round(self.x, 2)) + ", y = " + str(np.round(self.y, 2)) + ", z = " + str(np.round(self.z, 2))
        return_string += ", length = " + str(np.round(self.length, 2))
        return_string += ", pointing side: " + self.side
        return_string += ", pointing mode: " + self.mode
        return return_string
        
    def create_object_vector(name, vector_values, side = 'none', mode = 'none'):
        return Object_Vector(name, vector_values, side, mode)

