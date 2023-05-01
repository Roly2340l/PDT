# Librerías para la red neuronal
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
import numpy as np
import os
import time
import psutil

# Carga el modelo machine learning
clasificador = load_model("modelo.h5")

# Para que el modelo detecte emoción se tomará en cuenta la modificación del siguiente archivo:
archivo = "features_espectral.npy"

# Se guarda la última hora y fecha de modificación, mediante esto se evaluará si el archivo cambió
# Si el archivo ha cambiado, significa que se detectó y generó un nuevo archivo de audio y que se preproceso y extrajo características
modificacion_actual = os.path.getmtime(archivo)

# Se entra en un bucle infinito
while (True):
    # La siguiente variable tomará la fecha y hora de la última modificación del archivo
    revisador = os.path.getmtime(archivo)

    # En caso de que sea distinto, significa que el archivo fue modificado, por ende, se tiene nuevo archivo de audio y nuevas característics
    if modificacion_actual != revisador:
        # Se carga los archivo numpy que contiene los array con las caracteríßticas espectrales y de espectrograma
        features_spectrogram = np.load('features_spectrogram.npy')
        features_espectral = np.load('features_espectral.npy')

        # Se toma el tiempo antes de ejecutar el modelo
        start_time = time.time()

        # Se llama al clasificador y se realiza la predicción
        result = clasificador.predict({"img_input": features_spectrogram, "data_input": features_espectral})

        # Se toma el tiempo después del la ejecución del modelo
        end_time = time.time()

        # Se toma finalmente el tiempo que llevó la clasificación
        print("Tiempo de clasificación: ", end_time - start_time)

        # El modelo devuelve un array con distintas probabilidades, es decir, un array de tamaño 7, el cual tiene distintas probabilidades
        # Esto determina que emoción cree el modelo que se ha detectado, por ello se obtenedra el argumento máximo
        respuesta = np.argmax(result)

        # Dependiendo del indice que devuelva, se tendrá una emoción distinta:

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

        # Se imprime la emoción detectada
        print("Emoción detectada: ", respuesta)

        # Se actualiza la fecha y hora de moficicación actual para tomar la nueva detectada
        modificacion_actual = os.path.getmtime(archivo)

        # Obtener información sobre el uso de memoria, detalles
        mem = psutil.virtual_memory()

        # Imprimir información sobre la memoria
        print(f"Uso de memoria total: {mem.total}")
        print(f"Uso de memoria disponible: {mem.available}")
        print(f"Porcentaje de uso de memoria: {mem.percent}%")

        # Guardamos la respuesta en un archivo de texto
        archivo = open("emocion.txt", "w")
        archivo.write(respuesta)
        archivo.close()

        # Finalmente, para aplicaciones internas del robot que requiera la respuesta se puede usar el archivo mv_respuesta.exp
        # Este archivo expect envia el archivo .txt al robot