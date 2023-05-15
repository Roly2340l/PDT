#if not, type ont terminal
#export PYTHONPATH=$HOME/pynaoqi/pynaoqi-python2.7-2.5.7.1-linux64/lib/python2.7/site-packages:$PYTHONPATH

import qi
import argparse
import sys
import time
import math
import random


def rad(num):
    return num*math.pi/180

def pose(motion_service):

    names  = ["RElbowRoll", "RElbowYaw", "RShoulderPitch", "RShoulderRoll", "RWristYaw","LElbowRoll", "LElbowYaw", "LShoulderPitch", "LShoulderRoll", "LWristYaw","LHand","RHand","HeadPitch","HeadYaw"]#Uso de articulaciones
    angles = [ rad(85.5), rad(72.4), rad(33.3), rad(0), rad(60.6), rad(-55.7), rad(-64), rad(0), rad(5.4), rad(-61.5),0,0,0,rad(-20)]#Definicion de los valores de las articulaciones
    fractionMaxSpeed  = 0.5#Velocidad de la postura (Velocidad del movimiento de las articulaciones)
    motion_service.setAngles(names, angles, fractionMaxSpeed)
    time.sleep(0.2)

def main(session):
    posture_service = session.service("ALRobotPosture")
    motion_service = session.service("ALMotion")

    posture_service.goToPosture("StandInit", 1)#Uso de la pose inicial del robot"predeterminado"
    pose(motion_service)
    posture_service.goToPosture("StandInit", 1)
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.0.172",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)
