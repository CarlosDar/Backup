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

# Ejecutar la medición con la nueva función V2
frecuencias, timestamps, delta_tiempos = objt_prueba.medir_n_muestras_equidistantesV2(n_muestras=n_muestras, intervalo_s=intervalo_s)

# Mostrar los resultados en el formato solicitado
print("\nResultados de la medición:")
for i in range(len(frecuencias)):
    print(f"Muestra {i+1}: {frecuencias[i]:.6f} Hz, {timestamps[i]:.6f} s, {delta_tiempos[i]:.6f} s") 