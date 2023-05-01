import pexpect
from naoqi import ALProxy
import time
import os
from subprocess import call

# Establecemos la dirección IP y el puerto para la conexión al robot

robot_IP = '192.168.31.23'
robot_PORT = 9559

lectura = True

def grabar(record, leds):
    # ----------> Conexion <----------
    record = ALProxy("ALAudioRecorder", robot_IP, robot_PORT)

    # ----------> Grabacion <----------
    print 'Robot grabando audio...'

    # Dirección donde se guardará el archivo de audio
    record_path = '/home/nao/miniconda3/envs/Robot/lib/expect5.45/grabacion.wav'
    # Llamamos al grupo de leds de los ojos para que se coloquen de color verde
    leds.fadeRGB('Ojos', 'green', 0.1)
    # Iniciamos la grabación con todos los microfonos activados [1, 1, 1, 1]
    record.startMicrophonesRecording(record_path, "wav", 48000, [
                                     1, 1, 1, 1])  # (2back, 2front)
    # Se activan los microfonos con una espera de 4 segundos, por lo que los audios durarán 4 segundos
    time.sleep(4)
    # Finalizamos la grabación parando los microfonos
    record.stopMicrophonesRecording()
    # Colocamos el color de los leds en los ojos a blanco
    leds.fadeRGB('Ojos', 'white', 0.1)
    
    print 'Grabacion terminada'

    return

def Deteccion(speech, memory, record, leds):
    vocabulary = ["peper"]

    # ----------> Inicializacion <-----------

    # Se realiza una configuración inicial a los parámetros del robot
    speech.pause(True)

    speech.setAudioExpression(False)  # BIP
    speech.setVisualExpression(False)

    speech.removeAllContext()
    speech.deleteAllContexts()

    # Se desactiva la detección en medio de la oración
    speech.setVocabulary(vocabulary, False)

    # Se subscribe a la información obtenida en speech, "Test_ASR" 
    speech.subscribe("Test_ASR")
    speech.pause(False)

    # ----------> Reconocimiento <-----------
    print('')
    print('Detectando audio del entorno')

    # ----------> Escucha activa <-----------

    # El robot estará en un bucle infinito hasta escuchar a alguien
    while True:
        # Cuando se escuche el audio la memoria tendrá un estado de detectado
        if memory.getData("ALSpeechRecognition/Status") == "SpeechDetected":
            # Se imprime un mensaje y se sale del bucle con break
            print("Pepper detecto a alguien hablando ...")

            break

    # Fuera del break se llama a la función grabar()
    grabar(record, leds)

    return

if __name__ == "__main__":

    # ----------> Conexion <----------

    # Se inicializa la conexión para el acceso a instancias del robot
    speech = ALProxy("ALSpeechRecognition", robot_IP, robot_PORT)
    memory = ALProxy("ALMemory", robot_IP, robot_PORT)
    record = ALProxy("ALAudioRecorder", robot_IP, robot_PORT)

    # Se inicializa los servicios
    speech_service = ALProxy("ALTextToSpeech", robot_IP, robot_PORT)
    posture_service = ALProxy("ALRobotPosture", robot_IP, robot_PORT)
    motion_service = ALProxy("ALMotion", robot_IP, robot_PORT)

    # Se crea la conexión a los leds del robot
    leds = ALProxy("ALLeds", robot_IP, robot_PORT)

    # Se crea distintos grupos, uno para el ojo derecho, otro para el ojo izquierdo y uno que use ambos
    leds.createGroup("OjoD", ['RightFaceLed1', 'RightFaceLed2', 'RightFaceLed3',
                     'RightFaceLed4', 'RightFaceLed5', 'RightFaceLed6', 'RightFaceLed7', 'RightFaceLed8'])
    leds.createGroup("OjoI",  ['LeftFaceLed1', 'LeftFaceLed2', 'LeftFaceLed3',
                     'LeftFaceLed4', 'LeftFaceLed5', 'LeftFaceLed6', 'LeftFaceLed7', 'LeftFaceLed8'])
    leds.createGroup("Ojos", ["OjoD", "OjoI"])

    # Establecemos el idioma con el que trabajará el servicio de audio y establecemos su postura inicial
    speech_service.setLanguage("Spanish")
    posture_service.goToPosture("StandInit", 1)
    time.sleep(0.5)

    # Finalmente, inicializamos la detección personas hablando mediante la siguiente función
    Deteccion(speech, memory, record, leds)