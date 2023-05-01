import sys
import numpy as np
from scipy.io import wavfile
import librosa
import matplotlib.pyplot as plt
from PIL import Image
from pydub import AudioSegment
from pydub.utils import which
from sklearn.preprocessing import StandardScaler

import time

def detectar_silencios(sound, silence_threshold=-50.0, chunk_size=10):
    # Detecta solo silencio y devuelve el punto donde empezó a existir audio "escuchable"
    trim_ms = 0
    assert chunk_size > 0
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size
    return trim_ms
    
def extract_features(data, sample_rate):
    # Llama a todas las funciones de librosa que extraen características, en este caso, 5 características:

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

    # Todas las características son stackeadas de forma horizontal, y se retorna un array numpy

    return result

def get_features(path):
    # Cara los datos del audio, su rate y llama a la extracción de características
    data, sample_rate = librosa.load(path)

    res1 = extract_features(data, sample_rate)

    # Retorna un array numpy
    result = np.array(res1)

    return result

def graph_spectrogram(wav_file, JA = "X"):
    # Se grafica el espectrograma con formato png y tamaño 64x64 píxeles.
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

# --------------> Inicio del preprocesamiento y extracción de características <--------------

for i in range (0, 1):
    # Estas variables de start_time y end_time serviran para obtener tiempos en la ejecución de ciertas lineas de código
    start_time = time.time()

    # Llamamos a la colección ffmpeg para el tratamiento de audio
    AudioSegment.converter = which("ffmpeg")

    # Establecemos la dirección del archivo de audio generado
    Direc = 'grabacion.wav'

    # Obtenemos el audio del archivo
    sound = AudioSegment.from_file(Direc)

    # Realizamos una amplifiación
    sound = sound + 5

    # Llamamos a la detección de silencios, obtenemos el punto de inicio y final para recortar aquellos silencios en los extremos
    start_trim = detectar_silencios(sound)
    end_trim = detectar_silencios(sound.reverse())

    # Extramos el audio solo la parte con audio, aquellos silencios en los extremos se dejarán
    duration = len(sound)
    trimmed_sound = sound[start_trim:duration-end_trim]

    # Si existiese el caso donde todo el audio era silencioso, por lo que el tamaño de trimmed_sound es 0, se sale del for y no se realiza nada más
    if len(trimmed_sound) == 0:
        break
    # Caso contrario, se exporta un audio limpio para empezar a extraer las características
    else:
        trimmed_sound.export("grabacion_limpio.wav", format='wav')

    # Obtenemos el tiempo cuando se finaliza la ejecución de las anteriores líneas
    end_time = time.time()

    # Se imprime el tiempo que tomó estas tareas
    print("Tiempo de preprocesamiento: ", end_time - start_time)

    # Se obtiene un nuevo tiempo de inicio
    start_time = time.time()

    # Se llama a la función de obtención de característas y se guarda en features
    features = get_features("grabacion_limpio.wav")
    # Se llama a la función de graficar espectrograma para generar una imagen 64x64 píxeles
    graph_spectrogram("grabacion_limpio.wav")

    # --------------> CARACTERISTICAS ESPECTRALES <--------------

    # Se modifica las dimensiones y se escala los valores para que puedan entrar al modelo
    features = np.expand_dims(features, axis=0)
    scaler = StandardScaler()
    features_espectral = scaler.fit_transform(features)

    # --------------> CARACTERISTICAS DE ESPECTROGRAMA <--------------

    # Se accede a la imagen creada, se convierte a escala de grises y se añade a una lista
    data = []

    img = Image.open('X.png')
    img_gray = img.convert('L')

    data.append(np.array(img_gray))

    # Se escala los valores de la imagen, la cual es una matriz con valores entre 0 a 255 pixeles, por lo que se escala de 0 a 1
    features_spectrogram = np.array(data, dtype="float") / 255.0

    # Se finaliza obteniendo el tiempo final al ejecutar las anteriores lineas
    end_time = time.time()

    # Se imprime el tiempo que tardó la extracción de características
    print("Tiempo de extracción de características: ", end_time - start_time)

    # Finalmente, se guarda los array que contienen la información de las características, se guarda como archivos .npy
    np.save('features_espectral.npy', features_espectral)
    np.save('features_spectrogram.npy', features_spectrogram)