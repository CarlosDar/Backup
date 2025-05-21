# Control de Frecuencímetro CNT-91

Este proyecto contiene funciones para controlar y realizar mediciones con el frecuencímetro CNT-91.

## Funcionalidades

- Configuración de mediciones estadísticas
- Lectura de estadísticas (media, mínimo, máximo, pico a pico, desviación estándar, ADEV)
- Control de parámetros como tiempo de apertura, acoplamiento, impedancia, etc.

## Requisitos

- Python 3.x
- Conexión GPIB al instrumento CNT-91

## Uso

```python
from FUNCIONESNUEVAS import CNT_frequenciometro

# Inicializar el frecuencímetro
cnt = CNT_frequenciometro()

# Configurar medición estadística
cnt.configurar_medicion_estadistica(
    tiempo_apertura=1.0,
    acoplamiento='DC',
    impedancia='50',
    atenuador='10',
    filtro_analogico=True,
    filtro_digital=True,
    freq_filtro_digital=1000,
    nivel_auto=False,
    nivel_disparo=0.3,
    medicion_continua=True,
    numero_muestras=100
)

# Leer estadísticas
resultados = cnt.leer_estadisticas(tiempo_apertura=1.0, numero_muestras=100)
print(resultados)
``` 