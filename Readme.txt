Building a Ray Tracer for assignment 3:

Import needed to run
- sys, os, numpy, math, time

Compiling
- python RayTracer.py <testcase.txt>

Runtime
- Atmost 90 second due to the amount of sphere
- Average is 30 - 50 second for most test cases
- will indicate what row is completed and time completed

OUTPUT
- PPM (P6), 

STEP TO BUILDING A RAY TRACER FOR ASSIGNMENT 3:

- READ INPUT FILE - COMPLETED
    - input format - OUTPUT <name>

- THE RAY TRACER
    - Setting up ray camera - COMPLETED
    - Draw RGB color to pixel - COMPLETED
    - Draw a spheres
        - Sphere intersection - COMPLETED
        - Scale sphere
            - inverse transform - COMPLETED
            - inverse normal - COMPLETED
        - Near plane - COMPELTED
            - Check if sphere intersection then get the max or min

- ENCODED OUTPUT PPM FORMAT - COMPELTED
    - choose between P6 or P3 - P6


TEST COMPLETED
- testAmbient.txt - This built the scene, scale, inverse, and camera
- testBackground.txt - This built the background - longest renders due to sphere
- testBehind.txt - This test if t value is negative. If t is negative do not draw 
- testDiffuse.txt - This test the diffuse. Use normal from sphere 
- testSpecular.txt - using phong lighting
- testParsing.txt - Can parse weird input
- testShadow.txt - shadow working
- testSample.txt - ADS working
- testReflection.txt - reflection works now
- testIntersection.txt - single pixel working - need testing
- testImgPlane.txt - floating point problem
- testIllum.txt - normal problem and floating point problem

INCOMPLETE






