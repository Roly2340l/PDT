# PDT

El repositorio cuenta con todos los archivos python necesarios para el funcionamiento del sistema, cada uno de ellos está debidamente comentado para el entendimiento de quien lo requiera. Asimismo, también se requiere archivos expect y bash para la automatización de la transferencia de archivos y ejecucion de programas.

## Funcionamiento:

Se debe contar con el robot Pepper y un servidor.

El servidor contiene los siguientes archivos:
- Clasificador.py
- mv_respuesta.exp

El robot contiene los siguientes archivos:
- Grabador.py
- Proceso.py
- mv_spectrogram.exp
- mv_espectral.exp
- start.sh

Para el funcionamiento continuo entre ambos dispositivos, es decir, robot y servidor, se debe ejecutar lo siguiente:

- Pepper: start.sh
- Servidor: Clasificador.py

Hasta el momento, el robot pepper requiere de llamar al start.sh para realizar una grabación, preprocesamiento, extracción de características y envío de archivos. Para próximas actualización se podría implementar una actualización donde se tenga un funcionamiento continuo o en bucle; no obstante, no se implementó por el motivo de que la ejecución interna en el robot no es eficiente, dado que consume recursos y demora aproximadamente 8 segundos. Lo cual lo descarta para la aplicación de un sistema de reconocimiento de emociones en tiempo real. Por lo tanto, es muy posible que el desarrollo de este proyecto finalice con lo actualmente presentado.

Por otro lado, se adiciona los siguientes archivos que permiten comunicación con los movimientos del robot y el modelo, todo alojado en un servidor:
- Triada.py
- Comunicame.py

Finalmente, los movimientos se presentan como tal de la siguiente manera:
- disgusto.py
- felicidad.py
- ira.py
- miedo.py
- neutral.py
- sorpresa.py
- tristeza.py

Cada una de estas emociones son archivos .py los cuales son llamados de acuerdo a la emoción captada por el modelo, el robot reaccionará en consecuencia.
