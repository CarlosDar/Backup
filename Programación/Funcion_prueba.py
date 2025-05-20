# Crear un objeto de la Libreria CNT_9X_pendulum
import CNT_9X_pendulum as CNT
objt_prueba = CNT.CNT_frequenciometro()

# Ver la lista de dispositivos en el GPIB
import pyvisa
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
print("Available VISA resources:", resources)

# ====== NUEVA SECCIÓN: Prueba de la función modificada ======

# Parámetros de la prueba
n_muestras = 5
intervalo_s = 0.2

# Calcular y mostrar el tiempo de espera antes de medir
tiempo_espera = n_muestras * intervalo_s * 1.1

# Conversión a formato horas:minutos:segundos
horas = int(tiempo_espera // 3600)
minutos = int((tiempo_espera % 3600) // 60)
segundos = tiempo_espera % 60

print(f"TIEMPO DE ESPERA ESTIMADO = {tiempo_espera:.2f} segundos "
      f"({horas:02d}:{minutos:02d}:{segundos:05.2f} [hh:mm:ss])")

# Ejecutar la medición
resultados = objt_prueba.medir_n_muestras_equidistantes(n_muestras=n_muestras, intervalo_s=intervalo_s)

# Ajustar los timestamps para restar el inicial
if resultados and isinstance(resultados[0], tuple) and len(resultados[0]) == 2:
    t0 = resultados[0][1]
    resultados_rel = [(f, t - t0) for (f, t) in resultados]
else:
    resultados_rel = resultados  # Si el formato es inesperado, dejar igual

print("Frecuencia (Hz), Delta t (s) respecto a la primera muestra:")
for freq, dt in resultados_rel:
    print(f"{freq:.6f}, {dt:.6f}")

"""
         Ilustración simplificada (puedes imaginar así):

Tiempo (s) ───────────────────────────────────────────────►

|<    intervalo_s >|<    intervalo_s  >| ...
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Muestra 1     │ │   Muestra 2     │ │   Muestra 3     │
│ (cuenta pulsos) │ │ (cuenta pulsos) │ │ (cuenta pulsos) │
└─────────────────┘ └─────────────────┘ └─────────────────┘
     ▲ t1                   ▲ t2                   ▲ t3
   (frecuencia1)         (frecuencia2)         (frecuencia3)

Cada bloque es una ventana de observación.

En cada ventana se cuenta el número de ciclos entrantes y se calcula frecuencia.

El timestamp registrado es el final de la ventana.

✅ Conclusión física
El CNT-91:


Abre una ventana de tiempo fija (definida por SENS:ACQ:APER) para observar pasivamente la señal de entrada.

Cuenta los ciclos/pulsos completos dentro de cada ventana.

Calcula frecuencia y registra el instante temporal.

Este proceso se repite automáticamente n_muestras veces durante el tiempo total de medición.
        
        
        
        
        
        
"""