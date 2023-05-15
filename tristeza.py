#if not, type ont terminal
#export PYTHONPATH=$HOME/pynaoqi/pynaoqi-python2.7-2.5.7.1-linux64/lib/python2.7/site-packages:$PYTHONPATH

import qi
import argparse
import sys
import time
import math


def rad(num):
    return num*math.pi/180

def pose_tristeza(motion_service):
    names  = ["RElbowRoll", "RElbowYaw", "RShoulderPitch", "RShoulderRoll", "RWristYaw","LElbowRoll", "LElbowYaw", "LShoulderPitch", "LShoulderRoll", "LWristYaw",   "HeadPitch", "HipPitch","LHand", "RHand"]#Uso de articulaciones
    angles = [ rad(24.9), rad(-50.7), rad(41.7), rad(-1.9), rad(90.4), rad(-26.0), rad(50.3), rad(43.2), rad(3.8), rad(-90.5),rad(25.5),rad(-51.2),1,1]#Definicion de los valores de las articulaciones
    fractionMaxSpeed  = 0.5#Velocidad de la postura (Velocidad del movimiento de las articulaciones)
    motion_service.setAngles(names, angles, fractionMaxSpeed)


def main(session):
    posture_service = session.service("ALRobotPosture")
    motion_service = session.service("ALMotion")

    posture_service.goToPosture("StandInit", 1)#Uso de la pose inicial del robot"predeterminado"
    pose_tristeza(motion_service)	
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
