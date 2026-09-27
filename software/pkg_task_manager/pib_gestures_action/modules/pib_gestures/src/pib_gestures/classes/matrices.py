'''
DH matrix class
used for transformation of vectors considering joint angles
usage accordingly to Denavit-Hartenberg convention
'''

from ..config import param
from ..classes.vectors import Object_Vector

import numpy as np

class DH_Matrix:
    def __init__(self, name = " ", theta = 0.0 , d = 0.0, a = 0.0, alpha = 0.0):
        self.name = name
        self.theta = theta
        self.d = d
        self.a = a
        self.alpha = alpha
        self.update_angle()

    def update_angle(self, angle = 0.0):
        self.values = np.array([
        [ np.cos(self.theta + angle) , -np.sin(self.theta + angle) * np.cos(self.alpha) ,  np.sin(self.theta + angle) * np.sin(self.alpha) , self.a * np.cos(self.theta + angle) ],
        [ np.sin(self.theta + angle) ,  np.cos(self.theta + angle) * np.cos(self.alpha) , -np.cos(self.theta + angle) * np.sin(self.alpha) , self.a * np.sin(self.theta + angle) ],
        [             0.0            ,                 np.sin(self.alpha)               ,                 np.cos(self.alpha)               ,               self.d                ],
        [             0.0            ,                        0.0                       ,                        0.0                       ,                 1.0                 ]])
        
    def create_vector_from_multiplication(self, name, vector, side = 'none', gesture = 'none'):
        return Object_Vector.create_object_vector(name, np.matmul(self.values, vector.values), side, gesture)  
    
    def __mul__(self, matrix):
        matrix_temp = DH_Matrix("temporary transformation matrix")
        matrix_temp.values = np.matmul(self.values, matrix.values)
        return matrix_temp
        
    def __str__(self):
        return f"{self.name:s}:{self.build_value_string():s}"
        
    def build_value_string(self):
        value_string = "\n"
        for id_value_row in range(4):
            value_string += "[ "
            for id_value_column in range(4):
                value_string += str(np.round(self.values[id_value_row][id_value_column], 2)) + "  "
            value_string += "]\n"
        return value_string

