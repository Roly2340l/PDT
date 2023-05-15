# Librerias para la red neuronal
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from subprocess import call

from sklearn.preprocessing import StandardScaler

# Librerias importantes
import librosa
import librosa.display

# Librerias extras
import wave
import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
from pydub.utils import which
import numpy as np
import cv2
import matplotlib.pyplot as plt

# Clasi
clasificador = load_model("modelo_final.h5")

# Libreriras de deteccion
from inotify_simple import INotify, flags
import os

inotify = INotify()

def detectar_silencios(sound, silence_threshold=-50.0, chunk_size=10):
    trim_ms = 0
    assert chunk_size > 0
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size
    return trim_ms

def limpiar_audio():
    AudioSegment.converter = which("ffmpeg")

    Direc = '/home/jose/TOFO/audio/grabacion_encontrado.wav' #Grabacion de 3 segundos

    sound = AudioSegment.from_file(Direc)
    
    sound = sound + 10
    start_trim = detectar_silencios(sound)
    end_trim = detectar_silencios(sound.reverse())

    duration = len(sound)
    trimmed_sound = sound[start_trim:duration-end_trim]

    trimmed_sound.export("grabacion_limpio.wav", format='wav')

def extract_features(data, sample_rate):
    # ZCR
    result = np.array([])
    zcr = np.mean(librosa.feature.zero_crossing_rate(y=data).T, axis=0)
    result = np.hstack((result, zcr))

    # Chroma_stft
    stft = np.abs(librosa.stft(data))
    chroma_stft = np.mean(librosa.feature.chroma_stft(
        S=stft, sr=sample_rate).T, axis=0)
    result = np.hstack((result, chroma_stft))

    # MFCC
    mfcc = np.mean(librosa.feature.mfcc(y=data, sr=sample_rate).T, axis=0)
    result = np.hstack((result, mfcc))

    # Root Mean Square Value
    rms = np.mean(librosa.feature.rms(y=data).T, axis=0)
    result = np.hstack((result, rms))

    # MelSpectogram
    mel = np.mean(librosa.feature.melspectrogram(
        y=data, sr=sample_rate).T, axis=0)
    result = np.hstack((result, mel))

    return result

def get_features(path):
    data, sample_rate = librosa.load(path)

    res1 = extract_features(data, sample_rate)
    result = np.array(res1)

    return result

def graph_spectrogram(wav_file, JA = "X"):
    rate, data = wavfile.read(wav_file)
    fig, ax = plt.subplots(1)
    fig.set_size_inches(0.64, 0.64)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis('off')
    try:
        pxx, freqs, bins, im = ax.specgram(
            x=data, Fs=rate, cmap='gray_r', noverlap=384, NFFT=512)
    except:
        pxx, freqs, bins, im = ax.specgram(
            x=(data[:, 0] + data[:, 1])/2, Fs=rate, cmap='gray_r', noverlap=384, NFFT=512)
    ax.axis('off')
    fig.savefig(JA, dpi='figure')
    plt.close(fig=fig)

def revisar_audio():
    AudioSegment.converter = which("ffmpeg")

    Direc = '/home/jose/TOFO/audio/grabacion_encontrado.wav'

    sound = AudioSegment.from_file(Direc)
    
    if(sound.dBFS > -45.0):
        return False
        
    else:
        return True

# -----> Detector de eventos <-------
watch_flags = flags.CREATE # Deteccion de evento de modificacion en carpeta
wd = inotify.add_watch('/home/jose/TOFO/audio', watch_flags) # Carpeta de deteccion

# ----------> Principal <---------- 
while(True):
    # Bucle de espera de deteccion de respuesta
    # no se inicializa el detector hasta que llegue el audio a la carpeta

    for event in inotify.read(): # Espera de evento
        os.chdir('/home/jose/TOFO/cosas')
        print(event)
        for flag in flags.from_mask(event.mask):  # Accion por evento detectado
            print('    ' + str(flag))
            if True:
                print ('Archivo agregado')
                
		# Inicio de deteccion de emociones
                if revisar_audio(): 
                    print('Habla no detectada')
                    respuesta = 'Nada'
                    os.chdir('/home/jose/TOFO/resultados')
                    os.system('echo ' + respuesta + ' > test.txt') # Guarda respuesta en test.txt
                    os.chdir('/home/jose/TOFO/audio')
                    break  # No guarda ni ejecuta posterior

                limpiar_audio()
                features = get_features("grabacion_limpio.wav")
                graph_spectrogram("grabacion_limpio.wav")

                # CARACTERISTICAS ESPECTRALES
                features = np.expand_dims(features, axis=0)
                scaler = StandardScaler()
                features_espectral = scaler.fit_transform(features)

                # CARACTERISTICAS DE ESPECTROGRAMA
                data = []

                image = cv2.imread('X.png', cv2.IMREAD_GRAYSCALE)
                data.append(image)

                features_spectrogram = np.array(data, dtype="float") / 255.0

                # PREDICCION

                result = clasificador.predict({"img_input": features_spectrogram, "data_input": features_espectral})
                print(result)
                print()
                respuesta = np.argmax(result)
                os.chdir('/home/jose/Descargas')

		# Respuesta por emocion detectada
                if respuesta == 0:
                    respuesta = 'Neutro'
                elif respuesta == 1:
                    respuesta = 'Disgusto'
                elif respuesta == 2:
                    respuesta = 'Felicidad'
                elif respuesta == 3:
                    respuesta = 'Ira'
                elif respuesta == 4:
                    respuesta = 'Miedo'
                elif respuesta == 5:
                    respuesta = 'Sorpresa'
                elif respuesta == 6:
                    respuesta = 'Tristeza'

		# Guardado de respuesta en archivo text.txt
                os.chdir('/home/jose/TOFO/resultados') # posible cambio al principio
                os.system('echo ' + respuesta + ' > test.txt')
                os.chdir('/home/jose/TOFO/audio')

                print("Emocion detectada: ", respuesta)
