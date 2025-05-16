import sys
import os
import time
import numpy as np
import math
from objt import Ray, Sphere

MAX_DEPTH = 4
toPrint = False

# use given PPM code and converted into python code
# create file and draw into PPM format
def saveImageP6(width, height, name, pixel):
    maxVal = 255
    with open(name, "wb") as file:
        file.write(b"P6\n")
        file.write(f"{width} {height}\n".encode())
        file.write(f"{maxVal}\n".encode())

        for j in range(height):
            start_index = j * width * 3
            pixel_row = bytes()
            for i in range(width):
                r = pixel[start_index + i * 3 + 0]
                g = pixel[start_index + i * 3 + 1]
                b = pixel[start_index + i * 3 + 2]
                pixel_row += bytes([int(r), int(g), int(b)]) 
            file.write(pixel_row)
        file.close()


# read content of the file
# return a tuple of the content
def readFile(fileName):

    # variable
    near = 0
    left = 0
    right = 0 
    bottom = 0
    top = 0
    # x-y
    res = [0,0]
    # list of sphere that is in the scene
    listSphere = []
    # list of lights that is in the scene
    listLight = []
    # r-g-b
    back = [0,0,0]
    #  r-g-b
    ambient = [0,0,0]
    # string
    output = None

    if not os.path.exists(fileName):
        exit("File does not exist")

    with open(fileName, "r") as file:
        for line in file:
            
            line = line.strip()
            token = line.split()
            if not token:
                continue
            if token[0] == "NEAR":
                near = token[1]
            if token[0] == "LEFT":
                left = token[1]
            if token[0] == "RIGHT":
                right = token[1]
            if token[0] == "BOTTOM":
                bottom = token[1]
            if token[0] == "TOP":
                top = token[1]
            if token[0] == "RES":
                res[0] = token[1]
                res[1] = token[2]
            if token[0] == "SPHERE":
                listSphere.append(token[1:])
            if token[0] == "LIGHT":
                listLight.append(token[1:])
            if token[0] == "BACK":
                back[0] = token[1]
                back[1] = token[2]
                back[2] = token[3]
            if token[0] == "AMBIENT":
                ambient[0] = token[1]
                ambient[1] = token[2]
                ambient[2] = token[3]    
            if token[0] == "OUTPUT":
                output = token[1]
    
    return (near, left, right, bottom, top, res, listSphere, listLight, back, ambient, output)


# function for drawing the ray trace image
# draw sphere
# draw background
# draw intersection
# draw reflection
# draw shadow
# draw specular
# return color for the pixel
def quadraticT(A,B,C, inPLane):
    discriminant = B*B - A*C
    
    discriminant = round(discriminant,12)
    if discriminant < 0:
        return None  # No real solutions
    
    t1 = (-B - math.sqrt(discriminant))/A
    t2 = (-B + math.sqrt(discriminant))/A
    t = None

    if inPLane:
        if t1 > 0 and t2 > 0:
            t = max(t1, t2)
        elif t1 > 0:
            t = t1
        elif t2 > 0:
            t = t2
    else:
        if t1 > 0 and t2 > 0:
            t = min(t1, t2)
        elif t1 > 0:
            t = t1
        elif t2 > 0:
            t = t2

    return t # Two real solutions

    
def findIntersect(ray, sphere, inPlane):
    
    # inverse transformed ray for spheres
    sphereObj = (ray.origin - sphere.position) / sphere.scale
    sphereDirObj = ray.rayDirect  /  sphere.scale

    # find A B C quadratic
    A = np.dot(sphereDirObj,sphereDirObj)
    B = np.dot(sphereDirObj, sphereObj)
    C = np.dot(sphereObj, sphereObj) - 1.0

    # quadratic equation 
    t = quadraticT(A,B,C, inPlane)
    if t is None:
        return None


    # calculate intersect and normal in world
    intersect = sphereObj + t * sphereDirObj

    # transform intersect to homogenous
    intersectHomo = np.append(intersect, 1)
    intersectHomoWorld = np.dot(sphere.transform,intersectHomo)[:3]

    # TODO : normal Object 
    normObj = intersect/np.linalg.norm(intersect)

    # Transform normal to world
    normalWorldObj = np.dot(sphere.normTransform, normObj)
    normal = normalWorldObj/np.linalg.norm(normalWorldObj)

    if inPlane:
        normal = normal * -1

    return {"t":t,"intersectWorld":intersectHomoWorld,"normal":normal, "sphere": sphere}

def intersectSphere(ray, listSphere, shadow=False, lightDistance=math.inf):
    closestIntersect = None
    minT = math.inf

    for mainSphere in listSphere:
        
        inPlane = False  
        if not shadow:
            if mainSphere.position[2] + mainSphere.scale[2] > -1:
                inPlane = True
            
        intersect = findIntersect(ray, mainSphere, inPlane)

        if intersect:
            if shadow:
                if intersect["t"] < lightDistance and intersect["t"] > 0:
                    return intersect 
            else:
                if inPlane:
                    if (ray.origin + ray.rayDirect * intersect["t"])[2] < -1:
                        if intersect["t"] < minT:
                            minT = intersect["t"]
                            closestIntersect = intersect
                else:
                    if intersect["t"] < minT:
                        minT = intersect["t"]
                        closestIntersect = intersect
    
    return closestIntersect

def isShadow(intersection, lightDirect, lightDistance, listSphere):
    # create shadow ray with a small offset to avoid self-intersection
    shadow_ray = Ray(intersection + lightDirect * 0.000001, lightDirect)
    
    # check for intersection between point and light
    intersect = intersectSphere(shadow_ray, listSphere, True, lightDistance)
    
    return intersect is not None

def drawRayTrace(ray, ambientInput , background, listSphere, listLight, reflected):

    if ray.depth > MAX_DEPTH:
        return 0.0,0.0,0.0
    
    # get all the t
    intersect = intersectSphere(ray, listSphere)
    
    if intersect is None:
        if reflected:
            return 0.0,0.0,0.0
        R = float(background[0])
        G = float(background[1])
        B = float(background[2])
        return R,G,B

    # seperate color into RGB
    sphere = intersect["sphere"]
    objectColor = sphere.color
    
    # ambient
    ambientLighting = np.array([float(ambientInput[0]),float(ambientInput[1]), float(ambientInput[2])])
    ambient = sphere.ka * objectColor * ambientLighting
    color = ambient

    # normal
    normal = intersect["normal"]
    
    # intersect
    interSectionPoint = intersect["intersectWorld"]

    # diffuse
    kd = sphere.kd

    # specular
    ks = sphere.ks
    specExp = sphere.n
    Ve = -interSectionPoint
    Ve = Ve/np.linalg.norm(Ve)

    # reflection
    kr = sphere.kr

    for light in listLight:                

        # extract light information
        lightX = float(light[1])
        lightY = float(light[2])
        lightZ = float(light[3])
        lightIr = float(light[4])
        lightIg = float(light[5])
        lightIb = float(light[6])

        lightPos = np.array([lightX, lightY, lightZ])
        lightColor = np.array([lightIr, lightIg, lightIb])

        # light direction
        lightDirect = lightPos - interSectionPoint
        lightDistance = np.linalg.norm(lightDirect)
        
        # shadow test
        if isShadow(interSectionPoint, lightDirect, lightDistance,listSphere):
            continue

        # normalize light
        lightDirect = lightDirect/lightDistance

        # Lambert's Law  = Il Kd (n * L)
        normLightD = max(np.dot(normal, lightDirect),0)
        # Il(light source intensity) * Kd(reflectance) * normLightD
        diffuse = objectColor *  (kd  * lightColor) * normLightD 

        # 2(n⋅L)n - L
        R = 2 * (np.dot(normal,lightDirect)) * normal - lightDirect

        # specular Is = Li * Ks * (H * N)**n
        normLightS = pow(max(np.dot(R,Ve),0.0),specExp)
        specular = ks * lightColor * normLightS

        color = color + diffuse + specular

    # reflection
    if kr > 0 :
        # V = -2(N . C ) * N + C
        reflectDirect = ray.rayDirect - 2 * normal * np.dot(ray.rayDirect, normal)
        reflectDirect = reflectDirect / np.linalg.norm(reflectDirect)
        reFlectRay = Ray(interSectionPoint + reflectDirect *  0.000001 , reflectDirect, ray.depth + 1 )
        Rr,Gr,Br = drawRayTrace(reFlectRay, ambientInput, background, listSphere, listLight, True)
        Rr = Rr * kr
        Gr = Gr * kr
        Br = Br * kr
        outReflect = np.array([Rr,Gr,Br])

        # add lighting diffuse
        color = color + outReflect

    
    R = min(1.0, max(0.0, color[0]))
    G = min(1.0, max(0.0, color[1]))
    B = min(1.0, max(0.0, color[2]))
    

    return R,G,B

    

def preComputeSphere(listSphere):
    computedSpheres = []
    for sphere in listSphere:
        name = sphere[0]
        position = np.array([float(sphere[1]),float(sphere[2]),float(sphere[3])])
        scale = np.array([float(sphere[4]),float(sphere[5]),float(sphere[6])])
        color = np.array([float(sphere[7]),float(sphere[8]),float(sphere[9])])
        ka = float(sphere[10])
        kd = float(sphere[11])
        ks = float(sphere[12])
        kr = float(sphere[13])
        n = float(sphere[14])
        mainSphere = Sphere(name, position, scale, color, ka, kd, ks, kr, n)
        computedSpheres.append(mainSphere)
    return computedSpheres


# main starting function --------------------------------------
if __name__ == "__main__":

    # variable  -------------------
    near = 0
    left = 0
    right = 0 
    bottom = 0
    top = 0
    # x-y
    res = None
    # list of sphere that is in the scene
    listSphere = None
    # list of lights that is in the scene
    listLight = None
    # r-g-b
    back = None
    #  r-g-b
    ambient = None
    # string
    output = None
    
    starttime = time.time_ns()
    # reading content of file
    # res = width/row = 0 --- height/col = 1
    near, left, right, bottom, top, res, listSphere, listLight, back, ambient, output = readFile(sys.argv[1])    

    listSphere = preComputeSphere(listSphere)

    # main render

    # image parameter
    width = int(res[0])
    height = int(res[1])
    pixel = np.zeros(height*width*3)

   
    # loop throught height and width of pixels
    k = 0
    for r in range(height):
        for c in range(width):
            
            if c == 0 and r % 10 == 0:
                    print(f"Row {r}/{height}")

            # initialize the ray from eye through pixel
            # main ray
            ray = Ray(np.array([0,0,0]))
            ray.fromPixel(r,c,int(near),int(left),int(right),int(bottom),int(top),height,width)
            # color variable for drawing to the screen
            # this is where the color will be printed
            # color = (i+j) * scale
            R,G,B = drawRayTrace(ray, ambient, back, listSphere, listLight, False)
            R = int(min(255,R * 255))
            G = int(min(255,G * 255))
            B = int(min(255,B * 255))

            # put the color into the pixel array
            # the pixel hold color in each pixel
            # k is for the R,G,B
            pixel[k] = R
            pixel[k+1] = G
            pixel[k+2] = B
            # iterate to the next pixel
            k = k + 3

    # save image into PPM (P6)
    fileName = output
    saveImageP6(width,height,fileName,pixel)
    endtime = time.time_ns()
    print(f"Second: {(endtime-starttime)/1000000000}")