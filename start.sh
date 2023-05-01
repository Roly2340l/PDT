#!/bin/bash

# Ruta al archivo conda.sh
CONDA_SCRIPT="/home/nao/miniconda3/etc/profile.d/conda.sh"

# Cargar conda.sh, necesario para automatizar el "conda activate" y "conda deactivate"
source "$CONDA_SCRIPT"

# Activar el entorno Robot
conda activate Robot
# Ejecutar el Grabador
python Grabador.py
# Desactivar el entorno
conda deactivate

# Activar el entorno Proceso
conda activate Proceso
# Ejecutar el Procesamiento, que es preprocesamiento y extracción de características
python Procesamiento.py
# Desactivar el entorno
conda deactivate

# Activar el entorno Robot
conda activate Robot
# Llamar a los archivos expect para copiar los archivos numpy del robot al servidor
expect mv_espectral.exp
expect mv_spectrogram.exp
# Desactivar el entorno
conda deactivate