#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import brickpi3 # import the BrickPi3 drivers
import time     # import the time library for the sleep function
import sys
import numpy as np
import cv2
from MapLib import Map2D
import funcionesRobot as fr
from ballFunctions import *
import constantsFile as cf
# tambien se podria utilizar el paquete de threading
from multiprocessing import Process, Value, Lock


MIN_DISTANCE = 4**2
RAD_PERI = 5

class Robot:
    def __init__(self, init_position=[0.0, 0.0, 0.0]):
        """
        Initialize basic robot params. \

        Initialize Motors and Sensors according to the set up in your robot
        """

######## UNCOMMENT and FILL UP all you think is necessary (following the suggested scheme) ########

        # Robot construction parameters
        #self.R = ??
        #self.L = ??
        #self. ...

        ##################################################
        # Motors and sensors setup

        # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
        self.BP = brickpi3.BrickPi3()
        self.BP.reset_all()
        # Configure sensors, for example a touch sensor.
        #self.BP.set_sensor_type(self.BP.PORT_1, self.BP.SENSOR_TYPE.TOUCH)

        # reset encoder B and C (or all the motors you are using)
        self.BP.offset_motor_encoder(self.BP.PORT_B,
            self.BP.get_motor_encoder(self.BP.PORT_B))
        self.BP.offset_motor_encoder(self.BP.PORT_C,
            self.BP.get_motor_encoder(self.BP.PORT_C))
        self.BP.offset_motor_encoder(self.BP.PORT_D,
            self.BP.get_motor_encoder(self.BP.PORT_D))

        self.BP.set_sensor_type(self.BP.PORT_1, self.BP.SENSOR_TYPE.EV3_ULTRASONIC_CM)
        self.BP.set_sensor_type(self.BP.PORT_3, self.BP.SENSOR_TYPE.EV3_GYRO_ABS_DPS)
        self.BP.set_sensor_type(self.BP.PORT_4, self.BP.SENSOR_TYPE.NXT_LIGHT_ON)

        ##################################################
        # odometry shared memory values
        self.x = Value('d',0.0)
        self.y = Value('d',0.0)
        self.xGoal = Value('d',0.0)
        self.thGoal = Value('d',0.0)
        self.yGoal = Value('d',0.0)
        self.thIni = Value('d',0.0)
        self.th = Value('d',0.0)
        self.v = Value('d',0.0)
        self.w = Value('d',0.0)
        self.vReal = Value('d',0.0)
        self.wReal = Value('d',0.0)
        self.finished = Value('b',1) # boolean to show if odometry updates are finished
        self.xPlot = 0
        self.yPlot = 0

        #Valores adicionales afectados por el mutex
        self.distanceSqrOld = 0
        self.gradiOLD = 0
        self.graddOLD = 0
        self.filename = 1
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.camW = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.camH = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.oldFetchV = cf.MAX_V
        self.factor = 1
        self.passedPeri = False
        self.currentCell = (0,0)
        print(self.camW, self.camH)
        # self.thOLD = Value('d',0.0)
        
        # if we want to block several instructions to be run together, we may want to use an explicit Lock
        self.lock_odometry = Lock()

        # odometry update period --> UPDATE value!
        self.P = cf.TIEMPO_MUESTREO

        self.L = cf.ANCHURA_EJES	
        self.radio = cf.RADIO_RUEDA

        #trabajo Vars
        self.SlaloneDcha = False
        self.startPosInMap = (0,0)
        self.salidaDcha = (0,0)
        self.salidaIzq = (0,0)
        self.anguloGirar = 1

    def getLight(self):
        value = self.BP.get_sensor(self.BP.PORT_4)
        return value
    
    def getSonar(self):
        return 10*self.BP.get_sensor(self.BP.PORT_1)

    def cargarMapa(self, mapFile):
        self.myMap = Map2D(mapFile)
    
    def findPath(self, x_ini, y_ini, x_goal, y_goal):
        self.myMap.findPath(x_ini, y_ini, x_goal, y_goal)

    def setSpeed(self, v,w):
        self.lock_odometry.acquire()
        self.v = v
        self.w = w
        self.lock_odometry.release()
        #print("setting speed to %.2f %.2f" % (v, w))

        # compute the speed that should be set in each motor ...

        speedDPS_left = fr.radTOgrad((v-self.L*w/2)/self.radio)
        speedDPS_right = fr.radTOgrad((v+self.L*w/2)/self.radio)
        #print("TREMENDA SPID:", speedDPS_left, speedDPS_right)
        #print(f"TREMENDA SPID: {speedDPS_left} {speedDPS_right}")
        self.BP.set_motor_dps(self.BP.PORT_C, speedDPS_left)
        self.BP.set_motor_dps(self.BP.PORT_B, speedDPS_right)

    def stop(self):
        self.lock_odometry.acquire()
        self.v = 0
        self.w = 0
        self.lock_odometry.release()
        #print("setting speed to %.2f %.2f" % (0, 0))

        #print("TREMENDA SPID:", 0, 0)
        self.BP.set_motor_dps(self.BP.PORT_C+self.BP.PORT_B, 0)

    # DONE
    def readSpeed(self):
        self.lock_odometry.acquire()
        v = self.v.value
        w =self.w.value
        self.lock_odometry.release()
        return v,w

    # DONE
    def readOdometry(self):
        self.lock_odometry.acquire()
        x = self.x.value
        y =self.y.value
        th = self.th.value
        self.lock_odometry.release()
        return x, y, th

    # DONE
    def startOdometry(self,thIni):
        """ This starts a new process/thread that will be updating the odometry periodically """
        if cf.LOGS:
            with open('logs.txt', 'w') as f:
                f.write('')
        self.finished.value = False
        thIni = fr.normalize_angle(fr.gradTOrad(thIni))
        self.thIni.value = thIni
        self.th.value = thIni
        print(self.thIni.value)
        

        print("Starting sonar...")
        encendido = False
        while not encendido:
            try:
                value = self.BP.get_sensor(self.BP.PORT_1)
                encendido = True
            except brickpi3.SensorError as error:
                encendido = False
            time.sleep(0.02)
        print("Sonar started")
        print("Starting gyro...")
        encendido = False
        while not encendido:
            try:
                value = self.BP.get_sensor(self.BP.PORT_3)
                encendido = True
            except brickpi3.SensorError as error:
                encendido = False
            
            time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.
        print("Gyro started")

        
        self.p = Process(target=self.updateOdometry, args=()) #additional_params?))
        self.p.start()
        print("PID: ", self.p.pid)
        print("Battery voltage : ", 100*(self.BP.get_voltage_battery()-7.8)/(12-7.8),"%" )

    def readGyro(self):
        # Obtener los valores de aceleración del sensor
        acc = self.BP.get_sensor(self.BP.PORT_3)
        acc[0] = fr.normalize_angle(fr.gradTOrad(-acc[0])+self.thIni.value)
        return acc
    
    # DONE
    # You may want to pass additional shared variables besides the odometry values and stop flag
    def updateOdometry(self):

        while not self.finished.value:
            # current processor time in a floating point value, in seconds
            tIni = time.clock()

            # compute updates

            ######## UPDATE FROM HERE with your code (following the suggested scheme) ########
            #sys.stdout.write("Stopping odometry ... X=  %.2f, \
             #   Y=  %.2f, th=  %.2f \n" %(self.x.value, self.y.value, self.th.value))

            #print("Dummy update of odometry ...., X=  %.2f" %(self.x.value) )

            # update odometry uses values that require mutex
            # (they are declared as value, so lock is implicitly done for atomic operations, BUT =+ is NOT atomic)
            
            try:
                # Each of the following BP.get_motor_encoder functions returns the encoder value
                # (what we want to store).
                #sys.stdout.write("Reading encoder values .... \n")
                [gradi, gradd] = [self.BP.get_motor_encoder(self.BP.PORT_C),
                    self.BP.get_motor_encoder(self.BP.PORT_B)]
                #wi -> puerto C ; wd-> puerto B
                wi = fr.gradTOrad(gradi - self.gradiOLD)/self.P
                wd = fr.gradTOrad(gradd - self.graddOLD)/self.P
                #print(wi)
                self.gradiOLD = gradi
                self.graddOLD = gradd
                self.lock_odometry.acquire()
                self.vReal.value = self.radio*(wd+wi)/2
                thW = self.readGyro()
                self.wReal.value = fr.gradTOrad(-thW[1])
                wAntes = self.radio*(wd-wi)/self.L
                #clears the file
                #logs in a file the values of the odometry
                if cf.LOGS:
                    with open('logs.txt', 'a') as f:
                        f.write('x: '+str(self.xPlot) + ' y: ' + str(self.yPlot) + ' theta: ' + str(self.th.value) + ' v: ' + str(self.vReal.value) + ' w: ' + str(self.wReal.value) + '\n')
                self.lock_odometry.release()
                #sys.stdout.write('x: '+str(self.xPlot) + ' y: ' + str(self.yPlot) + ' theta: ' + str(self.th.value) + ' v: ' + str(self.vReal.value) + ' w: ' + str(self.wReal.value) + '\n')
            except IOError as error:
                #print(error)
                sys.stdout.write(error)

            vc = [self.vReal.value, self.wReal.value]
            self.lock_odometry.acquire()
            xPos = np.array([self.x.value, self.y.value, self.th.value])
            xPosPlot = np.array([self.xPlot, self.yPlot, self.th.value])
            newPos = fr.simubot(vc, xPos, self.P)
            newPosPlot = fr.simubot(vc, xPosPlot, self.P)
            # to "lock" a whole set of operations, we can use a "mutex"
            
            # self.xOLD.value = self.x.value
            # self.yOLD.value = self.y.value
            # self.thOLD.value = self.th.value
            self.x.value = newPos[0]
            self.y.value = newPos[1]
            self.xPlot = newPosPlot[0]
            self.yPlot = newPosPlot[1]
            # self.th.value = newPos[2]
            self.th.value = thW[0]
            #print("thhhhh",self.th.value)
            self.lock_odometry.release()


            #sys.stdout.write("Encoder (%s) increased (in degrees) B: %6d  C: %6d " %
            #        (type(encoder1), encoder1, encoder2))  1,


            # save LOG
            # Need to decide when to store a log with the updated odometry ...

            ######## UPDATE UNTIL HERE with your code ########


            tEnd = time.clock()
            time.sleep(self.P - (tEnd-tIni))

        #print("Stopping odometry ... X= %d" %(self.x.value))
        sys.stdout.write("Stopping odometry ... X=  %.2f, \
                Y=  %.2f, th=  %.2f \n" %(self.xPlot, self.yPlot, self.th.value))

    def setPosGoals(self,xd,yd,v,w):
        self.lock_odometry.acquire()
        self.xGoal.value = xd
        self.passedPeri = False
        self.yGoal.value = yd
        x = self.x.value
        y = self.y.value
        self.lock_odometry.release()
        self.distanceSqrOld = (x-xd)*(x-xd)+(y-yd)*(y-yd)
        self.setSpeed(v, w)
        print("setting goals to %.2f %.2f" % (xd, yd))

    def setThetaGoal(self,th):
        self.lock_odometry.acquire()
        self.thGoal.value = th
        print("setting thgoal to", th)
        self.lock_odometry.release()

    def checkTheta(self):
        self.lock_odometry.acquire()
        th = self.th.value
        thg = self.thGoal.value
        # print("th:", th)
        # print("thg:", thg)
        self.lock_odometry.release()
        if abs(th-thg)<0.08:
            self.stop()
            return 1
        factor = -1
        if self.w>0: factor=1
        self.setSpeed(0,factor*min(cf.W_MAX,np.pi/8+cf.W_MAX*abs(th-thg)))
        return 0

    def checkObstucalo(self):
        dist = self.getSonar()
        return dist < 300

    def checkSonar(self,dist):
        sonarDist = self.getSonar()
        if abs(sonarDist-dist-cf.CM_TO_SONAR)>1:
            factor = -1
            if sonarDist-dist>0:
                factor=1
            vel = min(cf.V_CARRERA,75+abs(sonarDist-dist))      
            self.setSpeed(vel*factor,0)
            return 0
        self.stop()
        return 1
    
    def checkSonarBarrido(self,dist):
        sonarDist = self.getSonar()
        print(dist, sonarDist)
        if abs(sonarDist-dist) > 0:
            return 0
        return 1

    def checkFinish(self):
        self.lock_odometry.acquire()
        xG = self.xGoal.value/10
        yG = self.yGoal.value/10
        x = self.x.value/10
        y = self.y.value/10
        print("xG:", xG, "yG:", yG)
        print("x", x, "y", y)
        distanceSqrOld = self.distanceSqrOld
        self.lock_odometry.release()
        distanceSqr = (x-xG)*(x-xG)+(y-yG)*(y-yG)
        if distanceSqr < MIN_DISTANCE:  # esta en rango
            print("llegue")
            self.stop()
            return 1
        elif distanceSqr > distanceSqrOld+5:
            if self.passedPeri:    # se aleja
                print("Se aleja",distanceSqr,distanceSqrOld)
                self.stop()
                return -1
            else: 
                print("aleja pero ok")
                self.lock_odometry.acquire()
                self.distanceSqrOld = distanceSqr
                self.lock_odometry.release()
                return 0
        #print("CONTINUAAAAAAA")
        #print(distanceSqr)
        #print("OLDDDDDDDDDDDD")
        #print(distanceSqrOld)
        print("acerca")
        self.lock_odometry.acquire()
        self.distanceSqrOld = distanceSqr
        self.passedPeri = True
        self.lock_odometry.release()
        return 0
    
    def checkDiam(self, estado = cf.Estados.CHECKDIAMNOESTADO):
        #Hacer la foto img = hacer foto
        ret, img_BGR = self.cap.read()
        if not ret:
            print ("can't recieve")
            return -1
        #print(estado)
        w = cf.W_SEGUIR_PELOTA
        kp = getKp(img_BGR)
        if estado == cf.Estados.COGER_PELOTA:
            for i in range(0,1):
                ret, img_BGRAux = self.cap.read()
                kpAux = getKp(img_BGRAux)
                if kpAux.size > kp.size:
                    kp = kpAux
                w = cf.W_COGER_PELOTA
        diamBall = kp.size
        print("Diam: ",diamBall)
        if diamBall == -1:
            return -1

        #print("vidHOY/"+str(self.filename)+".png")
        #cv2.imwrite("vidHOY/"+str(self.filename)+".png", img_BGR)
        #self.filename = self.filename+1
        if estado != cf.Estados.RECULAR:
            v = max(min(cf.MAX_V,cf.K / diamBall, self.oldFetchV+5),0)
            self.oldFetchV = v
            print(kp.pt[0], kp.pt[1])
            if kp.pt[0] > (self.camW/2 -30) and kp.pt[0] < (self.camW/2 +30):
                w = 0
            elif kp.pt[0] < self.camW/2:
                w = -1*w #GIRAR A LA DERECHA
                self.factor = -1
            else:
                self.factor = 1
            #print("V: ",v)
            #print("W: ",w)
            self.setSpeed(v,w)
        if diamBall < cf.stoppingDiameter1:
            return 0 # Continue til stop1
        elif diamBall < cf.stoppingDiameter2:
            return 1 # Lower forklift
        elif diamBall < cf.stoppingDiameter3:
            return 2 # Colision danger
        else:
            return 3 # Parar

    def checkThetaBall(self):
        #Hacer la foto img = hacer foto
        ret, img_BGR = self.cap.read()
        if not ret:
            print ("can't recieve")
            return -1
        #print(estado)
        kp = getKp(img_BGR)
        for i in range(0,2):
            ret, img_BGRAux = self.cap.read()
            kpAux = getKp(img_BGRAux)
            if kpAux.size > kp.size:
                kp = kpAux
        diamBall = kp.size
        print("Diam: ",diamBall)
        if diamBall == -1:
            return -1

        print(kp.pt[0], kp.pt[1])
        if kp.pt[0] > (self.camW/2 -cf.LIM_THETA) and kp.pt[0] < (self.camW/2 +cf.LIM_THETA):
            return 1
        elif kp.pt[0] < self.camW/2:
            self.setSpeed(0,-cf.W_THETABALL)
            self.factor = -1
        else:
            self.setSpeed(0,cf.W_THETABALL)
            self.factor = 1
        return 0

    def resetForklift(self):
        self.BP.set_motor_dps(self.BP.PORT_D, 150)
        time.sleep(2)
        self.BP.set_motor_dps(self.BP.PORT_D, 0)
        self.BP.offset_motor_encoder(self.BP.PORT_D,
        self.BP.get_motor_encoder(self.BP.PORT_D))

    # Stop the odometry thread.
    def stopOdometry(self):
        self.finished.value = True
        self.cap.release()
        self.BP.reset_all()

    def liftForklift(self):
        #while the motor is not at the desired position, keep moving
        self.BP.set_motor_dps(self.BP.PORT_D, cf.forkliftV)
        print(self.BP.get_motor_encoder(self.BP.PORT_D))
        while self.BP.get_motor_encoder(self.BP.PORT_D) < cf.LIMITE_SUPERIOR_FORKLIFT:
            print(self.BP.get_motor_encoder(self.BP.PORT_D))
            time.sleep(0.1)
        self.BP.set_motor_dps(self.BP.PORT_D, 0)

    def lowerForklift(self):
        #while the motor is not at the desired position, keep moving
        self.BP.set_motor_dps(self.BP.PORT_D, -cf.forkliftV)
        print(self.BP.get_motor_encoder(self.BP.PORT_D))
        while self.BP.get_motor_encoder(self.BP.PORT_D) > cf.LIMITE_INFERIOR_FORKLIFT:
            print(self.BP.get_motor_encoder(self.BP.PORT_D))
            time.sleep(0.1)
        self.BP.set_motor_dps(self.BP.PORT_D, 0)

    def ForkliftToPos(self, deg):
        motosPos = self.BP.get_motor_encoder(self.BP.PORT_D)
        if motosPos > deg:
            self.BP.set_motor_dps(self.BP.PORT_D, -cf.forkliftV)
            while self.BP.get_motor_encoder(self.BP.PORT_D) > deg:
                print(self.BP.get_motor_encoder(self.BP.PORT_D))
                time.sleep(0.1)
            self.BP.set_motor_dps(self.BP.PORT_D, 0)
        else:
            self.BP.set_motor_dps(self.BP.PORT_D, cf.forkliftV)
            while self.BP.get_motor_encoder(self.BP.PORT_D) < deg:
                print(self.BP.get_motor_encoder(self.BP.PORT_D))
                time.sleep(0.1)
            self.BP.set_motor_dps(self.BP.PORT_D, 0)

    