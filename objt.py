import numpy as np
import math


class Ray:
    def __init__(self, origin=None, direction=None, depth=0):
        self.depth = depth
        self.rayDirect = direction/np.linalg.norm(direction) if  direction is not None else np.array([0,0,0])
        self.origin = origin
    

    def at(self, t):
        return self.origin + self.direction * t

    # ray through pixel equation 
    # P(r,c) - eye --> (-Nn + W((2c/nCols) - 1)u + H((2r/nRows)-1)v) 
    def fromPixel(self,r,c,near,left,right,bottom,top,nCols,nRows):
        W = (right - left) / 2
        H = (top - bottom) / 2

        
        u = W * (((2 * c)/nCols) - 1)
        v = H * (((2 * r)/nRows) - 1)

        # P(r,c-eye)
        rayDirect = np.array([u,-v,-near])
        self.rayDirect = rayDirect /np.linalg.norm(rayDirect)
        

class Sphere:
    def __init__(self, name, position, scale, color,ka, kd, ks, kr, n):
        self.name = name
        self.position = position
        self.scale = scale
        self.color = color
        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.kr = kr 
        self.n = n

        translation = np.array([
            [1, 0, 0, self.position[0]],
            [0, 1, 0, self.position[1]],
            [0, 0, 1, self.position[2]],
            [0, 0, 0, 1]
        ])
        
        # Scale matrix
        scale = np.array([
            [self.scale[0], 0, 0, 0],
            [0, self.scale[1], 0, 0],
            [0, 0, self.scale[2], 0],
            [0, 0, 0, 1]
        ])

        translationInv = np.array([
            [1, 0, 0, -self.position[0]],
            [0, 1, 0, -self.position[1]],
            [0, 0, 1, -self.position[2]],
            [0, 0, 0, 1]
        ])
        
        # Scale matrix
        scaleInv = np.array([
            [1/self.scale[0], 0, 0, 0],
            [0, 1/self.scale[1], 0, 0],
            [0, 0, 1/self.scale[2], 0],
            [0, 0, 0, 1]
        ])

        # Combined transform
        self.transform = np.dot(translation, scale)
        
        # inverse
        self.inverseTransform = np.dot(scaleInv, translationInv)

        # transpose
        self.normTransform = self.inverseTransform.T[:3, :3]
