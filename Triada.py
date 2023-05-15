from naoqi import ALProxy
import time
import os

from subprocess import call

from inotify_simple import INotify, flags
inotify = INotify()

import poses as p

robot_IP = '192.168.31.23'
robot_PORT = 9559


lectura = True

def grabar(record,leds):
	# ----------> Conexion <----------
	record = ALProxy("ALAudioRecorder", robot_IP, robot_PORT)

	# ----------> Grabacion <----------
	print 'Robot grabando audio...'
	record_path = '/tmp/test.wav'
	leds.fadeRGB('Ojos','green',0.1)
	record.startMicrophonesRecording(record_path,"wav",48000,[1,1,1,1])#(2back, 2front)
	time.sleep(3)
	record.stopMicrophonesRecording()
	leds.fadeRGB('Ojos','white',0.1)
	print 'Grabacion terminada'
	
	return 
    

def Pepper_awake(speech,memory,record,leds):
    vocabulary = ["peper"]        

    # ----------> Inicializacion <-----------
    speech.pause(True)

    speech.setAudioExpression(False)  # BIP
    speech.setVisualExpression(False)

    speech.removeAllContext()
    speech.deleteAllContexts()

    speech.setVocabulary(vocabulary,False) # 'True' par detectar en medio de oracion

    speech.subscribe("Test_ASR")
    speech.pause(False)

    # ----------> Reconocimiento <-----------
    print('')
    print('Detectando audio del entorno')    

    while True:
        if memory.getData("ALSpeechRecognition/Status") == "SpeechDetected":
   
            print ("Pepper detecto a alguien hablando ...")

            break

    grabar(record,leds)

    return 

if __name__ == "__main__":

    # ----------> Conexion <----------
    speech = ALProxy("ALSpeechRecognition", robot_IP, robot_PORT)
    memory = ALProxy("ALMemory", robot_IP, robot_PORT)
    record = ALProxy("ALAudioRecorder", robot_IP, robot_PORT)

    speech_service = ALProxy("ALTextToSpeech", robot_IP, robot_PORT)
    posture_service = ALProxy("ALRobotPosture", robot_IP, robot_PORT)
    motion_service = ALProxy("ALMotion", robot_IP, robot_PORT)

    leds =  ALProxy("ALLeds", robot_IP, robot_PORT)

	# Creacion de grupos de LED para su manejo
    leds.createGroup("OjoD", ['RightFaceLed1','RightFaceLed2','RightFaceLed3','RightFaceLed4','RightFaceLed5','RightFaceLed6','RightFaceLed7','RightFaceLed8'])
    leds.createGroup("OjoI",  ['LeftFaceLed1', 'LeftFaceLed2', 'LeftFaceLed3','LeftFaceLed4', 'LeftFaceLed5', 'LeftFaceLed6','LeftFaceLed7', 'LeftFaceLed8'])
    leds.createGroup("Ojos", ["OjoD", "OjoI"]) # 'Ojos' para manejo de todos los LEDS de los ojos del robot

    speech_service.setLanguage("Spanish")    
    posture_service.goToPosture("StandInit", 1)
    time.sleep(0.5)

    # -----> Inicializacion de algoritmo <-------
    call('./iniciar_algo.sh')    
    
    # -----> Detector de eventos <-------
    watch_flags = flags.MODIFY # Deteccion de evento de modificacion en carpeta
    wd = inotify.add_watch('/home/jose/TOFO/resultados', watch_flags) #Carpeta de deteccion

    # ----------> Principal <----------
    while(True):
        Pepper_awake(speech,memory,record,leds)
        
        os.system('touch /home/jose/TOFO/tiempo/tmp.txt') #Inicio de medicion de tiempo
        
        call('./Descargar_archivo.sh') # Descarga de audio grabado

        call('./manejo_archivo.sh') # Reconocimiento de persona hablando

        print('Archivo copiado')
        
	# Bucle de espera de deteccion de respuesta
        for event in inotify.read(): # Espera de evento
            for flag in flags.from_mask(event.mask): # Accion por evento detectado
                archivo = open('/home/jose/TOFO/resultados/test.txt')
                respuesta = archivo.readline(3) # Guardado de respuesta del algoritmo
                archivo.close()

        print('Se detecto: '+ respuesta)

	# Accion por emocion detectada
        if respuesta == 'Ira':
            p.pose_ira(speech_service, motion_service,leds)
        elif respuesta == 'Tri':
            p.pose_tristeza(speech_service, motion_service,leds)
        elif respuesta == 'Sor':
            p.pose_sorpresa(speech_service, motion_service,leds)
        elif respuesta == 'Dis':
            p.pose_disgusto(speech_service, motion_service,leds)
        elif respuesta == 'Mie':
            p.pose_miedo(speech_service, motion_service,leds)
        elif respuesta == 'Fel':
            p.pose_felicidad(speech_service, motion_service,leds)
        else:
            p.pose_neutro(speech_service, motion_service,leds)
        
	# Postura neutral    
        posture_service.goToPosture("StandInit", 1)
        time.sleep(0.5)

	# Inicializacion de 
        os.system('rm /home/jose/TOFO/audio/grabacion_encontrado.wav')
        os.system('rm /home/jose/TOFO/resultados/test.txt')
